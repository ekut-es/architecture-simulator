from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from architecture_simulator.uarch.riscv.riscv_architectural_state import (
    RiscvArchitecturalState,
)
from architecture_simulator.isa.riscv.riscv_parser import RiscvParser
from .simulation import Simulation

if TYPE_CHECKING:
    from architecture_simulator.uarch.performance_metrics import PerformanceMetrics


class RiscvSimulation(Simulation):
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
        self.state = (
            RiscvArchitecturalState(
                pipeline_mode=mode, detect_data_hazards=detect_data_hazards
            )
            if state is None
            else state
        )

    def step(self) -> bool:
        self.state.pipeline.step()
        return not self.is_done()

    def run(self):
        self.state.performance_metrics.resume_timer()
        while not self.state.pipeline.is_done():
            self.step()
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

    def is_done(self):
        return self.state.pipeline.is_done()

    def has_instructions(self) -> bool:
        return bool(self.state.instruction_memory)

    def get_performance_metrics_str(self) -> str:
        return str(self.state.performance_metrics)

    def get_performance_metrics(self) -> PerformanceMetrics:
        return self.state.performance_metrics
