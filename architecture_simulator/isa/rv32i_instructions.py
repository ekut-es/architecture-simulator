# from ctypes import c_int32, c_uint32, c_int8, c_int16, c_uint8, c_uint16

from .instruction_types import RTypeInstruction, CSRTypeInstruction, CSRITypeInstruction
from ..uarch.architectural_state import ArchitecturalState

import fixedint

# todo: use ctypes


class ADD(RTypeInstruction):
    def __init__(self, rs1: int, rs2: int, rd: int):
        super().__init__(rs1, rs2, rd, mnemonic="add")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        # rd = rs1 + rs2
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = rs1 + rs2
        return architectural_state


class SUB(RTypeInstruction):
    def __init__(self, rs1: int, rs2: int, rd: int):
        super().__init__(rs1, rs2, rd, mnemonic="add")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        """rd = rs1 - rs2

        Args:
            architectural_state (ArchitecturalState): _description_

        Returns:
            ArchitecturalState: _description_
        """
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = rs1 - rs2
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
    def __init__(self, rd: int, csr: int, imm: int):
        super().__init__(rd, csr, imm, mnemonic="csrrci")

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


instruction_map = {"add": ADD, "sub": SUB, "csrrw": CSRRW, "csrrs": CSRRS, "csrrc": CSRRC, "csrrwi": CSRRWI, "csrrsi": CSRRSI, "csrrci": CSRRSI}
