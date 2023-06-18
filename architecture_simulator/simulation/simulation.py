from ..uarch.architectural_state import ArchitecturalState
from dataclasses import dataclass, field


@dataclass
class Simulation:
    state: ArchitecturalState = field(default_factory=ArchitecturalState)

    def step_simulation(self) -> bool:
        current_instruction = self.state.instruction_memory.load_instruction(
            self.state.program_counter
        )
        self.state = current_instruction.behavior(self.state)
        self.state.program_counter += current_instruction.length
        self.state.performance_metrics.instruction_count += 1
        return self.state.instruction_at_pc()

    def run_simulation(self):
        """run the current simulation until no more instructions are left (pc stepped over last instruction)"""
        self.state.performance_metrics.start_timer()
        if self.state.instruction_memory.instructions:
            while self.state.instruction_at_pc():
                self.step_simulation()
        self.state.performance_metrics.stop_timer()
