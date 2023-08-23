from dataclasses import dataclass


@dataclass
class InstructionExecutionException(RuntimeError):
    address: int
    instruction_repr: str
    error_message: str

    def __repr__(self):
        return f"There was an error executing the instruction at address '{self.address}': '{self.instruction_repr}':\n{self.error_message}"
