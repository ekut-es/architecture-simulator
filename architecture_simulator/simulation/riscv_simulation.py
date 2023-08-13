from typing import Optional

from architecture_simulator.uarch.riscv.riscv_architectural_state import (
    RiscvArchitecturalState,
)
from architecture_simulator.uarch.riscv.pipeline import Pipeline
from architecture_simulator.uarch.riscv.stages import (
    SingleStage,
    InstructionFetchStage,
    InstructionDecodeStage,
    ExecuteStage,
    MemoryAccessStage,
    RegisterWritebackStage,
)
from architecture_simulator.isa.riscv.riscv_parser import RiscvParser


class RiscvSimulation:
    """A Simulation for the RISC-V architecture.
    Currently supports single_stage_pipeline and five_stage_pipeline.

    Args:
        mode : "single_stage_pipeline" (=default) | "five_stage_pipeline"
    """

    def __init__(
        self,
        state: Optional[RiscvArchitecturalState] = None,
        mode: str = "single_stage_pipeline",
        detect_data_hazards: bool = True,
    ) -> None:
        """Constructor for RISC-V simulations.

        Args:
            state (Optional[ArchitecturalState], optional): The state to use. Creates a sensible default.
            mode (str, optional): Can be one of "single_stage_pipeline" (default) or "five_stage_pipeline".
            detect_data_hazards (bool, optional): Turn data hazard detection on or off. Defaults to True.
        """
        self.state = RiscvArchitecturalState() if state is None else state
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
        """Execute the next instruction."""
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
        """Loads a text form program into the simulation.

        Args:
            program (str): A program which complies with (a subset of) the RISC-V syntax.
        """
        parser = RiscvParser()
        parser.parse(program=program, state=self.state)
