from typing import Optional

from architecture_simulator.uarch.architectural_state import ArchitecturalState
from architecture_simulator.uarch.pipeline import Pipeline
from architecture_simulator.uarch.stages import (
    SingleStage,
    InstructionFetchStage,
    InstructionDecodeStage,
    ExecuteStage,
    MemoryAccessStage,
    RegisterWritebackStage,
)
from architecture_simulator.isa.parser import RiscvParser


# Does currently support single_stage_pipeline and five_stage_pipeline
class Simulation:
    """
    Args:
        mode : "single_stage_pipeline" (=default) | "five_stage_pipeline"
    """

    def __init__(
        self,
        state: Optional[ArchitecturalState] = None,
        mode: str = "single_stage_pipeline",
        detect_data_hazards: bool = True,
    ) -> None:
        self.state = ArchitecturalState() if state is None else state
        self.pipeline = (
            Pipeline(
                stages=[
                    InstructionFetchStage(),
                    InstructionDecodeStage(detect_data_hazards=detect_data_hazards),
                    ExecuteStage(),
                    MemoryAccessStage(),
                    RegisterWritebackStage(),
                ],
                execution_ordering=[0, 4, 1, 2, 3],
                state=self.state,
            )
            if mode == "five_stage_pipeline"
            else Pipeline(
                stages=[SingleStage()], execution_ordering=[0], state=self.state
            )
        )
        self.mode = mode

    def step_simulation(self) -> bool:
        if not self.pipeline.is_done():
            self.pipeline.step()
        return not self.pipeline.is_done()

    def run_simulation(self):
        """run the current simulation until no more instructions are left (pc stepped over last instruction)"""
        self.state.performance_metrics.resume_timer()
        if self.state.instruction_memory.instructions:
            while not self.pipeline.is_done():
                self.step_simulation()
        self.state.performance_metrics.stop_timer()

    def load_program(self, program: str):
        parser = RiscvParser()
        # Required to compute labels TODO: Actually, I think this is not needed, because instructions always use relative addresses for jumping.
        # The parser should get slightly reworked.
        start_address = self.state.instruction_memory.address_range.start
        self.state.instruction_memory.write_instructions(
            parser.parse(
                program=program,
                start_address=start_address,
            )
        )
