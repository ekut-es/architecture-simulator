# from ctypes import c_int32, c_uint32, c_int8, c_int16, c_uint8, c_uint16

from .instruction_types import RTypeInstruction
from .instruction_types import ITypeInstruction
from ..uarch.architectural_state import ArchitecturalState
import fixedint

# todo: use ctypes
class ECALLException(Exception):
    "Raises when an ECALL is executed"


class EBREAKException(Exception):
    "Raises when an EBREAK is executed"


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


class LB(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lb")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = sext(M[x[rs1] + sext(imm)][7:0])"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(
                fixedint.Int8(
                    int(architectural_state.memory.load_byte(int(rs1 + self.imm)))
                )
            )
        )
        return architectural_state


class LH(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lh")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = sext(M[x[rs1] + sext(imm)][15:0])"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(
                fixedint.Int16(
                    int(architectural_state.memory.load_halfword(int(rs1 + self.imm)))
                )
            )
        )
        return architectural_state


class LW(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lw")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = sext(M[x[rs1] + sext(imm)][31:0])"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(
                fixedint.Int32(
                    int(architectural_state.memory.load_word(int(rs1 + self.imm)))
                )
            )
        )
        return architectural_state


class LBU(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lbu")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = M[x[rs1] + sext(imm)][7:0]"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(architectural_state.memory.load_byte(int(rs1 + self.imm)))
        )
        return architectural_state


class LHU(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lhu")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = M[x[rs1] + sext(imm)][15:0]"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(architectural_state.memory.load_halfword(int(rs1 + self.imm)))
        )
        return architectural_state


class JALR(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="jalr")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """t=pc+4; pc=(x[rs1]+sext(imm))&∼1; x[rd]=t"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            architectural_state.program_counter + 4
        )
        architectural_state.program_counter = (
            int((rs1 + self.imm)) & (pow(2, 32) - 2)
        ) - 4
        return architectural_state


class ECALL(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="ecall")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """RaiseException(EnvironmentCall)"""
        raise ECALLException
        return architectural_state


class EBREAK(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="ebreak")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """RaiseException(EnvironmentCall)"""
        raise EBREAKException
        return architectural_state


class SRAI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="srai")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] >>s shamt"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            rs1 >> self.imm
        )
        return architectural_state


instruction_map = {
    "add": ADD,
    "sub": SUB,
}
