from typing import Optional

from architecture_simulator.uarch.toy.toy_architectural_state import (
    ToyArchitecturalState,
)


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
        """_summary_"""
        self.state.instruction_memory.load_instruction(
            int(self.state.program_counter)
        ).behavior(self.state)

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
