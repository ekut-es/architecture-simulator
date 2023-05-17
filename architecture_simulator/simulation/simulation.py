from dataclasses import dataclass

from ..isa.instruction_types import Instruction
from ..isa.parser import RiscvParser
from ..uarch.architectural_state import ArchitecturalState


@dataclass
class Simulation:
    state: ArchitecturalState
    instructions: dict[int, Instruction]

    def append_instructions(self, program: str):
        next_address = len(self.instructions) * 4
        parser: RiscvParser = RiscvParser()
        for instr in parser.parse_res_to_instructions(
            parser.parse_assembly(program), start_address=0
        ):
            self.instructions[next_address] = instr
            next_address += 4

    def step_simulation(self):
        self.state = self.instructions[self.state.program_counter].behavior(self.state)
        self.state.program_counter += 4
