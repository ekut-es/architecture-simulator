from dataclasses import dataclass, field
import fixedint

from architecture_simulator.settings.settings import Settings
from architecture_simulator.util.integer_representations import (
    get_32_bit_representations,
)


class Registers(list):
    """Custom list that overwrites [] so that register x0 gets hardwired to zero."""

    def __getitem__(self, index):
        # access of x0 will alway return zero, since x0 get´s initialized as zero and can not be changed
        # index out of bounds error will be thrown if trying to acces a register outside of x0 to x31
        return super().__getitem__(index)

    def __setitem__(self, index, value):
        # ensures, that register x0 stays 0 and that there are only 32 registers
        if index > 0 and index < 32:
            super().__setitem__(index, value)


@dataclass
class RegisterFile:
    """This class implements the register file.

    Args:
        registers:
            list[fixedint.MutableUInt32] => provided list will be used to init registers, x0 can have any value (test mode). Default: 32 registers with x0 hard wired to zero.
    """

    registers: list[fixedint.MutableUInt32] = field(
        default_factory=lambda: Registers([fixedint.MutableUInt32(0)] * 32)
    )

    def reg_repr(self) -> list[tuple[str, str, str, str]]:
        """Returns the contents of the register file as bin, udec, hex, sdec values.

        Returns:
            list[tuple[str, str, str, str]]: Register values as tuples of (bin, udec, hex, sdec)
        """
        return [get_32_bit_representations(int(reg)) for reg in self.registers]

    def get_abi_names(self, register: int) -> str:
        """Get the ABI name for the given register index.

        Args:
            register (int): Index of the register.

        Returns:
            str: ABI name of the register.
        """
        abi_names = Settings().get()["abi_names"]
        register_name = ""
        for key, value in abi_names.items():
            if value == register:
                if register_name != "":
                    register_name += "/"
                register_name += key
        return register_name
