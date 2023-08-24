from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from architecture_simulator.settings.settings import Settings
from architecture_simulator.uarch.riscv.riscv_architectural_state import (
    RiscvArchitecturalState,
)
from architecture_simulator.isa.riscv.riscv_parser import RiscvParser
from .simulation import Simulation

if TYPE_CHECKING:
    from architecture_simulator.uarch.riscv.riscv_performance_metrics import (
        RiscvPerformanceMetrics,
    )


class RiscvSimulation(Simulation):
    """A Simulation for the RISC-V architecture.
    Currently supports single_stage_pipeline and five_stage_pipeline.

    Args:
        mode : "single_stage_pipeline" (=default) | "five_stage_pipeline"
    """

    def __init__(
        self,
        state: Optional[RiscvArchitecturalState] = None,
        mode: str = Settings().get()["default_pipeline_mode"],
        detect_data_hazards: bool = Settings().get()["hazard_detection"],
    ) -> None:
        """Constructor for RISC-V simulations.

        Args:
            state (Optional[ArchitecturalState], optional): The state to use. Creates a sensible default.
            mode (str, optional): Can be one of "single_stage_pipeline" (default) or "five_stage_pipeline".
            detect_data_hazards (bool, optional): Turn data hazard detection on or off. Defaults to True.
        """
        self.state = (
            RiscvArchitecturalState(
                pipeline_mode=mode, detect_data_hazards=detect_data_hazards
            )
            if state is None
            else state
        )
        self.mode = mode

    def step(self) -> bool:
        if not self.is_done():
            self.state.pipeline.step()
        return not self.is_done()

    def run(self):
        self.state.performance_metrics.resume_timer()
        while not self.state.pipeline.is_done():
            self.step()
        self.state.performance_metrics.stop_timer()

    def load_program(self, program: str):
        """Loads a text form program into the simulation.

        Args:
            program (str): A program which complies with (a subset of) the RISC-V syntax.
        """
        parser = RiscvParser()
        parser.parse(program=program, state=self.state)

    def is_done(self):
        return self.state.pipeline.is_done()

    def has_instructions(self) -> bool:
        return bool(self.state.instruction_memory)

    def get_performance_metrics(self) -> RiscvPerformanceMetrics:
        return self.state.performance_metrics
