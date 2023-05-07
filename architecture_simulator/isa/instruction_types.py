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
