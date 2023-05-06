# from ctypes import c_int32, c_uint32, c_int8, c_int16, c_uint8, c_uint16

from .instruction_types import RTypeInstruction, ITypeInstruction
from ..uarch.architectural_state import ArchitecturalState
import fixedint

# todo: use ctypes


class ADD(RTypeInstruction):
    def __init__(self, rs1: int, rs2: int, rd: int):
        super().__init__(rs1, rs2, rd, mnemonic="add")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        # rd = rs1 + rs2
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = rs1 + rs2
        return architectural_state


class SUB(RTypeInstruction):
    def __init__(self, rs1: int, rs2: int, rd: int):
        super().__init__(rs1, rs2, rd, mnemonic="add")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """rd = rs1 - rs2

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = rs1 - rs2
        return architectural_state


class ADDI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="addi")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] + sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = rs1 + self.imm
        return architectural_state


class ANDI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="andi")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] & sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = rs1 & self.imm
        return architectural_state


class ORI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="ori")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] | sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = rs1 | self.imm
        return architectural_state


class XORI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="xori")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] ^ sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = rs1 ^ self.imm
        return architectural_state


class SLLI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="slli")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] << shamt  (imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = rs1 ^ self.imm
        return architectural_state


class SRLI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="srli")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] >>u shamt  (imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = rs1 >> self.imm
        return architectural_state


class SRAI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="srai")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] >>s shamt  (imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = rs1 >> self.imm
        return architectural_state


class SLTI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="slti")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] <s sext(imm)"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = (
            fixedint.MutableUInt32(1) if rs1 < self.imm else fixedint.MutableUInt32(0)
        )
        return architectural_state


class SLTIU(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="sltiu")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] <u sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = (
            fixedint.MutableUInt32(1)
            if rs1 < fixedint.UInt32(self.imm)
            else fixedint.MutableUInt32(0)
        )
        return architectural_state


instruction_map = {"add": ADD, "sub": SUB}
