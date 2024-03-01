from fixedint import MutableUInt16
from typing import Optional

from architecture_simulator.settings.settings import Settings
from architecture_simulator.uarch.memory.memory import Memory, AddressingType
from architecture_simulator.isa.toy.toy_instructions import ToyInstruction
from .toy_performance_metrics import ToyPerformanceMetrics
from .SvgVisValues import SvgVisValues
from architecture_simulator.util.fixedint_12 import MutableUInt12


class ToyArchitecturalState:
    """Architectural State for the Toy architecture."""

    def __init__(self, unified_memory_size: Optional[int] = None):
        self.program_counter: MutableUInt12 = MutableUInt12(1)
        self.address_of_current_instruction: Optional[int] = None
        self.address_of_next_instruction = 0
        self.accu = MutableUInt16(0)
        self.memory = Memory(
            AddressingType.HALF_WORD,
            12,
            address_range=range(unified_memory_size)
            if unified_memory_size
            else range(Settings().get()["toy_memory_max_bytes"]),
        )
        self.performance_metrics = ToyPerformanceMetrics()
        self.max_pc: Optional[int] = None  # init by parser
        self.loaded_instruction: Optional[ToyInstruction] = None  # init by parser
        self.visualisation_values = SvgVisValues()

    def set_current_pc(self, address: MutableUInt12):
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
