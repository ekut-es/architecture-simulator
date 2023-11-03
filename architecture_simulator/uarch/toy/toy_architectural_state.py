from fixedint import MutableUInt16
from typing import Optional

from architecture_simulator.settings.settings import Settings
from .toy_memory import ToyMemory
from ..instruction_memory import InstructionMemory
from architecture_simulator.isa.toy.toy_instructions import ToyInstruction
from .toy_performance_metrics import ToyPerformanceMetrics


class ToyArchitecturalState:
    """Architectural State for the Toy architecture."""

    def __init__(self, unified_memory_size: Optional[int] = None):
        self.accu = MutableUInt16(0)
        self.memory = ToyMemory(
            address_range=(
                range(unified_memory_size)
                if unified_memory_size
                else range(Settings().get()["toy_memory_max_bytes"])
            )
        )
        self.max_pc: Optional[int] = None  # init by parser
        self.performance_metrics = ToyPerformanceMetrics()
        self.alu_out: Optional[MutableUInt16] = None
        self.ram_out: Optional[MutableUInt16] = None
        self.jump: Optional[bool] = None
        self.program_counter: MutableUInt16 = MutableUInt16(1)
        self.loaded_instruction: Optional[ToyInstruction] = None  # init by parser

    # def increment_pc(self):
    #    """Increment program counter by 1."""
    #    # self.previous_program_counter = MutableUInt16(int(self.program_counter)) # was macht der überhaupt
    #    self.program_counter += MutableUInt16(1)

    # NOTE: only used by brz
    def set_current_pc(self, address: MutableUInt16):
        """Sets the program counter to the specified address.

        Args:
            address (MutableUInt16): Address for the program counter.
        """
        # self.previous_program_counter = MutableUInt16(int(self.program_counter))
        self.program_counter = address

    def instruction_loaded(self) -> bool:
        """Return whether there is an instruction in the instruction memory at the current program counter.

        Returns:
            bool: Whether there is an instruction in the instruction memory at the current program counter.
        """
        # return self.instruction_memory.instruction_at_address(int(self.program_counter))
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
        # TODO: Add get repr for alu out, ram out, jump
        # TODO: Unify Memory, etc
        # TODO: Can be done in just simulation and stat files, probabliy utilize data from parser
        # TODO: Make a general display category where you can display code as instructions?!
        # TODO: Was tun wenn wer was auf seinen instruktions bereich schreiben will, sonst idee: bei verlassen von selbst def instr ber stopp
