from dataclasses import dataclass

from architecture_simulator.uarch.architectural_state import ArchitecturalState


@dataclass
class Instruction:
    mnemonic: str

    def behavior(self, architectural_state: ArchitecturalState):
        pass


class RTypeInstruction(Instruction):
    def __init__(self, rd: int, rs1: int, rs2: int, **args):
        super().__init__(**args)
        self.rs1 = rs1
        self.rs2 = rs2
        self.rd = rd

    def __repr__(self) -> str:
        return f"{self.mnemonic} x{self.rd}, x{self.rs1}, x{self.rs2}"


class CSRTypeInstruction(Instruction):
    """Create an I-Type instruction

    Args:
        rd (int): register destination
        csr (int): the control/status register's index
        rs1 (int): source register 1
    """

    def __init__(self, rd: int, csr: int, rs1: int, **args):
        super().__init__(**args)
        self.rd = rd
        self.csr = csr
        self.rs1 = rs1

    def __repr__(self) -> str:
        return f"{self.mnemonic} x{self.rd}, {hex(self.csr)}, x{self.rs1}"


class CSRITypeInstruction(Instruction):
    """Create an I-Type instruction

    Args:
        rd (int): register destination
        csr (int): the control/status register's index
        imm (int): immediate
    """

    def __init__(self, rd: int, csr: int, uimm: int, **args):
        super().__init__(**args)
        self.rd = rd
        self.csr = csr
        self.uimm = uimm

    def __repr__(self) -> str:
        return f"{self.mnemonic} x{self.rd}, {hex(self.csr)}, {self.uimm}"


class BTypeInstruction(Instruction):
    def __init__(self, rs1: int, rs2: int, imm: int, **args):
        """Create a B-Type instruction
        Note: These B-Type-Instructions will actually set the pc to 2*imm-4, because the simulator will always add 4 to the pc.

        Args:
            rs1 (int): source register 1
            rs2 (int): source register 2
            imm (int): offset to be added to the pc. Needs to be a 12 bit signed integer. Interpreted as multiple of 2 bytes.
        """
        if imm < -2048 or 2047 < imm:
            raise ValueError(
                "B-Type Instruction immediate values have to be in range(-2048, 2048). Given immediate was "
                + str(imm)
            )
        super().__init__(**args)
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm

    def __repr__(self) -> str:
        return f"{self.mnemonic} x{self.rs1}, x{self.rs2}, {self.imm*2}"


class STypeInstruction(Instruction):
    def __init__(self, rs1: int, rs2: int, imm: int, **args):
        super().__init__(**args)
        if imm < -2048 or 2047 < imm:
            raise ValueError(
                "STypeInstruction can only take 12 bit immediates. Given immediate was "
                + str(imm)
            )
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm

    def __repr__(self) -> str:
        return f"{self.mnemonic} x{self.rs2}, {self.imm}(x{self.rs1})"


class UTypeInstruction(Instruction):
    def __init__(self, rd: int, imm: int, **args):
        super().__init__(**args)
        if imm < -pow(2, 19) or pow(2, 19) - 1 < imm:
            raise ValueError(
                "UTypeInstruction can only take 20 bit immediates. Given immediate was "
                + str(imm)
            )
        self.rd = rd
        self.imm = imm

    def __repr__(self) -> str:
        return f"{self.mnemonic} x{self.rd}, {self.imm}"


class JTypeInstruction(Instruction):
    def __init__(self, rd: int, imm: int, **args):
        super().__init__(**args)
        if imm < -pow(2, 19) or pow(2, 19) - 1 < imm:
            raise ValueError(
                "JTypeInstruction can only take 20 bit immediates. Given immediate was "
                + str(imm)
            )
        self.rd = rd
        self.imm = imm

    def __repr__(self) -> str:
        return f"{self.mnemonic} x{self.rd}, {self.imm*2}"


class fence(Instruction):
    def __init__(self, **args):
        super().__init__(**args)

    # TODO: Change me, if Fence gets implemented
    # def __repr__(self) -> str:
    #    return f"{self.mnemonic}"


class ITypeInstruction(Instruction):
    def __init__(self, rd: int, rs1: int, imm: int, **args):
        """Create a I-Type instruction

        Args:
            imm (int): offset to be further progressed by the instruction
            rs1 (int): source register 1
            rd (int): destination register
        """
        super().__init__(**args)
        if imm < -2048 or 2047 < imm:
            raise ValueError(
                "ITypeInstruction can only take 12 bit immediates. Given immediate was "
                + str(imm)
            )
        self.imm = imm
        self.rs1 = rs1
        self.rd = rd

    def __repr__(self) -> str:
        from architecture_simulator.isa.rv32i_instructions import (
            LB,
            LH,
            LW,
            LBU,
            LHU,
            ECALL,
            EBREAK,
        )

        memory_instructions = (LB, LH, LW, LBU, LHU)
        e_instructions = (ECALL, EBREAK)
        if isinstance(self, memory_instructions):
            return f"{self.mnemonic} x{self.rd}, {self.imm}(x{self.rs1})"
        elif isinstance(self, e_instructions):
            return f"{self.mnemonic}"
        else:
            return f"{self.mnemonic} x{self.rd}, x{self.rs1}, {self.imm}"
