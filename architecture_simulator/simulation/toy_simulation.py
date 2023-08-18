from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from architecture_simulator.uarch.toy.toy_architectural_state import (
    ToyArchitecturalState,
)
from architecture_simulator.isa.toy.toy_parser import ToyParser
from .simulation import Simulation

if TYPE_CHECKING:
    from architecture_simulator.uarch.toy.toy_performance_metrics import (
        ToyPerformanceMetrics,
    )


class ToySimulation(Simulation):
    def __init__(
        self,
        instruction_memory_range: Optional[range] = None,
        data_memory_range: Optional[range] = None,
    ):
        self.state = ToyArchitecturalState(
            instruction_memory_range=instruction_memory_range,
            data_memory_range=data_memory_range,
        )

    def step(self):
        if not self.is_done():
            self.state.instruction_memory.read_instruction(
                int(self.state.program_counter)
            ).behavior(self.state)
            self.state.performance_metrics.instruction_count += 1
        return not self.is_done()

    def is_done(self) -> bool:
        return not self.state.instruction_at_pc()

    def run(self):
        self.state.performance_metrics.resume_timer()
        while not self.is_done():
            self.step()
        self.state.performance_metrics.stop_timer()

    def load_program(self, program: str):
        self.state = ToyArchitecturalState(
            instruction_memory_range=self.state.instruction_memory.address_range,
            data_memory_range=self.state.data_memory.address_range,
        )
        parser = ToyParser()
        parser.parse(program=program, state=self.state)

    def has_instructions(self) -> bool:
        return bool(self.state.instruction_memory)

    def get_performance_metrics(self) -> ToyPerformanceMetrics:
        return self.state.performance_metrics
