from dataclasses import dataclass

from ..isa.instruction_types import Instruction
from ..isa.parser import riscv_parser
from ..uarch.architectural_state import ArchitecturalState


@dataclass
class Simulation:
    state: ArchitecturalState
    instructions: dict[int, Instruction]

    def append_instructions(self, program: str):
        next_address = len(self.instructions) * 4
        for instr in riscv_parser(program):
            self.instructions[next_address] = instr
            next_address += 4

    def step_simulation(self):
        self.state = self.instructions[self.state.program_counter].behavior(self.state)
        self.state.program_counter += 4
