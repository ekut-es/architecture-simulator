from architecture_simulator.uarch.architectural_state import ArchitecturalState
from .architectural_state import ArchitecturalState
from ..isa.instruction_types import Instruction, EmptyInstruction
from typing import Optional
from dataclasses import dataclass, field

#
# Classes for a 5 Stage Pipeline:
#
@dataclass
class ControlUnitSignals:
    """The signals of the control unit, which is located in the ID stage! These signals are used to decide
    which input gets used, but are mostly asthetic and constructed for the webui!
    """

    alu_src: Optional[bool] = None
    mem_to_reg: Optional[bool] = None
    reg_write: Optional[bool] = None
    mem_read: Optional[bool] = None
    mem_write: Optional[bool] = None
    branch: Optional[bool] = None
    jump: Optional[bool] = None
    alu_op: Optional[int] = None


@dataclass
class PipelineRegister:
    """The PipelineRegister superclass!
    Every PipelineRegister needs to save the instruction that is currently in this part of the pipeline!
    """

    instruction: Instruction = field(default_factory=EmptyInstruction)


@dataclass
class InstructionFetchPipelineRegister(PipelineRegister):
    pass


@dataclass
class InstructionDecodePipelineRegister(PipelineRegister):
    control_unit_signals: ControlUnitSignals = field(default_factory=ControlUnitSignals)
    register_read_addr_1: Optional[int] = None
    register_read_addr_2: Optional[int] = None
    register_read_data_1: Optional[int] = None
    register_read_data_2: Optional[int] = None
    imm: Optional[int] = None
    write_register: Optional[int] = None


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
    zero: Optional[bool] = None


@dataclass
class MemoryAccessPipelineRegister(PipelineRegister):
    control_unit_signals: ControlUnitSignals = field(default_factory=ControlUnitSignals)
    memory_address: Optional[int] = None
    result: Optional[int] = None
    memory_write_data: Optional[int] = None
    memory_read_data: Optional[int] = None
    write_register: Optional[int] = None
    # control signals
    zero: Optional[bool] = None
    zero_and_branch: Optional[bool] = None
    pc_src: Optional[bool] = None


@dataclass
class RegisterWritebackPipelineRegister(PipelineRegister):
    control_unit_signals: ControlUnitSignals = field(default_factory=ControlUnitSignals)
    register_write_data: Optional[int] = None
    write_register: Optional[int] = None
    memory_read_data: Optional[int] = None
    alu_result: Optional[int] = None


# Stage superclass, every stage need to implement a behaviour method
class Stage:
    def behavior(
        self,
        pipeline_register: PipelineRegister,
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
        pipeline_register: PipelineRegister,
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
        return InstructionFetchPipelineRegister(
            # loads the instruction at the current program counter
            instruction=state.instruction_memory.load_instruction(state.program_counter)
            if state.instruction_at_pc()
            else EmptyInstruction()
        )


class InstructionDecodeStage(Stage):
    def behavior(
        self, pipeline_register: PipelineRegister, state: ArchitecturalState
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
        if isinstance(pipeline_register, InstructionFetchPipelineRegister):
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
            )
        else:
            return InstructionDecodePipelineRegister()


class ExecuteStage(Stage):
    def behavior(
        self, pipeline_register: PipelineRegister, state: ArchitecturalState
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
        if isinstance(pipeline_register, InstructionDecodePipelineRegister):
            alu_in_1 = pipeline_register.register_read_data_1
            alu_in_2 = (
                pipeline_register.imm
                if pipeline_register.control_unit_signals.alu_src
                else pipeline_register.register_read_data_2
            )
            zero, result = pipeline_register.instruction.alu_compute(
                alu_in_1=alu_in_1, alu_in_2=alu_in_2
            )
            return ExecutePipelineRegister(
                instruction=pipeline_register.instruction,
                alu_in_1=alu_in_1,
                alu_in_2=alu_in_2,
                register_read_data_2=pipeline_register.register_read_data_2,
                imm=pipeline_register.imm,
                result=result,
                zero=zero,
                write_register=pipeline_register.write_register,
                control_unit_signals=pipeline_register.control_unit_signals,
            )
        else:
            return ExecutePipelineRegister()


class MemoryAccessStage(Stage):
    def behavior(
        self, pipeline_register: PipelineRegister, state: ArchitecturalState
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
        if isinstance(pipeline_register, ExecutePipelineRegister):
            memory_address = pipeline_register.result
            memory_write_data = pipeline_register.register_read_data_2
            memory_read_data = pipeline_register.instruction.memory_access(
                memory_address=memory_address,
                memory_write_data=memory_write_data,
                architectural_state=state,
            )
            zero_and_branch = (
                pipeline_register.zero and pipeline_register.control_unit_signals.branch
            )
            pc_src = pipeline_register.control_unit_signals.jump or zero_and_branch
            if pc_src:
                assert pipeline_register.imm is not None
                state.program_counter += pipeline_register.imm
            else:
                # FIXME: Do not use fixed length for the instruction length
                state.program_counter += 4
            return MemoryAccessPipelineRegister(
                instruction=pipeline_register.instruction,
                memory_address=memory_address,
                result=pipeline_register.result,
                memory_write_data=memory_write_data,
                memory_read_data=memory_read_data,
                zero=pipeline_register.zero,
                zero_and_branch=zero_and_branch,
                pc_src=pc_src,
                write_register=pipeline_register.write_register,
                control_unit_signals=pipeline_register.control_unit_signals,
            )
        else:
            # FIXME: Do not use fixed length for the instruction length
            state.program_counter += 4
            return MemoryAccessPipelineRegister()


class RegisterWritebackStage(Stage):
    def behavior(
        self, pipeline_register: PipelineRegister, state: ArchitecturalState
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
        if isinstance(pipeline_register, MemoryAccessPipelineRegister):
            register_write_data = (
                pipeline_register.memory_read_data
                if pipeline_register.control_unit_signals.mem_to_reg
                else pipeline_register.result
            )
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
            )
        else:
            return RegisterWritebackPipelineRegister()


#
# Single stage Pipeline:
#
class SingleStage(Stage):
    def behavior(
        self, pipeline_register: PipelineRegister, state: ArchitecturalState
    ) -> PipelineRegister:
        """behavior of the single stage pipeline

        Args:
            pipeline_register (PipelineRegister): gets any PipelineRegister as argument, but does not use it
            state (ArchitecturalState): gets the current architectural state as argument

        Returns:
            PipelineRegister: returns an PipelineRegister with default values
        """
        if state.instruction_at_pc():
            instr = state.instruction_memory.load_instruction(state.program_counter)
            state.program_counter += instr.length
            instr.behavior(state)
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
        self.pipeline_register: list[PipelineRegister] = [
            PipelineRegister(instruction=EmptyInstruction())
        ] * self.num_stages

    def step(self):
        """the pipeline step method, this is the central part of the pipeline! Every time it is called, it does one
        whole step of the pipeline, and every stage gets executed once in their ececution ordering
        """
        next_pipeline_register = [None] * self.num_stages
        for index in self.execution_ordering:
            # first stage in pipeline does not consume any PipelineRegister
            if index == 0:
                next_pipeline_register[0] = self.stages[0].behavior(
                    pipeline_register=PipelineRegister(instruction=EmptyInstruction()),
                    state=self.state,
                )
            # last stage in pipeline comsumes PipelineRegister, but the PipelineRegister it returns is not used
            elif index == self.num_stages - 1:
                self.stages[index].behavior(
                    pipeline_register=self.pipeline_register[index - 1],
                    state=self.state,
                )
            # all other pipeline stages consume PipelineRegister and return PipelineRegister
            else:
                next_pipeline_register[index] = self.stages[index].behavior(
                    pipeline_register=self.pipeline_register[index - 1],
                    state=self.state,
                )
        self.pipeline_register = next_pipeline_register

    def stall(self):
        ...

    def flush(self):
        ...
