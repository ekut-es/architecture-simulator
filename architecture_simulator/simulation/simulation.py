from ..isa.instruction_types import Instruction
from ..isa.parser import RiscvParser
from ..uarch.architectural_state import ArchitecturalState
from dataclasses import dataclass, field


@dataclass
class Simulation:
    state: ArchitecturalState = field(default_factory=ArchitecturalState)
    instructions: dict[int, Instruction] = field(default_factory=dict)

    def append_instructions(self, program: str):
        if self.instructions:
            last_address = max(self.instructions.keys())
            next_address = last_address + self.instructions[last_address].length
        else:
            next_address = 0
        parser: RiscvParser = RiscvParser()
        for instr in parser.parse_res_to_instructions(
            parser.parse_assembly(program), start_address=0
        ):
            self.instructions[next_address] = instr
            next_address += instr.length

    def step_simulation(self):
        current_instruction = self.instructions[self.state.program_counter]
        self.state = current_instruction.behavior(self.state)
        self.state.program_counter += current_instruction.length
        self.state.performance_metrics.instruction_count += 1

    def run_simulation(self):
        """run the current simulation until no more instructions are left (pc stepped over last instruction)"""
        self.state.performance_metrics.start_timer()
        if self.instructions:
            last_address = max(self.instructions.keys())
            while self.state.program_counter <= last_address:
                self.step_simulation()
        self.state.performance_metrics.stop_timer()
