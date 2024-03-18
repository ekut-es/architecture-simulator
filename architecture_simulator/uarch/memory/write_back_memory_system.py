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


class WriteBackMemorySystem(BaseCacheMemorySystem):
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

        # Cache Miss -> read block from memory
        if block_values is None:
            block_values = self._read_block_from_memory(decoded_address)

        # Place the byte to write into block and write to cache
        block_values = byte_into_block(decoded_address, block_values, value)
        _, displaced_block = self.cache.write_block(decoded_address, block_values)

        # Displaced block -> write back
        if displaced_block is not None:
            db_addr, db_block = displaced_block
            self._write_block_to_memory(db_addr, db_block)

        self.hits += int(hit)
        self.last_was_hit = hit
        if not hit:
            self.performance_metrics.cycles += self.miss_penality
        self.accesses += 1

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

        # Cache Miss -> read block from memory
        if block_values is None:
            block_values = self._read_block_from_memory(decoded_address)

        # Place the byte to write into block and write to cache
        block_values = halfword_into_block(decoded_address, block_values, value)
        _, displaced_block = self.cache.write_block(decoded_address, block_values)

        # Displaced block -> write back
        if displaced_block is not None:
            db_addr, db_block = displaced_block
            self._write_block_to_memory(db_addr, db_block)

        self.hits += int(hit)
        self.last_was_hit = hit
        if not hit:
            self.performance_metrics.cycles += self.miss_penality
        self.accesses += 1

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

        # Cache Miss -> read block from memory
        if block_values is None:
            block_values = self._read_block_from_memory(decoded_address)

        # Place the byte to write into block and write to cache
        block_values = word_into_block(decoded_address, block_values, value)
        _, displaced_block = self.cache.write_block(decoded_address, block_values)

        # Displaced block -> write back
        if displaced_block is not None:
            db_addr, db_block = displaced_block
            self._write_block_to_memory(db_addr, db_block)

        self.hits += int(hit)
        self.last_was_hit = hit
        if not hit:
            self.performance_metrics.cycles += self.miss_penality
        self.accesses += 1

    def _write_block_to_memory(
        self, decoded_address: DecodedAddress, block: list[UInt32]
    ) -> None:
        for i, word in enumerate(block):
            self.memory.write_word(decoded_address.block_alinged_address + 4 * i, word)

    def _read_block(self, decoded_address: DecodedAddress) -> tuple[list[UInt32], bool]:
        block_values = self.cache.read_block(decoded_address)
        hit = block_values is not None
        if block_values is None:
            block_values = self._read_block_from_memory(decoded_address)
            h, displaced_block = self.cache.write_block(decoded_address, block_values)
            if displaced_block is not None:
                db_addr, db_block = displaced_block
                self._write_block_to_memory(db_addr, db_block)
        # Probabily differentiate whether you had to write back a dirty block or not
        return block_values, hit
