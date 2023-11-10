from fixedint import MutableUInt16
from typing import Optional

from architecture_simulator.settings.settings import Settings
from .toy_memory import ToyMemory
from architecture_simulator.isa.toy.toy_instructions import ToyInstruction
from .toy_performance_metrics import ToyPerformanceMetrics
from .SvgVisValues import SvgVisValues


class ToyArchitecturalState:
    """Architectural State for the Toy architecture."""

    def __init__(self, unified_memory_size: Optional[int] = None):
        self.program_counter: MutableUInt16 = MutableUInt16(1)
        self.address_of_current_instruction: Optional[int] = None
        self.address_of_next_instruction = 0
        self.accu = MutableUInt16(0)
        self.memory = ToyMemory(
            address_range=(
                range(unified_memory_size)
                if unified_memory_size
                else range(Settings().get()["toy_memory_max_bytes"])
            )
        )
        self.performance_metrics = ToyPerformanceMetrics()
        self.max_pc: Optional[int] = None  # init by parser
        self.loaded_instruction: Optional[ToyInstruction] = None  # init by parser
        self.visualisation_values = SvgVisValues()

    def set_current_pc(self, address: MutableUInt16):
        """Sets the program counter to the specified address.

        Args:
            address (MutableUInt16): Address for the program counter.
        """
        self.program_counter = address

    def instruction_loaded(self) -> bool:
        """Return whether a instructions is currently loaded.

        Returns:
            bool: Whether a instructions is currently loaded.
        """
        return self.loaded_instruction is not None

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

    def get_repr(self):
        ...
        # TODO: Implement for alu_out, ram_out, accu
