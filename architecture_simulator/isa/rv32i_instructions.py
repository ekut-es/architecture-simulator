# from ctypes import c_int32, c_uint32, c_int8, c_int16, c_uint8, c_uint16

from .instruction_types import RTypeInstruction
from ..uarch.architectural_state import ArchitecturalState
import fixedint

# todo: use ctypes


class ADD(RTypeInstruction):
    def __init__(self, rs1: int, rs2: int, rd: int):
        super().__init__(rs1, rs2, rd, mnemonic="add")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """
        Addition:
            rd = rs1 + rs2

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = rs1 + rs2
        return architectural_state


class SUB(RTypeInstruction):
    def __init__(self, rs1: int, rs2: int, rd: int):
        super().__init__(rs1, rs2, rd, mnemonic="sub")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """
        Subtraction:
            rd = rs1 - rs2

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(fixedint.Int32(int(rs1)) - fixedint.Int32(int(rs2)))
        )
        return architectural_state


class SLL(RTypeInstruction):
    def __init__(self, rs1: int, rs2: int, rd: int):
        super().__init__(rs1, rs2, rd, mnemonic="sll")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """
        Shift left logical:
            rd = rs1 << rs2

        (shift amount determined by lower 5 bits of rs2)

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[
            self.rs2
        ] % fixedint.MutableUInt32(32)
        architectural_state.register_file.registers[self.rd] = rs1 << rs2
        return architectural_state


class SLT(RTypeInstruction):
    def __init__(self, rs1: int, rs2: int, rd: int):
        super().__init__(rs1, rs2, rd, mnemonic="slt")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """
        Set lower than:
            rd = 1 if (rs1 < rs2) else 0

        (register values are interpreted as signed integers)

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        rs2 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs2]))
        architectural_state.register_file.registers[self.rd] = (
            fixedint.MutableUInt32(1) if rs1 < rs2 else fixedint.MutableUInt32(0)
        )
        return architectural_state


class SLTU(RTypeInstruction):
    def __init__(self, rs1: int, rs2: int, rd: int):
        super().__init__(rs1, rs2, rd, mnemonic="sltu")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """
        Set lower than unsigned:
            rd = 1 if (rs1 < rs2) else 0

        (register values are interpreted as unsigned integers)

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = (
            fixedint.MutableUInt32(1) if rs1 < rs2 else fixedint.MutableUInt32(0)
        )
        return architectural_state


class XOR(RTypeInstruction):
    def __init__(self, rs1: int, rs2: int, rd: int):
        super().__init__(rs1, rs2, rd, mnemonic="xor")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """
        XOR:
            rd = rs1 ^ rs2

        (executed bitwise)

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = rs1 ^ rs2
        return architectural_state


class SRL(RTypeInstruction):
    def __init__(self, rs1: int, rs2: int, rd: int):
        super().__init__(rs1, rs2, rd, mnemonic="srl")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """
        Shift right logical:
            rd = rs1 >> rs2

        (shift amount determined by lower 5 bits of rs2)

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[
            self.rs2
        ] % fixedint.MutableUInt32(32)
        architectural_state.register_file.registers[self.rd] = rs1 >> rs2
        return architectural_state


class SRA(RTypeInstruction):
    def __init__(self, rs1: int, rs2: int, rd: int):
        super().__init__(rs1, rs2, rd, mnemonic="sra")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """
        Shift right arithmetic:
            rd = rs1 >>s rs2

        (shift amount determined by lower 5 bits of rs2)

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        rs2 = fixedint.Int32(
            int(
                architectural_state.register_file.registers[self.rs2]
                % fixedint.MutableUInt32(32)
            )
        )
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(rs1 >> rs2)
        )
        return architectural_state


class OR(RTypeInstruction):
    def __init__(self, rs1: int, rs2: int, rd: int):
        super().__init__(rs1, rs2, rd, mnemonic="or")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """
        OR:
            rd = rs1 | rs2

        (executed bitwise)

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = rs1 | rs2
        return architectural_state


class AND(RTypeInstruction):
    def __init__(self, rs1: int, rs2: int, rd: int):
        super().__init__(rs1, rs2, rd, mnemonic="and")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """
        AND:
            rd = rs1 & rs2

        (executed bitwise)

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = rs1 & rs2
        return architectural_state


instruction_map = {
    "add": ADD,
    "sub": SUB,
    "sll": SLL,
    "slt": SLT,
    "sltu": SLTU,
    "xor": XOR,
    "srl": SRL,
    "sra": SRA,
    "or": OR,
    "and": AND,
}
