from dataclasses import dataclass, field
import fixedint


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
        abi_names = {
            0: "zero",
            1: "ra",
            2: "sp",
            3: "gp",
            4: "tp",
            5: "t0",
            6: "t1",
            7: "t2",
            8: "s0/fp",  # this is intentional
            9: "s1",
            10: "a0",
            11: "a1",
            12: "a2",
            13: "a3",
            14: "a4",
            15: "a5",
            16: "a6",
            17: "a7",
            18: "s2",
            19: "s3",
            20: "s4",
            21: "s5",
            22: "s6",
            23: "s7",
            24: "s8",
            25: "s9",
            26: "s10",
            27: "s11",
            28: "t3",
            29: "t4",
            30: "t5",
            31: "t6",
        }
        return abi_names[register]
