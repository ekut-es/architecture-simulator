from fixedint import UInt8, UInt16, UInt32

from architecture_simulator.uarch.memory.base_cache_memory_system import (
    BaseCacheMemorySystem,
)
from architecture_simulator.util.integer_manipulation import (
    byte_into_block,
    halfword_into_block,
    word_into_block,
)

from architecture_simulator.uarch.memory.cache import Cache, CacheRepr
from architecture_simulator.uarch.memory.decoded_address import DecodedAddress
from architecture_simulator.uarch.memory.memory import Memory
from architecture_simulator.uarch.memory.replacement_strategies import (
    ReplacementStrategy,
    LRU,
)
from architecture_simulator.uarch.riscv.riscv_performance_metrics import (
    RiscvPerformanceMetrics,
)


class WriteThroughMemorySystem(BaseCacheMemorySystem):
    def __init__(
        self,
        memory: Memory,
        num_index_bits: int,
        num_block_bits: int,
        associativity: int,
        performance_metrics: RiscvPerformanceMetrics,
        miss_penality: int = 0,
        replacement_strategy: str = "lru",
    ) -> None:
        super().__init__(
            memory,
            num_index_bits,
            num_block_bits,
            associativity,
            performance_metrics,
            miss_penality,
            replacement_strategy,
        )

    def write_byte(
        self, address: int, value: UInt8, directly_write_to_lower_memory: bool = False
    ) -> None:
        decoded_address = self._decode_address(address)

        # Omit any cache related simulation
        if directly_write_to_lower_memory:
            self.memory.write_byte(address, value)
            return None

        block_values = self.cache.read_block(decoded_address)
        hit = block_values is not None
        self.hits += int(hit)
        if not hit:
            self.performance_metrics.cycles += self.miss_penality
        self.accesses += 1

        if block_values is not None:
            block_values = byte_into_block(decoded_address, block_values, value)
            self.cache.write_block(decoded_address, block_values)
        self.memory.write_byte(address, value)

    def write_halfword(
        self, address: int, value: UInt16, directly_write_to_lower_memory: bool = False
    ) -> None:
        decoded_address = self._decode_address(address)

        # Omit any cache related simulation
        if directly_write_to_lower_memory:
            self.memory.write_halfword(address, value)
            return None

        block_values = self.cache.read_block(decoded_address)
        hit = block_values is not None
        self.hits += int(hit)
        if not hit:
            self.performance_metrics.cycles += self.miss_penality
        self.accesses += 1

        if block_values is not None:
            block_values = halfword_into_block(decoded_address, block_values, value)
            self.cache.write_block(decoded_address, block_values)
        self.memory.write_halfword(address, value)

    def write_word(
        self, address: int, value: UInt32, directly_write_to_lower_memory: bool = False
    ) -> None:
        decoded_address = self._decode_address(address)

        # Omit any cache related simulation
        if directly_write_to_lower_memory:
            self.memory.write_word(address, value)
            return None

        block_values = self.cache.read_block(decoded_address)
        hit = block_values is not None
        self.hits += int(hit)
        if not hit:
            self.performance_metrics.cycles += self.miss_penality
        self.accesses += 1

        if block_values is not None:
            block_values = word_into_block(decoded_address, block_values, value)
            self.cache.write_block(decoded_address, block_values)
        self.memory.write_word(address, value)

    def _read_block(self, decoded_address: DecodedAddress) -> tuple[list[UInt32], bool]:
        block_values = self.cache.read_block(decoded_address)
        hit = block_values is not None
        if block_values is None:
            block_values = self._read_block_from_memory(decoded_address)
            self.cache.write_block(decoded_address, block_values)
        return block_values, hit
