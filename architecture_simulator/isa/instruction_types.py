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
        if imm < -2048 or 2047 < imm:
            raise ValueError(
                "STypeInstruction can only take 12 bit immediates. Given immediate was "
                + str(imm)
            )
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm


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


class fence(Instruction):
    def __init__(self, **args):
        super().__init__(**args)
