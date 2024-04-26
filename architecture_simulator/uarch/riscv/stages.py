from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .pipeline_registers import (
    PipelineRegister,
    InstructionFetchPipelineRegister,
    InstructionDecodePipelineRegister,
    ExecutePipelineRegister,
    MemoryAccessPipelineRegister,
    RegisterWritebackPipelineRegister,
    SingleStagePipelineRegister,
)

from architecture_simulator.isa.riscv.instruction_types import (
    BTypeInstruction,
    EmptyInstruction,
)
from architecture_simulator.isa.riscv.rv32i_instructions import (
    JAL,
    SB,
    SH,
    SW,
    LB,
    LBU,
    LH,
    LHU,
    LW,
    CSRRW,
    CSRRS,
    CSRRC,
    CSRRWI,
    CSRRSI,
    CSRRCI,
    ECALL,
    EBREAK,
    FENCE,
)
from .pipeline import InstructionExecutionException

if TYPE_CHECKING:
    from architecture_simulator.uarch.riscv.riscv_architectural_state import (
        RiscvArchitecturalState,
    )

from collections import defaultdict


class Stage:
    """Stage superclass. Every stage needs to implement a behavior method"""

    # An abbreviation for the stage. May be used as display name.
    abbreviation: str

    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: RiscvArchitecturalState,
    ) -> PipelineRegister:
        """general behavior method

        Args:
            pipeline_register (PipelineRegister): gets the data from the stage before as argument
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns data of this stage
        """
        return PipelineRegister()


class InstructionFetchStage(Stage):
    abbreviation = "IF"

    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: RiscvArchitecturalState,
    ) -> PipelineRegister:
        """behavior of the IF Stage
        The input pipeline_register can be of any type of PipelineRegister

        Args:
            pipeline_register (PipelineRegister): gets a PipelineRegister as argument, but does not use it
            (it only gets this to be consistent with the superclass)
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns the InstructionFetchPipelineRegister class with all information from the
            IF stage
        """
        if not state.instruction_at_pc():
            return InstructionFetchPipelineRegister()
        # NOTE: PC gets incremented here. This means that branch prediction also happens here. Currently, we just statically predict not taken.
        address_of_instruction = state.program_counter
        instruction = state.instruction_memory.read_instruction(address_of_instruction)
        state.program_counter += instruction.length
        pc_plus_instruction_length = address_of_instruction + instruction.length

        return InstructionFetchPipelineRegister(
            instruction=instruction,
            address_of_instruction=address_of_instruction,
            branch_prediction=False,
            pc_plus_instruction_length=pc_plus_instruction_length,
        )


class InstructionDecodeStage(Stage):
    abbreviation = "ID"

    def __init__(self, stages_until_writeback=2, detect_data_hazards=True) -> None:
        self.stages_until_writeback = stages_until_writeback
        self.detect_data_hazards = detect_data_hazards
        super().__init__()

    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: RiscvArchitecturalState,
    ) -> PipelineRegister:
        """behavior of the ID Stage
        Should the pipeline_register not be InstructionFetchPipelineRegister it returns an
        InstructionDecodePipelineRegister with default values

        Args:
            pipeline_register (PipelineRegister): gets the InstructionFetchPipelineRegister as argument
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns InstructionDecodePipelineRegister with all information from
            the ID stage and all results of computations done in this step, as well as all controll signals
        """
        pipeline_register = pipeline_registers[index_of_own_input_register]

        if not isinstance(pipeline_register, InstructionFetchPipelineRegister):
            return InstructionDecodePipelineRegister()

        # uses the access_register_file method of the instruction saved in the InstructionFetchPipelineRegister
        # to get the data from the register files
        (
            register_read_addr_1,
            register_read_addr_2,
            register_read_data_1,
            register_read_data_2,
            imm,
        ) = pipeline_register.instruction.access_register_file(
            architectural_state=state
        )
        # gets the write register, used in the WB stage to find the register to write data to
        write_register = pipeline_register.instruction.get_write_register()

        # Data Hazard Detection
        stall_signal = None
        if self.detect_data_hazards:
            # Put all the write registers of later stages, that are not done ahead of this stage into a list
            write_registers_of_later_stages = [
                pipeline_registers[
                    index_of_own_input_register + i + 1
                ].instruction.get_write_register()
                for i in range(self.stages_until_writeback)
            ]
            # Check if there is a data hazard
            for register in write_registers_of_later_stages:
                if register is None or register == 0:
                    continue
                if register_read_addr_1 == register or register_read_addr_2 == register:
                    assert pipeline_register.address_of_instruction is not None
                    stall_signal = StallSignal(2)
                    break

        # gets the control unit signals that are generated in the ID stage
        control_unit_signals = pipeline_register.instruction.control_unit_signals()
        return InstructionDecodePipelineRegister(
            instruction=pipeline_register.instruction,
            register_read_addr_1=register_read_addr_1,
            register_read_addr_2=register_read_addr_2,
            register_read_data_1=register_read_data_1,
            register_read_data_2=register_read_data_2,
            imm=imm,
            write_register=write_register,
            control_unit_signals=control_unit_signals,
            branch_prediction=pipeline_register.branch_prediction,
            stall_signal=stall_signal,
            pc_plus_instruction_length=pipeline_register.pc_plus_instruction_length,
            address_of_instruction=pipeline_register.address_of_instruction,
        )


class ExecuteStage(Stage):
    abbreviation = "EX"

    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: RiscvArchitecturalState,
    ) -> PipelineRegister:
        """behavior of the EX stage
        Should the pipeline_register not be InstructionDecodePipelineRegister it returns an
        ExecutePipelineRegister with default values

        Args:
            pipeline_register (PipelineRegister): gets InstructionDecodePipelineRegister as argument
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns the ExecutePipelineRegister with all necessary information produced or
            used in the EX stage, as well as all controll signals
        """
        pipeline_register = pipeline_registers[index_of_own_input_register]

        if not isinstance(pipeline_register, InstructionDecodePipelineRegister):
            return ExecutePipelineRegister()

        alu_in_1 = (
            pipeline_register.register_read_data_1
            if pipeline_register.control_unit_signals.alu_src_1
            else pipeline_register.address_of_instruction
        )
        alu_in_2 = (
            pipeline_register.imm
            if pipeline_register.control_unit_signals.alu_src_2
            else pipeline_register.register_read_data_2
        )
        branch_taken, result = pipeline_register.instruction.alu_compute(
            alu_in_1=alu_in_1, alu_in_2=alu_in_2
        )
        pc_plus_imm = (
            pipeline_register.imm + pipeline_register.address_of_instruction
            if pipeline_register.imm is not None
            and pipeline_register.address_of_instruction is not None
            else None
        )

        # ECALL needs some special behavior (flush and print to output)
        stall_signal = None
        exit_code = None
        flush_signal = None  # Needed for exiting the simulation (ecall 10/93)
        if isinstance(pipeline_register.instruction, ECALL):
            # assume that all further stages need to be empty, unless this stage is already stalled and the value of the next register is only for display purposes
            for other_pr in pipeline_registers[
                index_of_own_input_register
                + 1
                + int(pipeline_register.is_of_stalled_value) : -1
            ]:
                if not isinstance(other_pr.instruction, EmptyInstruction):
                    assert pipeline_register.address_of_instruction is not None
                    stall_signal = StallSignal(2)
                    break
            if stall_signal is None:
                ecall_result = pipeline_register.instruction.process_ecall(state)
                if type(ecall_result) is str:
                    state.output += ecall_result
                elif type(ecall_result) is int:
                    exit_code = ecall_result
                    assert pipeline_register.pc_plus_instruction_length is not None
                    flush_signal = FlushSignal(
                        False, pipeline_register.pc_plus_instruction_length
                    )

        return ExecutePipelineRegister(
            stall_signal=stall_signal,
            instruction=pipeline_register.instruction,
            alu_in_1=alu_in_1,
            alu_in_2=alu_in_2,
            register_read_data_1=pipeline_register.register_read_data_1,
            register_read_data_2=pipeline_register.register_read_data_2,
            imm=pipeline_register.imm,
            result=result,
            comparison=branch_taken,
            write_register=pipeline_register.write_register,
            control_unit_signals=pipeline_register.control_unit_signals,
            pc_plus_imm=pc_plus_imm,
            branch_prediction=pipeline_register.branch_prediction,
            pc_plus_instruction_length=pipeline_register.pc_plus_instruction_length,
            address_of_instruction=pipeline_register.address_of_instruction,
            exit_code=exit_code,
            flush_signal=flush_signal,
        )


class MemoryAccessStage(Stage):
    abbreviation = "MA"

    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: RiscvArchitecturalState,
    ) -> PipelineRegister:
        """behavior of MEM stage
        Should the pipeline_register not be ExecutePipelineRegister it returns an MemoryAccessPipelineRegister
        with default values

        Args:
            pipeline_register (PipelineRegister): gets ExecutePipelineRegister as argument
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns MemoryAccessPipelineRegister with all necessary information produced or
            used in the MEM stage, as well as all controll signals
        """
        pipeline_register = pipeline_registers[index_of_own_input_register]

        if not isinstance(pipeline_register, ExecutePipelineRegister):
            return MemoryAccessPipelineRegister()

        memory_address = pipeline_register.result
        memory_write_data = pipeline_register.register_read_data_2
        memory_read_data = pipeline_register.instruction.memory_access(
            memory_address=memory_address,
            memory_write_data=memory_write_data,
            architectural_state=state,
        )
        comparison_or_jump = (
            pipeline_register.control_unit_signals.jump or pipeline_register.comparison
        )

        # NOTE: comparison_or_jump = 0 -> select (pc+i_length), comparison_or_jump = 1 -> select (pc+imm)
        incorrect_branch_prediction = (
            pipeline_register.control_unit_signals.branch
            and comparison_or_jump != pipeline_register.branch_prediction
        )

        if incorrect_branch_prediction or pipeline_register.control_unit_signals.jump:
            # flush if (pc+imm) should have been written to the pc
            assert pipeline_register.pc_plus_imm is not None
            flush_signal = FlushSignal(
                inclusive=False, address=pipeline_register.pc_plus_imm
            )
        elif pipeline_register.control_unit_signals.alu_to_pc:
            # flush if result should have been written to pc
            assert pipeline_register.result is not None
            flush_signal = FlushSignal(
                inclusive=False, address=pipeline_register.result
            )
        elif pipeline_register.exit_code is not None:
            # Exit codes stem from ecalls which cannot cause branches and thus cannot generate other flush signals
            assert pipeline_register.pc_plus_instruction_length is not None
            flush_signal = FlushSignal(
                False, pipeline_register.pc_plus_instruction_length
            )
        else:
            flush_signal = None

        if flush_signal is not None:
            if isinstance(pipeline_register.instruction, BTypeInstruction):
                state.performance_metrics.branch_count += 1
            elif isinstance(pipeline_register.instruction, JAL):
                state.performance_metrics.procedure_count += 1

        return MemoryAccessPipelineRegister(
            instruction=pipeline_register.instruction,
            memory_address=memory_address,
            result=pipeline_register.result,
            memory_write_data=memory_write_data,
            memory_read_data=memory_read_data,
            comparison=pipeline_register.comparison,
            comparison_or_jump=comparison_or_jump,
            write_register=pipeline_register.write_register,
            control_unit_signals=pipeline_register.control_unit_signals,
            pc_plus_imm=pipeline_register.pc_plus_imm,
            flush_signal=flush_signal,
            pc_plus_instruction_length=pipeline_register.pc_plus_instruction_length,
            imm=pipeline_register.imm,
            address_of_instruction=pipeline_register.address_of_instruction,
            exit_code=pipeline_register.exit_code,
        )


class RegisterWritebackStage(Stage):
    abbreviation = "WB"

    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: RiscvArchitecturalState,
    ) -> PipelineRegister:
        """behavior of WB stage
        Should the pipeline_register not be MemoryAccessPipelineRegister it returns an
        RegisterWritebackPipelineRegister with default values

        Args:
            pipeline_register (PipelineRegister): gets MemoryAccessPipelineRegister as argument
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns RegisterWritebackPipelineRegister with all necessary information produced or
            used in the WB stage, as well as all controll signals.
            Note: this information is not taken as an input by any other stage, because the WB stage is
            the last stage!
        """
        pipeline_register = pipeline_registers[index_of_own_input_register]

        if not isinstance(pipeline_register, MemoryAccessPipelineRegister):
            return RegisterWritebackPipelineRegister()

        if not isinstance(pipeline_register.instruction, EmptyInstruction):
            state.performance_metrics.instruction_count += 1

        # select the correct data for write back
        wb_src = pipeline_register.control_unit_signals.wb_src
        if wb_src == 0:
            register_write_data = pipeline_register.pc_plus_instruction_length
        elif wb_src == 1:
            register_write_data = pipeline_register.memory_read_data
        elif wb_src == 2:
            register_write_data = pipeline_register.result
        elif wb_src == 3:
            register_write_data = pipeline_register.imm
        else:
            register_write_data = None

        pipeline_register.instruction.write_back(
            write_register=pipeline_register.write_register,
            register_write_data=register_write_data,
            architectural_state=state,
        )

        flush_signal = None
        if pipeline_register.exit_code is not None:
            assert pipeline_register.pc_plus_instruction_length is not None
            flush_signal = FlushSignal(
                False, pipeline_register.pc_plus_instruction_length
            )
            state.exit_code = pipeline_register.exit_code

        return RegisterWritebackPipelineRegister(
            instruction=pipeline_register.instruction,
            register_write_data=register_write_data,
            write_register=pipeline_register.write_register,
            memory_read_data=pipeline_register.memory_read_data,
            alu_result=pipeline_register.result,
            control_unit_signals=pipeline_register.control_unit_signals,
            pc_plus_instruction_length=pipeline_register.pc_plus_instruction_length,
            imm=pipeline_register.imm,
            address_of_instruction=pipeline_register.address_of_instruction,
            flush_signal=flush_signal,
        )


#
# Single stage Pipeline:
#
class SingleStage(Stage):
    TYPE_MEMORY_INSTRUCTION = {SB, SH, SW, LB, LBU, LH, LHU, LW}
    TYPE_STORE_INSTRUCTION = {SB, SH, SW}
    TYPE_LOAD_INSTRUCTION = {LB, LBU, LH, LHU, LW}

    TYPE_NO_VISUALISATION_AVIVABLE = {
        CSRRW,
        CSRRS,
        CSRRC,
        CSRRWI,
        CSRRSI,
        CSRRCI,
        EBREAK,
        FENCE,
    }

    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: RiscvArchitecturalState,
    ) -> PipelineRegister:
        """behavior of the single stage pipeline

        Args:
            pipeline_register (PipelineRegister): gets any PipelineRegister as argument, but does not use it
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns a SingleStagePipelineRegister or a default PipelineRegister
        """
        if state.instruction_at_pc():
            state.performance_metrics.instruction_count += 1
            result_pr = SingleStagePipelineRegister()

            result_pr.instruction = state.instruction_memory.read_instruction(
                state.program_counter
            )
            result_pr.address_of_instruction = state.program_counter

            five_stage_control_unit_signals = (
                result_pr.instruction.control_unit_signals()
            )
            result_pr.control_unit_signals.alu_src_1 = (
                None
                if five_stage_control_unit_signals.alu_src_1 is None
                else not five_stage_control_unit_signals.alu_src_1
            )
            result_pr.control_unit_signals.alu_src_2 = (
                five_stage_control_unit_signals.alu_src_2
            )
            result_pr.control_unit_signals.alu_control = (
                five_stage_control_unit_signals.alu_op is not None
            )
            result_pr.control_unit_signals.wb_src_int = (
                five_stage_control_unit_signals.wb_src
            )
            result_pr.control_unit_signals.jump = bool(
                five_stage_control_unit_signals.jump
            )
            result_pr.control_unit_signals.pc_from_alu_res = (
                result_pr.instruction.mnemonic == "jalr"
            )

            (
                result_pr.register_read_addr_1,
                result_pr.register_read_addr_2,
                result_pr.register_read_data_1,
                result_pr.register_read_data_2,
                result_pr.imm,
            ) = result_pr.instruction.access_register_file(state)
            result_pr.register_write_register = (
                result_pr.instruction.get_write_register()
            )

            result_pr.instruction_length = result_pr.instruction.length
            result_pr.pc_plus_instruction_length = (
                state.program_counter + result_pr.instruction_length
            )
            if result_pr.imm is not None and (
                five_stage_control_unit_signals.branch
                or result_pr.control_unit_signals.jump
            ):
                result_pr.pc_plus_imm = state.program_counter + result_pr.imm

            a_comparison, a_result = result_pr.instruction.alu_compute(
                (
                    state.program_counter
                    if result_pr.control_unit_signals.alu_src_1
                    else result_pr.register_read_data_1
                ),
                (
                    result_pr.imm
                    if result_pr.control_unit_signals.alu_src_2
                    else result_pr.register_read_data_2
                ),
            )

            result_pr.alu_comparison = bool(a_comparison)
            result_pr.alu_result = a_result

            result_pr.memory_address = (
                result_pr.alu_result
                if type(result_pr.instruction) in SingleStage.TYPE_MEMORY_INSTRUCTION
                else None
            )

            result_pr.memory_write_data = (
                result_pr.register_read_data_2
                if type(result_pr.instruction) in SingleStage.TYPE_STORE_INSTRUCTION
                else None
            )

            result_pr.register_write_data = defaultdict(
                lambda: None,
                {
                    None: None,  # to stop mypy complaining
                    0: result_pr.pc_plus_instruction_length,
                    1: result_pr.memory_read_data,
                    2: result_pr.alu_result,
                    3: result_pr.imm,
                },
            )[five_stage_control_unit_signals.wb_src]

            try:
                result_pr.instruction.behavior(state)
                result_pr.memory_read_data = (
                    result_pr.instruction.memory_access(
                        result_pr.memory_address, None, state, update_statistics=False
                    )
                    if type(result_pr.instruction) in SingleStage.TYPE_LOAD_INSTRUCTION
                    else None
                )
                state.program_counter += result_pr.instruction.length
                if (
                    not type(result_pr.instruction)
                    in SingleStage.TYPE_NO_VISUALISATION_AVIVABLE
                ):
                    return result_pr
            except Exception as e:
                raise InstructionExecutionException(
                    address=result_pr.address_of_instruction,
                    instruction_repr=result_pr.instruction.__repr__(),
                    error_message=e.__repr__(),
                )
        return PipelineRegister()


@dataclass
class FlushSignal:
    """A signal that all previous pipeline registers should be flushed and that the program counter should be set back"""

    # whether the pipeline register that holds this signal should be flushed too or not
    inclusive: bool
    # address to return to
    address: int


@dataclass
class StallSignal:
    """A signal that this stage and all previous stages should be stalled for a duration of cycles"""

    # how many cycles to stall
    duration: int
