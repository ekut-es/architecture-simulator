from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass, field

from ..isa.instruction_types import EmptyInstruction, BTypeInstruction
from ..isa.rv32i_instructions import JAL
from .control_unit_signals import ControlUnitSignals

if TYPE_CHECKING:
    from ..isa.instruction_types import Instruction
    from architecture_simulator.uarch.architectural_state import ArchitecturalState


@dataclass
class FlushSignal:
    """A signal that all previous pipeline registers should be flushed and that the program counter should be set back"""

    # whether the pipeline register that holds this signal should be flushed too or not
    inclusive: bool
    # address to return to
    address: int


@dataclass
class PipelineRegister:
    """The PipelineRegister superclass!
    Every PipelineRegister needs to save the instruction that is currently in this part of the pipeline!
    """

    instruction: Instruction = field(default_factory=EmptyInstruction)
    address_of_instruction: Optional[int] = None
    flush_signal: Optional[FlushSignal] = None


@dataclass
class InstructionFetchPipelineRegister(PipelineRegister):
    branch_prediction: Optional[bool] = None
    pc_plus_instruction_length: Optional[int] = None


@dataclass
class InstructionDecodePipelineRegister(PipelineRegister):
    control_unit_signals: ControlUnitSignals = field(default_factory=ControlUnitSignals)
    register_read_addr_1: Optional[int] = None
    register_read_addr_2: Optional[int] = None
    register_read_data_1: Optional[int] = None
    register_read_data_2: Optional[int] = None
    imm: Optional[int] = None
    write_register: Optional[int] = None
    branch_prediction: Optional[bool] = None
    pc_plus_instruction_length: Optional[int] = None


@dataclass
class ExecutePipelineRegister(PipelineRegister):
    control_unit_signals: ControlUnitSignals = field(default_factory=ControlUnitSignals)
    alu_in_1: Optional[int] = None
    alu_in_2: Optional[int] = None
    # alu_in_2 is one of read_data_2 and imm
    register_read_data_2: Optional[int] = None
    imm: Optional[int] = None
    result: Optional[int] = None
    write_register: Optional[int] = None
    # control signals
    comparison: Optional[bool] = None
    pc_plus_imm: Optional[int] = None
    branch_prediction: Optional[bool] = None
    pc_plus_instruction_length: Optional[int] = None


@dataclass
class MemoryAccessPipelineRegister(PipelineRegister):
    control_unit_signals: ControlUnitSignals = field(default_factory=ControlUnitSignals)
    memory_address: Optional[int] = None
    result: Optional[int] = None
    memory_write_data: Optional[int] = None
    memory_read_data: Optional[int] = None
    write_register: Optional[int] = None
    # control signals
    comparison: Optional[bool] = None
    comparison_or_jump: Optional[bool] = None
    pc_plus_imm: Optional[int] = None
    pc_plus_instruction_length: Optional[int] = None
    imm: Optional[int] = None


@dataclass
class RegisterWritebackPipelineRegister(PipelineRegister):
    control_unit_signals: ControlUnitSignals = field(default_factory=ControlUnitSignals)
    register_write_data: Optional[int] = None
    write_register: Optional[int] = None
    memory_read_data: Optional[int] = None
    alu_result: Optional[int] = None
    pc_plus_instruction_length: Optional[int] = None
    imm: Optional[int] = None


# Stage superclass, every stage need to implement a behaviour method
class Stage:
    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: ArchitecturalState,
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
    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: ArchitecturalState,
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
        instruction = state.instruction_memory.load_instruction(address_of_instruction)
        state.program_counter += instruction.length
        pc_plus_instruction_length = address_of_instruction + instruction.length

        return InstructionFetchPipelineRegister(
            instruction=instruction,
            address_of_instruction=address_of_instruction,
            branch_prediction=False,
            pc_plus_instruction_length=pc_plus_instruction_length,
        )


class InstructionDecodeStage(Stage):
    def __init__(self, stages_until_writeback=2, detect_data_hazards=True) -> None:
        self.stages_until_writeback = stages_until_writeback
        self.detect_data_hazards = detect_data_hazards
        super().__init__()

    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: ArchitecturalState,
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
        flush_signal = None
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
                    flush_signal = FlushSignal(
                        inclusive=True,
                        address=pipeline_register.address_of_instruction,
                    )
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
            flush_signal=flush_signal,
            pc_plus_instruction_length=pipeline_register.pc_plus_instruction_length,
            address_of_instruction=pipeline_register.address_of_instruction,
        )


class ExecuteStage(Stage):
    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: ArchitecturalState,
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

        return ExecutePipelineRegister(
            instruction=pipeline_register.instruction,
            alu_in_1=alu_in_1,
            alu_in_2=alu_in_2,
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
        )


class MemoryAccessStage(Stage):
    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: ArchitecturalState,
    ) -> PipelineRegister:
        """behavior of MA stage
        Should the pipeline_register not be ExecutePipelineRegister it returns an MemoryAccessPipelineRegister
        with default values

        Args:
            pipeline_register (PipelineRegister): gets ExecutePipelineRegister as argument
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns MemoryAccessPipelineRegister with all necessary information produced or
            used in the MA stage, as well as all controll signals
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
        )


class RegisterWritebackStage(Stage):
    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: ArchitecturalState,
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
        )


#
# Single stage Pipeline:
#
class SingleStage(Stage):
    def behavior(
        self,
        pipeline_registers: list[PipelineRegister],
        index_of_own_input_register: int,
        state: ArchitecturalState,
    ) -> PipelineRegister:
        """behavior of the single stage pipeline

        Args:
            pipeline_register (PipelineRegister): gets any PipelineRegister as argument, but does not use it
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns an PipelineRegister with default values
        """
        if state.instruction_at_pc():
            pc_before_increment = state.program_counter
            instr = state.instruction_memory.load_instruction(state.program_counter)

            state.performance_metrics.instruction_count += 1
            try:
                instr.behavior(state)
                state.program_counter += instr.length
                return PipelineRegister(
                    address_of_instruction=pc_before_increment,
                )
            except Exception as e:
                raise InstructionExecutionException(
                    address=pc_before_increment,
                    instruction_repr=instr.__repr__(),
                    error_message=e.__repr__(),
                )
        return PipelineRegister()


#
# Pipeline wrapper Classs
#


class Pipeline:
    def __init__(
        self,
        stages: list[Stage],
        execution_ordering: list[int],
        state: ArchitecturalState,
    ) -> None:
        """constructor of the pipeline

        Args:
            stages (list[Stage]): the stages the user wants to build the pipeline out of
            execution_ordering (list[int]): the execution ordering of the different stages,
            the list gets iterated over from first to last element, and executes the ith element in the
            stages list!
            state (ArchitecturalState): gets the current architectural state as an argument
        """
        self.stages = stages
        self.num_stages = len(stages)
        self.execution_ordering = execution_ordering
        self.state = state
        self.pipeline_registers: list[PipelineRegister] = [
            PipelineRegister()
        ] * self.num_stages

    def step(self):
        """the pipeline step method, this is the central part of the pipeline! Every time it is called, it does one
        whole step of the pipeline, and every stage gets executed once in their ececution ordering
        """
        self.state.performance_metrics.cycles += 1
        next_pipeline_registers = [None] * self.num_stages
        for index in self.execution_ordering:
            try:
                next_pipeline_registers[index] = self.stages[index].behavior(
                    pipeline_registers=self.pipeline_registers,
                    index_of_own_input_register=(index - 1),
                    state=self.state,
                )
            except Exception as e:
                if index - 1 >= 0:
                    raise InstructionExecutionException(
                        address=self.pipeline_registers[
                            index - 1
                        ].address_of_instruction,
                        instruction_repr=self.pipeline_registers[
                            index - 1
                        ].instruction.__repr__(),
                        error_message=e.__repr__(),
                    )
                else:
                    raise
        self.pipeline_registers = next_pipeline_registers

        # if one of the stages wants to flush, do so (starting from the back makes sense)
        for index, pipeline_register in reversed(
            list(enumerate(self.pipeline_registers))
        ):
            flush_signal = pipeline_register.flush_signal
            if flush_signal is not None:
                self.state.performance_metrics.flushes += 1
                # This works because int(True) = 1, int(False) = 0
                # This is good code, trust me
                num_to_flush = index + flush_signal.inclusive
                self.pipeline_registers[:num_to_flush] = [
                    PipelineRegister()
                ] * num_to_flush
                self.state.program_counter = flush_signal.address
                break  # break since we don't care about the previous stages

    def is_empty(self) -> bool:
        """Return True if all pipeline registers (exluding the last) are empty (determined by whether the instruction in the pipeline register is empty).
            Note, that the last pipeline register is not considerd, because it will not be used as input for an other stage.

        Returns:
            bool: whether all pipeline registers are empty
        """
        return all(
            type(pipeline_register.instruction) == EmptyInstruction
            for pipeline_register in self.pipeline_registers[:-1]
        )

    def is_done(self) -> bool:
        """Return True if the pipeline is empty and there is no instruction at the program counter, so nothing will happen anymore

        Returns:
            bool: if the pipeline has finished
        """
        return self.is_empty() and not self.state.instruction_at_pc()


@dataclass
class InstructionExecutionException(RuntimeError):
    address: int
    instruction_repr: str
    error_message: str

    def __repr__(self):
        return f"There was an error executing the instruction at address '{self.address}': '{self.instruction_repr}':\n{self.error_message}"
