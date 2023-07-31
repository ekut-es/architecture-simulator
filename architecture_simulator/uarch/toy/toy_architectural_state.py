from dataclasses import dataclass, field
from fixedint import MutableUInt16

from .toy_memory import ToyMemory
from ..memory import InstructionMemory
from architecture_simulator.isa.toy.toy_instructions import ToyInstruction


@dataclass
class ToyArchitecturalState:
    program_counter: MutableUInt16 = field(default_factory=lambda: MutableUInt16(0))
    accu: MutableUInt16 = field(default_factory=lambda: MutableUInt16(0))
    # 13 bit addresses because the Memory class is byte addressed but the toy processor is half word addressed
    data_memory: ToyMemory = field(default_factory=ToyMemory)
    instruction_memory: InstructionMemory = field(
        default_factory=lambda: InstructionMemory[ToyInstruction](
            address_range=range(0, 1024)
        )
    )

    def increment_pc(self):
        self.program_counter += MutableUInt16(1)
