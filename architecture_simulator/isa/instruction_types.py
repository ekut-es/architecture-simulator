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
        super().__init__(**args)
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm
