from .instruction_types import RTypeInstruction
from ..uarch.architectural_state import ArchitecturalState


class ADD(RTypeInstruction):
    def __init__(self, rs1: int, rs2: int, rd: int):
        super().__init__(rs1, rs2, rd, mnemonic="add")

    def behavior(self, architectural_state: ArchitecturalState) -> ArchitecturalState:
        # rd = rs1 + rs2
        rs1 = architectural_state.register_file.registers[self.rs1]
        rs2 = architectural_state.register_file.registers[self.rs2]
        architectural_state.register_file.registers[self.rd] = rs1 + rs2
        return architectural_state


instruction_map = {"add": ADD}
