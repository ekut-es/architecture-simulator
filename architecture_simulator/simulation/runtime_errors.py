from dataclasses import dataclass


@dataclass
class InstructionExecutionException(RuntimeError):
    address: int
    instruction_repr: str
    error_message: str

    def __repr__(self):
        hex_address = "0x" + "{:X}".format(self.address)
        return f"There was an error executing '{self.instruction_repr}' at address {hex_address}:\n{self.error_message}"


@dataclass
class StepSequenceError(RuntimeError):
    message: str

    def __repr__(self) -> str:
        return self.message
