from typing import Optional

from architecture_simulator.uarch.toy.toy_architectural_state import (
    ToyArchitecturalState,
)
from architecture_simulator.isa.toy.toy_parser import ToyParser


class ToySimulation:
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
        """Executes the next instruction and updates the performance metrics accordingly."""
        self.state.performance_metrics.resume_timer()
        self.state.instruction_memory.read_instruction(
            int(self.state.program_counter)
        ).behavior(self.state)
        self.state.performance_metrics.stop_timer()
        self.state.performance_metrics.instruction_count += 1
        self.state.performance_metrics.cycles += 1

    def is_done(self) -> bool:
        """Return whether the simulation is done because there is no instruction at the current program counter.

        Returns:
            bool: whether the simulation is done because there is no instruction at the current program counter.
        """
        return not self.state.instruction_at_pc()

    def run(self):
        """Step through the simulation until it terminates (which it might not if there is an infinite loop in the program)"""
        while not self.is_done():
            self.step()

    def load_program(self, program: str):
        parser = ToyParser()
        instructions = parser.parse(program)
        self.state.instruction_memory.write_instructions(instructions)
