from typing import Optional

from architecture_simulator.uarch.riscv.riscv_architectural_state import (
    RiscvArchitecturalState,
)
from architecture_simulator.isa.riscv.riscv_parser import RiscvParser
from .simulation import Simulation


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
        """Execute the next instruction."""
        if not self.state.pipeline.is_done():
            self.state.pipeline.step()
        return not self.state.pipeline.is_done()

    def run(self):
        """run the current simulation until no more instructions are left (pc stepped over last instruction)"""
        self.state.performance_metrics.resume_timer()
        if self.state.instruction_memory.instructions:
            while not self.state.pipeline.is_done():
                self.step()
        self.state.performance_metrics.stop_timer()

    def load_program(self, program: str):
        """Loads a text format program into the simulation.

        Args:
            program (str): A program which complies with (a subset of) the toy syntax.
        """
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
