from architecture_simulator.uarch.architectural_state import ArchitecturalState
from .architectural_state import ArchitecturalState
from ..isa.instruction_types import Instruction, EmptyInstruction
from typing import Optional
from dataclasses import dataclass


@dataclass
class StageData:
    instruction: Instruction


@dataclass
class InstructionFetchStageData(StageData):
    pass


@dataclass
class InstructionDecodeStageData(StageData):
    read_addr_1: Optional[int] = None
    read_addr_2: Optional[int] = None
    read_data_1: Optional[int] = None
    read_data_2: Optional[int] = None
    imm: Optional[int] = None
    # control signals
    jump: Optional[bool] = None
    alu_op: Optional[int] = None
    branch: Optional[bool] = None
    mem_to_reg: Optional[bool] = None
    mem_read: Optional[bool] = None
    mem_write: Optional[bool] = None
    alu_src: Optional[bool] = None
    reg_write: Optional[bool] = None


@dataclass
class ExecuteStageData(StageData):
    alu_in_1: Optional[int] = None
    alu_in_2: Optional[int] = None
    # alu_in_2 is one of read_data_2 and imm
    read_data_2: Optional[int] = None
    imm: Optional[int] = None
    result: Optional[int] = None
    # control signals
    jump: Optional[bool] = None
    alu_op: Optional[int] = None
    branch: Optional[bool] = None
    mem_to_reg: Optional[bool] = None
    mem_read: Optional[bool] = None
    mem_write: Optional[bool] = None
    alu_src: Optional[bool] = None
    zero: Optional[bool] = None


class Stage:
    def behavior(self, state: ArchitecturalState, *args, **kwargs) -> StageData:
        return StageData(instruction=EmptyInstruction())


class InstructionFetchStage(Stage):
    def behavior(
        self,
        state: ArchitecturalState,
        data: InstructionFetchStageData,
        *args,
        **kwargs,
    ) -> StageData:
        return InstructionFetchStageData(
            instruction=state.instruction_memory.load_instruction(state.program_counter)
        )


class InstructionDecodeStage(Stage):
    def behavior(
        self, data: InstructionFetchStageData, state: ArchitecturalState
    ) -> StageData:
        (
            read_addr_1,
            read_addr_2,
            read_data_1,
            read_data_2,
            imm,
        ) = data.instruction.access_register_file(state)

        (
            jump,
            alu_op,
            branch,
            mem_to_reg,
            mem_read,
            mem_write,
            alu_src,
            reg_write,
        ) = data.instruction.control_unit_signals()
        return InstructionDecodeStageData(
            instruction=data.instruction,
            read_addr_1=read_addr_1,
            read_addr_2=read_addr_2,
            read_data_1=read_data_1,
            read_data_2=read_data_2,
            imm=imm,
            jump=jump,
            alu_op=alu_op,
            branch=branch,
            mem_to_reg=mem_to_reg,
            mem_read=mem_read,
            mem_write=mem_write,
            alu_src=alu_src,
            reg_write=reg_write,
        )


class ExecuteStage(Stage):
    def behavior(
        self, data: InstructionDecodeStageData, state: ArchitecturalState
    ) -> StageData:
        alu_in_1 = data.read_data_1
        alu_in_2 = data.imm if data.alu_src else data.read_data_2
        zero, result = data.instruction.alu_compute(alu_in_1, alu_in_2)
        return super().behavior(data, state)


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

    stage_data: list[StageData]

    def step(self):
        next_stage_data = ["None"] * self.num_stages
        for index in self.execution_ordering:
            # first stage in pipeline does not consume any StageData
            if index == 0:
                next_stage_data[1] = self.stages[0].behavior(data=StageData())
            # last stage in pipeline comsumes StageData, but the StageData it returns is not used
            elif index == self.num_stages - 1:
                self.stages[index].behavior(data=self.stage_data[index])
            # all other pipeline stages consume StageData and return StageData
            else:
                next_stage_data[index + 1] = self.stages[index].behavior(
                    data=self.stage_data[index]
                )
        self.stage_data = next_stage_data

    def stall(self):
        ...

    def flush(self):
        ...
