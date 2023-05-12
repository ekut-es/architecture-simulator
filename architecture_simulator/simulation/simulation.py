from dataclasses import dataclass
import time
from ..isa.instruction_types import Instruction
from ..isa.parser import riscv_parser
from ..uarch.architectural_state import ArchitecturalState
from architecture_simulator.simulation.performance_metrics import PerformanceMetrics


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

    def run_simulation(self) -> PerformanceMetrics:
        """run the current simulation until no more instructions are left (pc stepped over last instruction)

        Returns:
            PerformanceMetrics: Some performance metrics about the simulation.
        """
        start = time.time()
        instruction_count = 0
        branch_count = 0
        if self.instructions:
            last_address = max(self.instructions.keys())
            while self.state.program_counter <= last_address:
                pc_before = self.state.program_counter
                self.state = self.instructions[self.state.program_counter].behavior(
                    self.state
                )
                self.state.program_counter += 4
                instruction_count += 1
                if self.state.program_counter - pc_before != 4:
                    branch_count += 1
        execution_time = time.time() - start
        return PerformanceMetrics(
            execution_time_s=execution_time,
            instruction_count=instruction_count,
            branch_count=branch_count,
            instructions_per_second=instruction_count / execution_time,
        )
