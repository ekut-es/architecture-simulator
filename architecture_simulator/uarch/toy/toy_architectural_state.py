from fixedint import MutableUInt16
from typing import Optional

from .toy_memory import ToyMemory
from ..instruction_memory import InstructionMemory
from architecture_simulator.isa.toy.toy_instructions import ToyInstruction
from .toy_performance_metrics import ToyPerformanceMetrics


class ToyArchitecturalState:
    """Architectural State for the Toy architecture."""

    def __init__(
        self,
        instruction_memory_range: Optional[range] = None,
        data_memory_range: Optional[range] = None,
    ):
        self.program_counter = MutableUInt16(
            instruction_memory_range.start if instruction_memory_range else 0
        )
        self.accu = MutableUInt16(0)
        self.instruction_memory = InstructionMemory[ToyInstruction](
            address_range=(
                instruction_memory_range if instruction_memory_range else range(0, 1024)
            )
        )
        self.data_memory = ToyMemory(
            address_range=(
                data_memory_range if data_memory_range else range(1024, 4096)
            )
        )
        self.performance_metrics = ToyPerformanceMetrics()

    def increment_pc(self):
        """Increment program counter by 1."""
        self.program_counter += MutableUInt16(1)

    def instruction_at_pc(self) -> bool:
        """Return whether there is an instruction in the instruction memory at the current program counter.

        Returns:
            bool: Whether there is an instruction in the instruction memory at the current program counter.
        """
        return self.instruction_memory.instruction_at_address(int(self.program_counter))

    def get_accu_representation(self) -> tuple[str, str, str, str]:
        """Returns the values of the accu as binary, unsigned decimal, hexadecimal, signed decimal strings.

        Returns:
            tuple[str, str, str]: tuple of the binary, unsigned decimal, hexadecimal, signed decimal representation strings of the accu.
        """
        unsigned_decimal = int(self.accu)
        signed_decimal = (
            unsigned_decimal - 2**16
            if unsigned_decimal >= 2**15
            else unsigned_decimal
        )
        binary = "{:016b}".format(unsigned_decimal)
        hexadecimal = "{:04X}".format(unsigned_decimal)
        return (
            binary[:8] + " " + binary[8:],
            str(unsigned_decimal),
            hexadecimal[:2] + " " + hexadecimal[2:],
            str(signed_decimal),
        )
