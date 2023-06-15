# from ctypes import c_int32, c_uint32, c_int8, c_int16, c_uint8, c_uint16

from .instruction_types import RTypeInstruction, CSRTypeInstruction, CSRITypeInstruction
from .instruction_types import ITypeInstruction
from architecture_simulator.uarch.architectural_state import ArchitecturalState
from .instruction_types import BTypeInstruction
from architecture_simulator.isa.instruction_types import STypeInstruction
from architecture_simulator.isa.instruction_types import UTypeInstruction
from architecture_simulator.isa.instruction_types import JTypeInstruction
from architecture_simulator.isa.instruction_types import fence
from architecture_simulator.isa.instruction_types import Instruction
from typing import Type
import fixedint


# todo: use ctypes
class ECALLException(Exception):
    "Raises when an ECALL is executed"


class EBREAKException(Exception):
    "Raises when an EBREAK is executed"


class ADD(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="add")

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
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="sub")

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
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="sll")

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
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="slt")

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
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="sltu")

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
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="xor")

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
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="srl")

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
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="sra")

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
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="or")

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


class BEQ(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="beq")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """if (x[rs1] == x[rs2]) pc += sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs1 == rs2:
            architectural_state.program_counter += self.imm * 2 - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state


class BNE(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="bne")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """if (x[rs1] != x[rs2]) pc += sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs1 != rs2:
            architectural_state.program_counter += self.imm * 2 - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state


class BLT(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="blt")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """if (x[rs1] <s x[rs2]) pc += sext(imm)"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        rs2 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs2]))
        if rs1 < rs2:
            architectural_state.program_counter += self.imm * 2 - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state


class BGE(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="bge")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """if (x[rs1] >= x[rs2]) pc += sext(imm)"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        rs2 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs2]))
        if rs1 >= rs2:
            architectural_state.program_counter += self.imm * 2 - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state


class BLTU(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="bltu")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """if (x[rs1] <u x[rs2]) pc += sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs1 < rs2:
            architectural_state.program_counter += self.imm * 2 - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state


class BGEU(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="bgeu")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """if (x[rs1] >=u x[rs2]) pc += sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs1 >= rs2:
            architectural_state.program_counter += self.imm * 2 - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state


class CSRRW(CSRTypeInstruction):
    def __init__(self, rd: int, csr: int, rs1: int):
        super().__init__(rd, csr, rs1, mnemonic="csrrw")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = x[rs1]

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.load_word(self.csr)
        architectural_state.csr_registers.store_word(
            self.csr, architectural_state.register_file.registers[self.rs1]
        )

        return architectural_state


class CSRRS(CSRTypeInstruction):
    def __init__(self, rd: int, csr: int, rs1: int):
        super().__init__(rd, csr, rs1, mnemonic="csrrs")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = csr_register[csr] or x[rs1]

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        rs1_value = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.load_word(self.csr)
        temp = architectural_state.csr_registers.load_word(self.csr) | rs1_value
        architectural_state.csr_registers.store_word(self.csr, temp)

        return architectural_state


class CSRRC(CSRTypeInstruction):
    def __init__(self, rd: int, csr: int, rs1: int):
        super().__init__(rd, csr, rs1, mnemonic="csrrc")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = csr_register[csr] and not(x[rs1])

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        rs1_value = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.load_word(self.csr)
        temp = architectural_state.csr_registers.load_word(self.csr) & (~(rs1_value))
        architectural_state.csr_registers.store_word(self.csr, temp)

        return architectural_state


class CSRRWI(CSRITypeInstruction):
    def __init__(self, rd: int, csr: int, uimm: int):
        super().__init__(rd, csr, uimm, mnemonic="csrrwi")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = zext(uimm)

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.load_word(self.csr)
        architectural_state.csr_registers.store_word(
            self.csr, fixedint.MutableUInt32(self.uimm)
        )

        return architectural_state


class CSRRSI(CSRITypeInstruction):
    def __init__(self, rd: int, csr: int, uimm: int):
        super().__init__(rd, csr, uimm, mnemonic="csrrsi")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = csr_register[csr] or zext(uimm)

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.load_word(self.csr)
        temp = architectural_state.csr_registers.load_word(
            self.csr
        ) | fixedint.MutableUInt32(self.uimm)
        architectural_state.csr_registers.store_word(self.csr, temp)

        return architectural_state


class CSRRCI(CSRITypeInstruction):
    def __init__(self, rd: int, csr: int, uimm: int):
        super().__init__(rd, csr, uimm, mnemonic="csrrci")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = csr_register[csr] and not(zext(uimm))

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.load_word(self.csr)
        temp = architectural_state.csr_registers.load_word(self.csr) & (
            ~(fixedint.MutableUInt32(self.uimm))
        )
        architectural_state.csr_registers.store_word(self.csr, temp)

        return architectural_state


class AND(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="and")

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


class SB(STypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1, rs2, imm, mnemonic="sb")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """M[x[rs1] + sext(imm)] = x[rs2][7:0]"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2][:8]
        architectural_state.memory.store_byte(
            int(rs1 + fixedint.MutableUInt32(self.imm)), fixedint.MutableUInt8(int(rs2))
        )
        return architectural_state


class SH(STypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1, rs2, imm, mnemonic="sh")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """M[x[rs1] + sext(imm)] = x[rs2][15:0]"""
        rs2 = architectural_state.register_file.registers[self.rs2][:16]
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.memory.store_halfword(
            int(rs1 + fixedint.MutableUInt32(self.imm)),
            fixedint.MutableUInt16(int(rs2)),
        )
        return architectural_state


class SW(STypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1, rs2, imm, mnemonic="sw")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """M[x[rs1] + sext(imm)] = x[rs2][31:0]"""
        rs2 = architectural_state.register_file.registers[self.rs2]
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.memory.store_word(
            int(rs1 + fixedint.MutableUInt32(self.imm)), rs2
        )
        return architectural_state


class ADDI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="addi")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] + sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        self.imm = (self.imm & 2047) - (self.imm & 2048)  # 12-bit sext
        architectural_state.register_file.registers[
            self.rd
        ] = rs1 + fixedint.MutableUInt32(self.imm)
        return architectural_state


class ANDI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="andi")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] & sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        self.imm = (self.imm & 2047) - (self.imm & 2048)  # 12-bit sext
        architectural_state.register_file.registers[
            self.rd
        ] = rs1 & fixedint.MutableUInt32(self.imm)
        return architectural_state


class ORI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="ori")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] | sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        self.imm = (self.imm & 2047) - (self.imm & 2048)  # 12-bit sext
        architectural_state.register_file.registers[
            self.rd
        ] = rs1 | fixedint.MutableUInt32(self.imm)
        return architectural_state


class XORI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="xori")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] ^ sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        self.imm = (self.imm & 2047) - (self.imm & 2048)  # 12-bit sext
        architectural_state.register_file.registers[
            self.rd
        ] = rs1 ^ fixedint.MutableUInt32(self.imm)
        return architectural_state


class SLLI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="slli")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] << shamt  (imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = (
            rs1 << fixedint.MutableUInt32(self.imm)[0:5]
        )
        return architectural_state


class SRLI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="srli")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] >>u shamt  (imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = (
            rs1 >> fixedint.MutableUInt32(self.imm)[0:5]
        )
        return architectural_state


class SLTI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="slti")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] <s sext(imm)"""
        rs1 = fixedint.Int32(architectural_state.register_file.registers[self.rs1])
        self.imm = (self.imm & 2047) - (self.imm & 2048)  # 12-bit sext
        architectural_state.register_file.registers[self.rd] = (
            fixedint.MutableUInt32(1)
            if rs1 < fixedint.Int32(self.imm)
            else fixedint.MutableUInt32(0)
        )
        return architectural_state


class SLTIU(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="sltiu")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = x[rs1] <u sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        self.imm = (self.imm & 2047) - (self.imm & 2048)  # 12-bit sext
        architectural_state.register_file.registers[self.rd] = (
            fixedint.MutableUInt32(1)
            if rs1 < fixedint.MutableUInt32(self.imm)
            else fixedint.MutableUInt32(0)
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
        architectural_state.program_counter += self.imm * 2 - self.length
        architectural_state.performance_metrics.procedure_count += 1
        return architectural_state


class FENCE(fence):
    def __init__(self):
        super().__init__(mnemonic="fence")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """fence(pred,succ)"""
        raise NotImplementedError


class LB(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lb")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = sext(M[x[rs1] + sext(imm)][7:0])"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        # casting like this is necessary for sign extension
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(
                fixedint.Int8(
                    int(architectural_state.memory.load_byte(int(rs1) + self.imm))
                )
            )
        )
        return architectural_state


class LH(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lh")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = sext(M[x[rs1] + sext(imm)][15:0])"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(
                fixedint.Int16(
                    int(architectural_state.memory.load_halfword(int(rs1) + self.imm))
                )
            )
        )
        return architectural_state


class LW(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lw")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = sext(M[x[rs1] + sext(imm)][31:0])"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.memory.load_word(int(rs1) + self.imm)
        return architectural_state


class LBU(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lbu")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = M[x[rs1] + sext(imm)][7:0]"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(architectural_state.memory.load_byte(int(rs1) + self.imm))
        )
        return architectural_state


class LHU(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lhu")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """x[rd] = M[x[rs1] + sext(imm)][15:0]"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = fixedint.MutableUInt32(
            int(architectural_state.memory.load_halfword(int(rs1) + self.imm))
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
            int((rs1 + fixedint.Int16(self.imm)[0:12])) & (pow(2, 32) - 2)
        ) - self.length
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
            rs1 >> int(fixedint.UInt16(self.imm)[0:6])
        )
        return architectural_state


instruction_map: dict[str, Type[Instruction]] = {
    "add": ADD,
    "beq": BEQ,
    "blt": BLT,
    "bne": BNE,
    "sub": SUB,
    "bge": BGE,
    "bltu": BLTU,
    "bgeu": BGEU,
    "csrrw": CSRRW,
    "csrrs": CSRRS,
    "csrrc": CSRRC,
    "csrrwi": CSRRWI,
    "csrrsi": CSRRSI,
    "csrrci": CSRRCI,
    "sb": SB,
    "sh": SH,
    "sw": SW,
    "lui": LUI,
    "auipc": AUIPC,
    "jal": JAL,
    "fence": FENCE,
    "sll": SLL,
    "slt": SLT,
    "sltu": SLTU,
    "xor": XOR,
    "srl": SRL,
    "sra": SRA,
    "or": OR,
    "and": AND,
    "lb": LB,
    "lh": LH,
    "lw": LW,
    "lbu": LBU,
    "lhu": LHU,
    "srai": SRAI,
    "jalr": JALR,
    "ecall": ECALL,
    "ebreak": EBREAK,
    "addi": ADDI,
    "slti": SLTI,
    "sltiu": SLTIU,
    "xori": XORI,
    "ori": ORI,
    "andi": ANDI,
    "slli": SLLI,
    "srli": SRLI,
}
