from typing import Optional

from architecture_simulator.uarch.toy.toy_architectural_state import (
    ToyArchitecturalState,
)
from architecture_simulator.isa.toy.toy_parser import ToyParser
from .simulation import Simulation


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
        self.state.instruction_memory.read_instruction(
            int(self.state.program_counter)
        ).behavior(self.state)
        self.state.performance_metrics.instruction_count += 1
        self.state.performance_metrics.cycles += 1
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
