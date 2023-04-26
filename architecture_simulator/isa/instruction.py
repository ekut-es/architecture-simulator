from dataclasses import dataclass

from ..uarch.architectural_state import ArchitecturalState


@dataclass
class Instruction:
    mnemonic: str

    def behavior(self, architectural_state: ArchitecturalState):
        pass
