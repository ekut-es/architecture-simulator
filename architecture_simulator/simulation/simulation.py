from ..uarch.architectural_state import ArchitecturalState
from dataclasses import dataclass, field


@dataclass
class Simulation:
    state: ArchitecturalState = field(default_factory=ArchitecturalState)

    def step_simulation(self) -> bool:
        current_instruction = self.state.instruction_memory.load_instruction(
            self.state.program_counter
        )
        try:
            self.state = current_instruction.behavior(self.state)
        except Exception as e:
            raise InstructionExecutionException(
                address=self.state.program_counter,
                instruction_repr=current_instruction.__repr__(),
                error_message=e.__repr__(),
            )
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


@dataclass
class InstructionExecutionException(RuntimeError):
    address: int
    instruction_repr: str
    error_message: str

    def __repr__(self):
        return f"There was an error executing the instruction at address '{self.address}': '{self.instruction_repr}':\n{self.error_message}"
