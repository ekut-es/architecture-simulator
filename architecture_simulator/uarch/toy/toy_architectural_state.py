from dataclasses import dataclass, field
from fixedint import MutableUInt16

from architecture_simulator.uarch.memory import Memory


@dataclass
class ToyArchitecturalState:
    program_counter: int = 0
    accu: MutableUInt16 = field(default_factory=MutableUInt16)
    data_memory: Memory = field(
        default_factory=lambda: Memory(address_length=12, min_bytes=2**10)
    )
