from dataclasses import dataclass, field
from fixedint import MutableUInt16

from architecture_simulator.uarch.memory import Memory


@dataclass
class ToyArchitecturalState:
    program_counter: MutableUInt16 = field(default_factory=lambda: MutableUInt16(0))
    accu: MutableUInt16 = field(default_factory=lambda: MutableUInt16(0))
    # 13 bit addresses because the Memory class is byte addressed but the toy processor is half word addressed
    data_memory: Memory = field(
        default_factory=lambda: Memory(address_length=13, min_bytes=2**11)
    )

    def load(self, address: int) -> MutableUInt16:
        # Shift by 1 bit because the Memory class is byte addressed but the toy processor is half word addressed
        byte_aligned_address = address << 1
        return self.data_memory.load_halfword(address=byte_aligned_address)

    def store(self, address: int, value: MutableUInt16):
        # Shift by 1 bit because the Memory class is byte addressed but the toy processor is half word addressed
        byte_aligned_address = address << 1
        self.data_memory.store_halfword(address=byte_aligned_address, value=value)

    def increment_pc(self):
        self.program_counter += MutableUInt16(1)
