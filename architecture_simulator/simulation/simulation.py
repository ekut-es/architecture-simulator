from ..isa.instruction_types import Instruction
from ..isa.parser import RiscvParser
from ..uarch.architectural_state import ArchitecturalState
from dataclasses import dataclass, field


@dataclass
class Simulation:
    state: ArchitecturalState = field(default_factory=ArchitecturalState)
    instructions: dict[int, Instruction] = field(default_factory=dict)

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
        self.state.performance_metrics.instruction_count += 1

    def run_simulation(self):
        """run the current simulation until no more instructions are left (pc stepped over last instruction)"""
        self.state.performance_metrics.start_timer()
        if self.instructions:
            last_address = max(self.instructions.keys())
            while self.state.program_counter <= last_address:
                self.step_simulation()
        self.state.performance_metrics.stop_timer()
