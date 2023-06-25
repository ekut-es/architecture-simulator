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
    alu_src: Optional[bool] = None
    mem_to_reg: Optional[bool] = None
    reg_write: Optional[bool] = None
    mem_read: Optional[bool] = None
    mem_write: Optional[bool] = None
    branch: Optional[bool] = None
    jump: Optional[bool] = None
    alu_op: Optional[int] = None


@dataclass
class StageData:
    instruction: Instruction = field(default_factory=EmptyInstruction)


@dataclass
class InstructionFetchStageData(StageData):
    pass


@dataclass
class InstructionDecodeStageData(StageData):
    control_unit_signals: ControlUnitSignals = field(default_factory=ControlUnitSignals)
    read_addr_1: Optional[int] = None
    read_addr_2: Optional[int] = None
    read_data_1: Optional[int] = None
    read_data_2: Optional[int] = None
    imm: Optional[int] = None
    write_register: Optional[int] = None


@dataclass
class ExecuteStageData(StageData):
    control_unit_signals: ControlUnitSignals = field(default_factory=ControlUnitSignals)
    alu_in_1: Optional[int] = None
    alu_in_2: Optional[int] = None
    # alu_in_2 is one of read_data_2 and imm
    read_data_2: Optional[int] = None
    imm: Optional[int] = None
    result: Optional[int] = None
    write_register: Optional[int] = None
    # control signals
    zero: Optional[bool] = None


@dataclass
class MemoryAccessStageData(StageData):
    control_unit_signals: ControlUnitSignals = field(default_factory=ControlUnitSignals)
    address: Optional[int] = None
    result: Optional[int] = None
    write_data: Optional[int] = None
    read_data: Optional[int] = None
    write_register: Optional[int] = None
    # control signals
    zero: Optional[bool] = None
    zero_and_branch: Optional[bool] = None
    pc_src: Optional[bool] = None


@dataclass
class RegisterWritebackStageData(StageData):
    control_unit_signals: ControlUnitSignals = field(default_factory=ControlUnitSignals)
    write_data: Optional[int] = None
    write_register: Optional[int] = None
    read_data: Optional[int] = None
    alu_result: Optional[int] = None


class Stage:
    def behavior(
        self,
        data: StageData,
        state: ArchitecturalState,
    ) -> StageData:
        return StageData()


class InstructionFetchStage(Stage):
    def behavior(
        self,
        data: StageData,
        state: ArchitecturalState,
    ) -> StageData:
        return InstructionFetchStageData(
            instruction=state.instruction_memory.load_instruction(state.program_counter)
            if state.instruction_at_pc()
            else EmptyInstruction()
        )


class InstructionDecodeStage(Stage):
    def behavior(self, data: StageData, state: ArchitecturalState) -> StageData:
        if isinstance(data, InstructionFetchStageData):
            (
                read_addr_1,
                read_addr_2,
                read_data_1,
                read_data_2,
                imm,
            ) = data.instruction.access_register_file(architectural_state=state)
            write_register = data.instruction.get_write_register()

            control_unit_signals = data.instruction.control_unit_signals()
            return InstructionDecodeStageData(
                instruction=data.instruction,
                read_addr_1=read_addr_1,
                read_addr_2=read_addr_2,
                read_data_1=read_data_1,
                read_data_2=read_data_2,
                imm=imm,
                write_register=write_register,
                control_unit_signals=control_unit_signals,
            )
        else:
            return InstructionDecodeStageData()


class ExecuteStage(Stage):
    def behavior(self, data: StageData, state: ArchitecturalState) -> StageData:
        if isinstance(data, InstructionDecodeStageData):
            alu_in_1 = data.read_data_1
            alu_in_2 = (
                data.imm if data.control_unit_signals.alu_src else data.read_data_2
            )
            zero, result = data.instruction.alu_compute(
                alu_in_1=alu_in_1, alu_in_2=alu_in_2
            )
            return ExecuteStageData(
                instruction=data.instruction,
                alu_in_1=alu_in_1,
                alu_in_2=alu_in_2,
                read_data_2=data.read_data_2,
                imm=data.imm,
                result=result,
                zero=zero,
                write_register=data.write_register,
                control_unit_signals=data.control_unit_signals,
            )
        else:
            return ExecuteStageData()


class MemoryAccessStage(Stage):
    def behavior(self, data: StageData, state: ArchitecturalState) -> StageData:
        if isinstance(data, ExecuteStageData):
            address = data.result
            write_data = data.read_data_2
            read_data = data.instruction.memory_access(
                address=address, write_data=write_data, architectural_state=state
            )
            zero_and_branch = data.zero and data.control_unit_signals.branch
            pc_src = data.control_unit_signals.jump or zero_and_branch
            if pc_src:
                assert data.imm is not None
                state.program_counter += data.imm
            else:
                # FIXME: Do not use fixed length for the instruction length
                state.program_counter += 4
            return MemoryAccessStageData(
                instruction=data.instruction,
                address=address,
                result=data.result,
                write_data=write_data,
                read_data=read_data,
                zero=data.zero,
                zero_and_branch=zero_and_branch,
                pc_src=pc_src,
                write_register=data.write_register,
                control_unit_signals=data.control_unit_signals,
            )
        else:
            # FIXME: Do not use fixed length for the instruction length
            state.program_counter += 4
            return MemoryAccessStageData()


class RegisterWritebackStage(Stage):
    def behavior(self, data: StageData, state: ArchitecturalState) -> StageData:
        if isinstance(data, MemoryAccessStageData):
            write_data = (
                data.read_data if data.control_unit_signals.mem_to_reg else data.result
            )
            data.instruction.write_back(
                write_register=data.write_register,
                write_data=write_data,
                architectural_state=state,
            )
            return RegisterWritebackStageData(
                instruction=data.instruction,
                write_data=write_data,
                write_register=data.write_register,
                read_data=data.read_data,
                alu_result=data.result,
                control_unit_signals=data.control_unit_signals,
            )
        else:
            return RegisterWritebackStageData()


#
# Single stage Pipeline:
#
class SingleStage(Stage):
    def behavior(self, data: StageData, state: ArchitecturalState) -> StageData:
        if state.instruction_at_pc():
            instr = state.instruction_memory.load_instruction(state.program_counter)
            state.program_counter += instr.length
            instr.behavior(state)
        return StageData()


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
        self.stages = stages
        self.num_stages = len(stages)
        self.execution_ordering = execution_ordering
        self.state = state
        self.stage_data: list[StageData] = [
            StageData(instruction=EmptyInstruction())
        ] * self.num_stages

    def step(self):
        next_stage_data = [None] * self.num_stages
        for index in self.execution_ordering:
            # first stage in pipeline does not consume any StageData
            if index == 0:
                next_stage_data[0] = self.stages[0].behavior(
                    data=StageData(instruction=EmptyInstruction()), state=self.state
                )
            # last stage in pipeline comsumes StageData, but the StageData it returns is not used
            elif index == self.num_stages - 1:
                self.stages[index].behavior(
                    data=self.stage_data[index - 1], state=self.state
                )
            # all other pipeline stages consume StageData and return StageData
            else:
                next_stage_data[index] = self.stages[index].behavior(
                    data=self.stage_data[index - 1], state=self.state
                )
        self.stage_data = next_stage_data

    def stall(self):
        ...

    def flush(self):
        ...
