from .architectural_state import ArchitecturalState
from ..isa.instruction_types import Instruction, EmptyInstruction

from dataclasses import dataclass


@dataclass
class StageData:
    instruction: Instruction
    ...


class Stage:
    def behavior(self, data: StageData, state: ArchitecturalState) -> StageData:
        return StageData(instruction=EmptyInstruction())


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
