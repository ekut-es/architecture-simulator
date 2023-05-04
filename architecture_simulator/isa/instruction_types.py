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


class BTypeInstruction(Instruction):
    def __init__(self, rs1: int, rs2: int, imm: int, **args):
        """Create a B-Type instruction

        Args:
            rs1 (int): source register 1
            rs2 (int): source register 2
            imm (int): offset to be added to the pc. Needs to be a 12 bit signed integer. Interpreted as multiple of 2 bytes.
        """
        if -2048 < imm or 2047 < imm:
            raise ValueError(
                "B-Type Instruction immediate values have to be in range(-2048, 2048). Given immediate was "
                + imm
            )
        super().__init__(**args)
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm
