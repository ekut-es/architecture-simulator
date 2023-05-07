# from ctypes import c_int32, c_uint32, c_int8, c_int16, c_uint8, c_uint16

from .instruction_types import RTypeInstruction, CSRTypeInstruction, CSRITypeInstruction
from architecture_simulator.uarch.architectural_state import ArchitecturalState
from .instruction_types import RTypeInstruction
from .instruction_types import BTypeInstruction
from ..uarch.architectural_state import ArchitecturalState
import fixedint


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
            architectural_state.program_counter += self.imm * 2 - 4
        return architectural_state


class BNE(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="bne")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """if (x[rs1] != x[rs2]) pc += sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs1 != rs2:
            architectural_state.program_counter += self.imm * 2 - 4
        return architectural_state


class BLT(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="blt")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """if (x[rs1] <s x[rs2]) pc += sext(imm)"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        rs2 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs2]))
        if rs1 < rs2:
            architectural_state.program_counter += self.imm * 2 - 4
        return architectural_state


class BGE(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="bge")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """if (x[rs1] >= x[rs2]) pc += sext(imm)"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        rs2 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs2]))
        if rs1 >= rs2:
            architectural_state.program_counter += self.imm * 2 - 4
        return architectural_state


class BLTU(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="bltu")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """if (x[rs1] <u x[rs2]) pc += sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs1 < rs2:
            architectural_state.program_counter += self.imm * 2 - 4
        return architectural_state


class BGEU(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="bgeu")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """if (x[rs1] >=u x[rs2]) pc += sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs1 >= rs2:
            architectural_state.program_counter += self.imm * 2 - 4
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
        architectural_state.register_file.registers[self.rd] = architectural_state.csr_registers.load_word(self.csr)
        architectural_state.csr_registers.store_word(self.csr, architectural_state.register_file.registers[self.rs1])

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
        architectural_state.register_file.registers[self.rd] = architectural_state.csr_registers.load_word(self.csr)
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
        architectural_state.register_file.registers[self.rd] = architectural_state.csr_registers.load_word(self.csr)
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
        architectural_state.register_file.registers[self.rd] = architectural_state.csr_registers.load_word(self.csr)
        architectural_state.csr_registers.store_word(self.csr, fixedint.MutableUInt32(self.uimm))

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
        architectural_state.register_file.registers[self.rd] = architectural_state.csr_registers.load_word(self.csr)
        temp = architectural_state.csr_registers.load_word(self.csr) | fixedint.MutableUInt32(self.uimm)
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
        architectural_state.register_file.registers[self.rd] = architectural_state.csr_registers.load_word(self.csr)
        temp = architectural_state.csr_registers.load_word(self.csr) & (~(fixedint.MutableUInt32(self.uimm)))
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
