# from ctypes import c_int32, c_uint32, c_int8, c_int16, c_uint8, c_uint16

from architecture_simulator.isa.instruction_types import RTypeInstruction
from architecture_simulator.isa.instruction_types import STypeInstruction
from architecture_simulator.isa.instruction_types import UTypeInstruction
from architecture_simulator.isa.instruction_types import JTypeInstruction
from architecture_simulator.isa.instruction_types import fence
from architecture_simulator.uarch.architectural_state import ArchitecturalState
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


class SB(STypeInstruction):
    def __init(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1, rs2, imm, mnemonic="sb")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """M[x[rs1] + sext(imm)] = x[rs2][7:0]"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2][-8:]
        architectural_state.memory.store_byte(
            int(rs1 + fixedint.MutableUInt32(self.imm)), fixedint.MutableUInt8(int(rs2))
        )
        return architectural_state


class SH(STypeInstruction):
    def __init(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1, rs2, imm, mnemonic="sh")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """M[x[rs1] + sext(imm)] = x[rs2][15:0]"""
        rs2 = architectural_state.register_file.registers[self.rs2][-16:]
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.memory.store_halfword(
            int(rs1 + fixedint.MutableUInt32(self.imm)),
            fixedint.MutableUInt16(int(rs2)),
        )
        return architectural_state


class SW(STypeInstruction):
    def __init(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1, rs2, imm, mnemonic="sw")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """M[x[rs1] + sext(imm)] = x[rs2][31:0]"""
        rs2 = architectural_state.register_file.registers[self.rs2]
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.memory.store_word(
            int(rs1 + fixedint.MutableUInt32(self.imm)), rs2
        )
        return architectural_state


class LUI(UTypeInstruction):
    def __init__(self, rd: int, imm: int):
        super().__init__(rd, imm, mnemonic="lui")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = sext(imm[31:12] << 12)"""
        imm = self.imm << 12
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            imm
        )
        return architectural_state


class AUIPC(UTypeInstruction):
    def __init__(self, rd: int, imm: int):
        super().__init__(rd, imm, mnemonic="auipc")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = pc + sext(imm[31:12] << 12)"""
        imm = self.imm << 12
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            architectural_state.program_counter + imm
        )
        return architectural_state


class JAL(JTypeInstruction):
    def __init__(self, rd: int, imm: int):
        super().__init__(rd, imm, mnemonic="jal")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd]=pc+4; pc+=sext(imm)"""
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            architectural_state.program_counter + 4
        )
        architectural_state.program_counter += self.imm * 2 - 4
        return architectural_state


class FENCE(fence):
    def __init__(self):
        super().__init__(mnemonic="fence")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """fence(pred,succ)"""
        raise NotImplementedError


instruction_map = {"add": ADD, "sub": SUB}
