from __future__ import annotations
from struct import unpack
from typing import Optional, Type, TYPE_CHECKING
from dataclasses import dataclass
import fixedint

from architecture_simulator.uarch.riscv.control_unit_signals import ControlUnitSignals
from .instruction_types import (
    RiscvInstruction,
    RTypeInstruction,
    ITypeInstruction,
    ShiftITypeInstruction,
    MemoryITypeInstruction,
    STypeInstruction,
    BTypeInstruction,
    UTypeInstruction,
    JTypeInstruction,
    FenceTypeInstruction,
    CSRTypeInstruction,
    CSRITypeInstruction,
)

if TYPE_CHECKING:
    from architecture_simulator.uarch.riscv.riscv_architectural_state import (
        RiscvArchitecturalState,
    )


@dataclass
class InstructionNotImplemented(NotImplementedError):
    mnemonic: str

    def __repr__(self):
        return f"Instruction {self.mnemonic} is not yet implemented"


class ADD(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="add")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
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

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = int(left + right)
        return (None, result)


class SUB(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="sub")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
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
        architectural_state.register_file.registers[self.rd] = rs1 - rs2
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = int(left - right)
        return (None, result)


class SLL(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="sll")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
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
        rs2 = architectural_state.register_file.registers[self.rs2] % fixedint.UInt32(
            32
        )
        architectural_state.register_file.registers[self.rd] = rs1 << rs2
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2) % fixedint.UInt32(32)
        result = int(left << right)
        return (None, result)


class SLT(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="slt")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
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
            fixedint.UInt32(1) if rs1 < rs2 else fixedint.UInt32(0)
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.Int32(alu_in_1)
        right = fixedint.Int32(alu_in_2)
        result = 1 if left < right else 0
        return (None, result)


class SLTU(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="sltu")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
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
            fixedint.UInt32(1) if rs1 < rs2 else fixedint.UInt32(0)
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = 1 if left < right else 0
        return (None, result)


class XOR(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="xor")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
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

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = int(left ^ right)
        return (None, result)


class SRL(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="srl")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
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
        rs2 = architectural_state.register_file.registers[self.rs2] % fixedint.UInt32(
            32
        )
        architectural_state.register_file.registers[self.rd] = rs1 >> rs2
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2) % fixedint.UInt32(32)
        result = int(left >> right)
        return (None, result)


class SRA(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="sra")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
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
            architectural_state.register_file.registers[self.rs2] % fixedint.UInt32(32)
        )
        architectural_state.register_file.registers[self.rd] = fixedint.UInt32(
            rs1 >> rs2
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.Int32(alu_in_1)
        right = fixedint.Int32(int(fixedint.UInt32(alu_in_2) % fixedint.UInt32(32)))
        result = int(left >> right)
        return (None, result)


class OR(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="or")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
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

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = int(left | right)
        return (None, result)


class AND(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="and")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
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

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = int(left & right)
        return (None, result)


class ADDI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="addi")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] + sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = rs1 + fixedint.UInt32(
            self.imm
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = int(left + right)
        return (None, result)


class SLTI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="slti")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] <s sext(imm)"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = (
            fixedint.UInt32(1) if rs1 < fixedint.Int32(self.imm) else fixedint.UInt32(0)
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.Int32(alu_in_1)
        right = fixedint.Int32(alu_in_2)
        result = 1 if left < right else 0
        return (None, result)


class SLTIU(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="sltiu")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] <u sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = (
            fixedint.UInt32(1)
            if rs1 < fixedint.UInt32(self.imm)
            else fixedint.UInt32(0)
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = 1 if left < right else 0
        return (None, result)


class XORI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="xori")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] ^ sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = rs1 ^ fixedint.UInt32(
            self.imm
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = int(left ^ right)
        return (None, result)


class ORI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="ori")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] | sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = rs1 | fixedint.UInt32(
            self.imm
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = int(left | right)
        return (None, result)


class ANDI(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="andi")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] & sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = rs1 & fixedint.UInt32(
            self.imm
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = int(left & right)
        return (None, result)


class SLLI(ShiftITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="slli")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] << shamt  (imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = rs1 << fixedint.UInt32(
            self.imm
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = int(left << right)
        return (None, result)


class SRLI(ShiftITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="srli")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] >>u shamt  (imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = rs1 >> fixedint.UInt32(
            self.imm
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = int(left >> right)
        return (None, result)


class SRAI(ShiftITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="srai")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = x[rs1] >>s shamt   (imm)"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = fixedint.UInt32(
            rs1 >> fixedint.UInt16(self.imm)
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.Int32(alu_in_1)
        right = alu_in_2
        result = int(left >> right)
        return (None, result)


class LB(MemoryITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lb")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = sext(M[x[rs1] + sext(imm)][7:0])"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        # casting like this is necessary for sign extension
        architectural_state.register_file.registers[self.rd] = fixedint.UInt32(
            fixedint.Int8(architectural_state.memory.read_byte(int(rs1) + self.imm))
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = alu_in_2
        result = int(left) + right
        return (None, result)

    def memory_access(
        self,
        memory_address: Optional[int],
        memory_write_data: Optional[int],
        architectural_state: RiscvArchitecturalState,
        update_statistics: bool = True,
    ) -> Optional[int]:
        assert memory_address is not None
        return int(
            fixedint.Int8(
                int(
                    architectural_state.memory.read_byte(
                        memory_address, update_statistics=update_statistics
                    )
                )
            )
        )


class LH(MemoryITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lh")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = sext(M[x[rs1] + sext(imm)][15:0])"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[self.rd] = fixedint.UInt32(
            fixedint.Int16(
                architectural_state.memory.read_halfword(int(rs1) + self.imm)
            )
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = alu_in_2
        result = int(left) + right
        return (None, result)

    def memory_access(
        self,
        memory_address: Optional[int],
        memory_write_data: Optional[int],
        architectural_state: RiscvArchitecturalState,
        update_statistics: bool = True,
    ) -> Optional[int]:
        assert memory_address is not None
        return int(
            fixedint.Int16(
                int(
                    architectural_state.memory.read_halfword(
                        memory_address, update_statistics=update_statistics
                    )
                )
            )
        )


class LW(MemoryITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lw")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = sext(M[x[rs1] + sext(imm)][31:0])"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.memory.read_word(int(rs1) + self.imm)
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = alu_in_2
        result = int(left) + right
        return (None, result)

    def memory_access(
        self,
        memory_address: Optional[int],
        memory_write_data: Optional[int],
        architectural_state: RiscvArchitecturalState,
        update_statistics: bool = True,
    ) -> Optional[int]:
        assert memory_address is not None
        return int(
            architectural_state.memory.read_word(
                memory_address, update_statistics=update_statistics
            )
        )


class LBU(MemoryITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lbu")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = M[x[rs1] + sext(imm)][7:0]"""
        rs1 = int(architectural_state.register_file.registers[self.rs1])
        architectural_state.register_file.registers[self.rd] = fixedint.UInt32(
            architectural_state.memory.read_byte(rs1 + self.imm)
        )

        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = alu_in_2
        result = int(left) + right
        return (None, result)

    def memory_access(
        self,
        memory_address: Optional[int],
        memory_write_data: Optional[int],
        architectural_state: RiscvArchitecturalState,
        update_statistics: bool = True,
    ) -> Optional[int]:
        assert memory_address is not None
        return int(
            architectural_state.memory.read_byte(
                memory_address, update_statistics=update_statistics
            )
        )


class LHU(MemoryITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="lhu")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = M[x[rs1] + sext(imm)][15:0]"""
        rs1 = int(architectural_state.register_file.registers[self.rs1])
        architectural_state.register_file.registers[self.rd] = fixedint.UInt32(
            architectural_state.memory.read_halfword(rs1 + self.imm)
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = alu_in_2
        result = int(left) + right
        return (None, result)

    def memory_access(
        self,
        memory_address: Optional[int],
        memory_write_data: Optional[int],
        architectural_state: RiscvArchitecturalState,
        update_statistics: bool = True,
    ) -> Optional[int]:
        assert memory_address is not None
        return int(
            architectural_state.memory.read_halfword(
                memory_address, update_statistics=update_statistics
            )
        )


class JALR(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="jalr")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """t=pc+4; pc=(x[rs1]+sext(imm))&∼1; x[rd]=t"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        architectural_state.register_file.registers[self.rd] = fixedint.UInt32(
            architectural_state.program_counter + 4
        )
        architectural_state.program_counter = (
            int((rs1 + fixedint.Int16(self.imm))) & (pow(2, 32) - 2)
        ) - self.length
        return architectural_state

    def control_unit_signals(self) -> ControlUnitSignals:
        return ControlUnitSignals(
            alu_src_1=True,
            alu_src_2=True,
            wb_src=0,
            reg_write=True,
            mem_read=False,
            mem_write=False,
            branch=False,
            jump=False,
            alu_op=None,
            alu_to_pc=True,
        )

    def alu_compute(
        self, alu_in_1: int | None, alu_in_2: int | None
    ) -> tuple[bool | None, int | None]:
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        return None, ((alu_in_1 + alu_in_2) & (~1))


class ECALL(ITypeInstruction):
    def __init__(self):
        super().__init__(0, 0, 1, mnemonic="ecall")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """RaiseException(EnvironmentCall)"""
        code = int(architectural_state.register_file.registers[17])
        arg = int(architectural_state.register_file.registers[10])

        match code:
            case 1:  # print arg as sint
                architectural_state.output += str(fixedint.Int32(arg))
            case 2:  # print arg as 32-bit float
                architectural_state.output += str(
                    unpack(">f", arg.to_bytes(4, "big"))[0]
                )
            case 11:  # print arg as ascii char
                architectural_state.output += chr(arg % 128)
            case 34:  # print arg as hex
                architectural_state.output += "0x" + "{:X}".format(arg)
            case 35:  # print arg as bin
                architectural_state.output += bin(arg)
            case 36:  # print arg as uint
                architectural_state.output += str(arg)
            case 10:  # exit with status 0
                architectural_state.exit_code = 0
            case 93:  # exit with arg as status
                architectural_state.exit_code = arg
            case _:
                raise ValueError(f"{code} (register a7) is not a valid code for ECALL")
        return architectural_state

    def __repr__(self) -> str:
        return self.mnemonic


class EBREAK(ITypeInstruction):
    def __init__(self, rd: int, rs1: int, imm: int):
        super().__init__(rd, rs1, imm, mnemonic="ebreak")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """RaiseException(EnvironmentCall)"""
        raise InstructionNotImplemented(mnemonic=self.mnemonic)
        return architectural_state

    def __repr__(self) -> str:
        return self.mnemonic


class SB(STypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1, rs2, imm, mnemonic="sb")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """M[x[rs1] + sext(imm)] = x[rs2][7:0]"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2][:8]
        architectural_state.memory.write_byte(
            int(rs1 + fixedint.UInt32(self.imm)), fixedint.UInt8(rs2)
        )
        return architectural_state

    def memory_access(
        self,
        memory_address: Optional[int],
        memory_write_data: Optional[int],
        architectural_state: RiscvArchitecturalState,
        update_statistics: bool = True,
    ) -> Optional[int]:
        if memory_address is not None and memory_write_data is not None:
            architectural_state.memory.write_byte(
                memory_address,
                fixedint.UInt8(memory_write_data),
                directly_write_to_lower_memory=not update_statistics,
            )
        return None

    def access_register_file(
        self, architectural_state: RiscvArchitecturalState
    ) -> tuple[
        Optional[int], Optional[int], Optional[int], Optional[int], Optional[int]
    ]:
        return (
            self.rs1,
            self.rs2,
            int(architectural_state.register_file.registers[self.rs1]),
            int(architectural_state.register_file.registers[self.rs2][:8]),
            self.imm,
        )


class SH(STypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1, rs2, imm, mnemonic="sh")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """M[x[rs1] + sext(imm)] = x[rs2][15:0]"""
        rs2 = architectural_state.register_file.registers[self.rs2][:16]
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.memory.write_halfword(
            int(rs1 + fixedint.UInt32(self.imm)),
            fixedint.UInt16((rs2)),
        )
        return architectural_state

    def access_register_file(
        self, architectural_state: RiscvArchitecturalState
    ) -> tuple[
        Optional[int], Optional[int], Optional[int], Optional[int], Optional[int]
    ]:
        return (
            self.rs1,
            self.rs2,
            int(architectural_state.register_file.registers[self.rs1]),
            int(architectural_state.register_file.registers[self.rs2][:16]),
            self.imm,
        )

    def memory_access(
        self,
        memory_address: Optional[int],
        memory_write_data: Optional[int],
        architectural_state: RiscvArchitecturalState,
        update_statistics: bool = True,
    ) -> Optional[int]:
        if memory_address is not None and memory_write_data is not None:
            architectural_state.memory.write_halfword(
                memory_address,
                fixedint.UInt16(memory_write_data),
                directly_write_to_lower_memory=not update_statistics,
            )
        return None


class SW(STypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1, rs2, imm, mnemonic="sw")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """M[x[rs1] + sext(imm)] = x[rs2][31:0]"""
        rs2 = architectural_state.register_file.registers[self.rs2]
        rs1 = architectural_state.register_file.registers[self.rs1]
        architectural_state.memory.write_word(int(rs1 + fixedint.UInt32(self.imm)), rs2)
        return architectural_state

    def access_register_file(
        self, architectural_state: RiscvArchitecturalState
    ) -> tuple[
        Optional[int], Optional[int], Optional[int], Optional[int], Optional[int]
    ]:
        return (
            self.rs1,
            self.rs2,
            int(architectural_state.register_file.registers[self.rs1]),
            int(architectural_state.register_file.registers[self.rs2]),
            self.imm,
        )

    def memory_access(
        self,
        memory_address: Optional[int],
        memory_write_data: Optional[int],
        architectural_state: RiscvArchitecturalState,
        update_statistics: bool = True,
    ) -> Optional[int]:
        if memory_address is not None and memory_write_data is not None:
            architectural_state.memory.write_word(
                memory_address,
                fixedint.UInt32(memory_write_data),
                directly_write_to_lower_memory=not update_statistics,
            )
        return None


class BEQ(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="beq")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """if (x[rs1] == x[rs2]) pc += sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs1 == rs2:
            architectural_state.program_counter += self.imm - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state

    def alu_compute(
        self, alu_in_1: int | None, alu_in_2: int | None
    ) -> tuple[bool | None, int | None]:
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        return (alu_in_1 == alu_in_2), None


class BNE(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="bne")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """if (x[rs1] != x[rs2]) pc += sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs1 != rs2:
            architectural_state.program_counter += self.imm - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state

    def alu_compute(
        self, alu_in_1: int | None, alu_in_2: int | None
    ) -> tuple[bool | None, int | None]:
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        return (alu_in_1 != alu_in_2), None


class BLT(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="blt")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """if (x[rs1] <s x[rs2]) pc += sext(imm)"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        rs2 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs2]))
        if rs1 < rs2:
            architectural_state.program_counter += self.imm - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state

    def alu_compute(
        self, alu_in_1: int | None, alu_in_2: int | None
    ) -> tuple[bool | None, int | None]:
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        # casting for signed comparison (inputs are unsigned)
        return (fixedint.Int32(alu_in_1) < fixedint.Int32(alu_in_2)), None


class BGE(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="bge")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """if (x[rs1] >= x[rs2]) pc += sext(imm)"""
        rs1 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs1]))
        rs2 = fixedint.Int32(int(architectural_state.register_file.registers[self.rs2]))
        if rs1 >= rs2:
            architectural_state.program_counter += self.imm - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state

    def alu_compute(
        self, alu_in_1: int | None, alu_in_2: int | None
    ) -> tuple[bool | None, int | None]:
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        # casting for signed comparison (inputs are unsigned)
        return (fixedint.Int32(alu_in_1) >= fixedint.Int32(alu_in_2)), None


class BLTU(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="bltu")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """if (x[rs1] <u x[rs2]) pc += sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs1 < rs2:
            architectural_state.program_counter += self.imm - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state

    def alu_compute(
        self, alu_in_1: int | None, alu_in_2: int | None
    ) -> tuple[bool | None, int | None]:
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        return (alu_in_1 < alu_in_2), None


class BGEU(BTypeInstruction):
    def __init__(self, rs1: int, rs2: int, imm: int):
        super().__init__(rs1=rs1, rs2=rs2, imm=imm, mnemonic="bgeu")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """if (x[rs1] >=u x[rs2]) pc += sext(imm)"""
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs1 >= rs2:
            architectural_state.program_counter += self.imm - self.length
            architectural_state.performance_metrics.branch_count += 1
        return architectural_state

    def alu_compute(
        self, alu_in_1: int | None, alu_in_2: int | None
    ) -> tuple[bool | None, int | None]:
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        return (alu_in_1 >= alu_in_2), None


class LUI(UTypeInstruction):
    def __init__(self, rd: int, imm: int):
        super().__init__(rd, imm, mnemonic="lui")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = sext(imm[31:12] << 12)"""
        imm = self.imm << 12
        architectural_state.register_file.registers[self.rd] = fixedint.UInt32(imm)
        return architectural_state

    def control_unit_signals(self) -> ControlUnitSignals:
        return ControlUnitSignals(
            alu_src_1=None,
            alu_src_2=None,
            wb_src=3,
            reg_write=True,
            mem_read=False,
            mem_write=False,
            branch=False,
            jump=False,
            alu_op=None,
            alu_to_pc=False,
        )


class AUIPC(UTypeInstruction):
    def __init__(self, rd: int, imm: int):
        super().__init__(rd, imm, mnemonic="auipc")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = pc + sext(imm[31:12] << 12)"""
        imm = self.imm << 12
        architectural_state.register_file.registers[self.rd] = fixedint.UInt32(
            architectural_state.program_counter + imm
        )
        return architectural_state

    def control_unit_signals(self) -> ControlUnitSignals:
        return ControlUnitSignals(
            alu_src_1=False,
            alu_src_2=True,
            wb_src=2,
            reg_write=True,
            mem_read=False,
            mem_write=False,
            branch=False,
            jump=False,
            alu_op=None,
            alu_to_pc=False,
        )

    def alu_compute(
        self, alu_in_1: int | None, alu_in_2: int | None
    ) -> tuple[bool | None, int | None]:
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        return None, (alu_in_1 + alu_in_2)


class JAL(JTypeInstruction):
    def __init__(self, rd: int, imm: int):
        super().__init__(rd, imm, mnemonic="jal")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        # NOTE: Actually sets the pc to (pc+imm-4) because the simulation always increases the pc by 4 after execution
        """x[rd]=pc+4; pc+=sext(imm)"""
        architectural_state.register_file.registers[self.rd] = fixedint.UInt32(
            architectural_state.program_counter + 4
        )
        architectural_state.program_counter += self.imm - self.length
        architectural_state.performance_metrics.procedure_count += 1
        return architectural_state


class FENCE(FenceTypeInstruction):
    def __init__(self):
        super().__init__(mnemonic="fence")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """fence(pred,succ)"""
        raise InstructionNotImplemented(mnemonic=self.mnemonic)


class CSRRW(CSRTypeInstruction):
    def __init__(self, rd: int, csr: int, rs1: int):
        super().__init__(rd, csr, rs1, mnemonic="csrrw")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = x[rs1]

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.read_word(self.csr)
        architectural_state.csr_registers.write_word(
            self.csr, architectural_state.register_file.registers[self.rs1]
        )

        return architectural_state


class CSRRS(CSRTypeInstruction):
    def __init__(self, rd: int, csr: int, rs1: int):
        super().__init__(rd, csr, rs1, mnemonic="csrrs")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = csr_register[csr] or x[rs1]

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        rs1_value = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.read_word(self.csr)
        temp = architectural_state.csr_registers.read_word(self.csr) | rs1_value
        architectural_state.csr_registers.write_word(self.csr, temp)

        return architectural_state


class CSRRC(CSRTypeInstruction):
    def __init__(self, rd: int, csr: int, rs1: int):
        super().__init__(rd, csr, rs1, mnemonic="csrrc")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = csr_register[csr] and not(x[rs1])

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        rs1_value = architectural_state.register_file.registers[self.rs1]
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.read_word(self.csr)
        temp = architectural_state.csr_registers.read_word(self.csr) & (~(rs1_value))
        architectural_state.csr_registers.write_word(self.csr, temp)

        return architectural_state


class CSRRWI(CSRITypeInstruction):
    def __init__(self, rd: int, csr: int, uimm: int):
        super().__init__(rd, csr, uimm, mnemonic="csrrwi")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = zext(uimm)

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.read_word(self.csr)
        architectural_state.csr_registers.write_word(
            self.csr, fixedint.UInt32(self.uimm)
        )

        return architectural_state


class CSRRSI(CSRITypeInstruction):
    def __init__(self, rd: int, csr: int, uimm: int):
        super().__init__(rd, csr, uimm, mnemonic="csrrsi")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = csr_register[csr] or zext(uimm)

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.read_word(self.csr)
        temp = architectural_state.csr_registers.read_word(self.csr) | fixedint.UInt32(
            self.uimm
        )
        architectural_state.csr_registers.write_word(self.csr, temp)

        return architectural_state


class CSRRCI(CSRITypeInstruction):
    def __init__(self, rd: int, csr: int, uimm: int):
        super().__init__(rd, csr, uimm, mnemonic="csrrci")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """x[rd] = zext(csr_register[csr]); csr_register[csr] = csr_register[csr] and not(zext(uimm))

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        architectural_state.register_file.registers[
            self.rd
        ] = architectural_state.csr_registers.read_word(self.csr)
        temp = architectural_state.csr_registers.read_word(self.csr) & (
            ~(fixedint.UInt32(self.uimm))
        )
        architectural_state.csr_registers.write_word(self.csr, temp)

        return architectural_state


# 'M' Standard Extension for Integer Multiplication and Division


class MUL(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="mul")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        Multiplication:
            x[rd] = x[rs1] * x[rs2]

        Places lower 32 bits in destination register

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = rs1 * rs2
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = int(left * right)
        return (None, result)


class MULH(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="mulh")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        Multiplication Higher:
            x[rd] = (x[rs1] s*s x[rs2]) >>s 32

            rs1 and rs2 are treated as signed

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = fixedint.UInt32(
            (int(fixedint.Int32(rs1)) * int(fixedint.Int32(rs2))) >> 32
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = int(fixedint.Int32(alu_in_1))
        right = int(fixedint.Int32(alu_in_2))
        result = left * right >> 32
        return (None, result)


class MULHU(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="mulhu")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        Multiplication Higher Unsigned:
            rd = x[rd] = (x[rs1] u*u x[rs2]) >>u 32

            rs1 and rs2 are treated as unsigned

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = fixedint.UInt32(
            (int(rs1) * int(rs2)) >> 32
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = alu_in_1
        right = alu_in_2
        result = left * right >> 32
        return (None, result)


class MULHSU(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="mulhsu")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        Multiplication Higher Signed Unsigned
            x[rd] = (x[rs1] s*u x[rs2]) >>s 32

            rs1 treated as signed number, rs2 treated as unsigned number

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = fixedint.UInt32(
            (int(fixedint.Int32(rs1)) * int(rs2)) >> 32
        )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = int(fixedint.Int32(alu_in_1))
        right = alu_in_2
        result = left * right >> 32
        return (None, result)


class DIV(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="div")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        Division
            x[rd] = x[rs1] /s x[rs2]

            signed integer division

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs2 == 0:
            architectural_state.register_file.registers[self.rd] = fixedint.UInt32(-1)
        else:
            architectural_state.register_file.registers[self.rd] = fixedint.UInt32(
                (int(int(fixedint.Int32(rs1)) / int(fixedint.Int32(rs2))))
            )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = int(fixedint.Int32(alu_in_1))
        right = int(fixedint.Int32(alu_in_2))
        result = -1 if right == 0 else int(left / right)
        return (None, result)


class DIVU(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="divu")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        Division Unsigned
            x[rd] = x[rs1] /u x[rs2]

            unsigned integer division

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs2 == 0:
            architectural_state.register_file.registers[self.rd] = fixedint.UInt32(-1)
        else:
            architectural_state.register_file.registers[self.rd] = rs1 // rs2
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = -1 if right == 0 else int(left // right)
        return (None, result)


class REM(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="rem")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        Remain
            x[rd] = x[rs1] %s x[rs2]

            signed remainder

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs2 == 0:
            architectural_state.register_file.registers[self.rd] = rs1
        else:
            n = int(fixedint.Int32(rs1))
            b = int(fixedint.Int32(rs2))
            architectural_state.register_file.registers[self.rd] = fixedint.UInt32(
                (n - int(n / b) * b)
            )
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = int(fixedint.Int32(alu_in_1))
        right = int(fixedint.Int32(alu_in_2))
        result = left if right == 0 else left - int(left / right) * right
        return (None, result)


class REMU(RTypeInstruction):
    def __init__(self, rd: int, rs1: int, rs2: int):
        super().__init__(rd, rs1, rs2, mnemonic="remu")

    def behavior(
        self, architectural_state: RiscvArchitecturalState
    ) -> RiscvArchitecturalState:
        """
        Remain
            x[rd] = x[rs1] %u x[rs2]

            unsigned remainder

        Args:
            architectural_state

        Returns:
            architectural_state
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        if rs2 == 0:
            architectural_state.register_file.registers[self.rd] = rs1
        else:
            architectural_state.register_file.registers[self.rd] = rs1 % rs2
        return architectural_state

    def alu_compute(self, alu_in_1: Optional[int], alu_in_2: Optional[int]):
        assert alu_in_1 is not None
        assert alu_in_2 is not None
        left = fixedint.UInt32(alu_in_1)
        right = fixedint.UInt32(alu_in_2)
        result = left if right == 0 else int(left % right)
        return (None, result)


# Used by the parser to instantiate instructions.
instruction_map: dict[str, Type[RiscvInstruction]] = {
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
    "mul": MUL,
    "mulh": MULH,
    "mulhu": MULHU,
    "mulhsu": MULHSU,
    "div": DIV,
    "divu": DIVU,
    "rem": REM,
    "remu": REMU,
}
