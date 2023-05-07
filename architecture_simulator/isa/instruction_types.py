from dataclasses import dataclass

from ..uarch.architectural_state import ArchitecturalState


@dataclass
class Instruction:
    mnemonic: str

    def behavior(self, architectural_state: ArchitecturalState):
        pass


class RTypeInstruction(Instruction):
    def __init__(self, rs1: int, rs2: int, rd: int, **args):
        super().__init__(**args)
        self.rs1 = rs1
        self.rs2 = rs2
        self.rd = rd


class ITypeInstruction(Instruction):
    def __init__(self, rd: int, rs1: int, imm: int, **args):
        """Create a I-Type instruction

        Args:
            rd (int): destination register
            rs1 (int): source register 1
            imm (int): offset to be further progressed by the instruction
        """
        if imm < -2048 or 2047 < imm:
            raise ValueError(
                "I-Type Instruction immediate values have to be in range(-2048, 2048). Given immediate was "
                + str(imm)
            )
        super().__init__(**args)
        self.rd = rd
        self.rs1 = rs1
        self.imm = imm
