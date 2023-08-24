from dataclasses import dataclass, field
import fixedint

from architecture_simulator.settings.settings import Settings


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

    def reg_repr(self) -> dict[int, tuple[str, str, str, str]]:
        """Returns the contents of the register file as binary, unsigned decimal, hexadecimal, signed decimal values.

        Returns:
            dict[int, tuple[str, str, str, str]]: keys: register indices. Values: Register values as tuple of (binary, unsigned decimal, hexadecimal, signed decimal)
        """
        reg_repr: dict[int, tuple[str, str, str, str]] = dict()
        index = 0
        for reg in self.registers:
            val = int(reg)
            signed_decimal = val - 2**32 if val >= 2**31 else val
            bin_reg = "{:032b}".format(int(reg))
            hex_reg = "{:08X}".format(int(reg))
            bin_reg_with_spaces = (
                bin_reg[0:8]
                + " "
                + bin_reg[8:16]
                + " "
                + bin_reg[16:24]
                + " "
                + bin_reg[24:32]
            )
            hex_reg_with_spaces = (
                hex_reg[0:2]
                + " "
                + hex_reg[2:4]
                + " "
                + hex_reg[4:6]
                + " "
                + hex_reg[6:8]
            )
            reg_repr[index] = (
                bin_reg_with_spaces,
                str(reg),
                hex_reg_with_spaces,
                str(signed_decimal),
            )
            index += 1
        return reg_repr

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
