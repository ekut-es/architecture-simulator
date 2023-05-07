from dataclasses import dataclass

from architecture_simulator.uarch.architectural_state import ArchitecturalState


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


class STypeInstruction(Instruction):
    def __init__(self, rs1: int, rs2: int, imm: int, **args):
        super().__init__(**args)
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm


class UTypeInstruction(Instruction):
    def __init__(self, rd: int, imm: int, **args):
        super().__init__(**args)
        self.rd = rd
        self.imm = imm


class JTypeInstruction(Instruction):
    def __init__(self, rd: int, imm: int, **args):
        super().__init__(**args)
        self.rd = rd
        self.imm = imm


class fence(Instruction):
    def __init__(self, **args):
        super().__init__(**args)
