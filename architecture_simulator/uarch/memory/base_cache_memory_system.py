from fixedint import UInt8, UInt16, UInt32

from architecture_simulator.uarch.memory.memory_system import MemorySystem
from architecture_simulator.util.integer_manipulation import (
    byte_from_block,
    halfword_from_block,
    word_from_block,
)

from architecture_simulator.uarch.memory.cache import Cache, CacheRepr
from architecture_simulator.uarch.memory.decoded_address import DecodedAddress
from architecture_simulator.uarch.memory.memory import Memory
from architecture_simulator.uarch.memory.replacement_strategies import (
    ReplacementStrategy,
    LRU,
    PLRU,
)
from architecture_simulator.uarch.riscv.riscv_performance_metrics import (
    RiscvPerformanceMetrics,
)
from abc import abstractmethod


class BaseCacheMemorySystem(MemorySystem):
    """
    Implements parts of the MemorySystem class that are shared in WB and WT cache memory systems.
    """

    def __init__(
        self,
        memory: Memory,
        num_index_bits: int,
        num_block_bits: int,
        associativity: int,
        performance_metrics: RiscvPerformanceMetrics,
        miss_penality: int,
        replacement_strategy: str,
    ) -> None:
        # TODO: check that num_index_bits, num_block_bits, associativity have legal values
        self.replacement_strategy_class: type[ReplacementStrategy] = LRU if replacement_strategy == "lru" else PLRU  # type: ignore[type-abstract]
        self.cache = Cache[UInt32](
            num_index_bits=num_index_bits,
            num_block_bits=num_block_bits,
            associativity=associativity,
            replacement_strategy=self.replacement_strategy_class,
        )

        self.num_index_bits = num_index_bits
        self.num_block_bits = num_block_bits
        self.associativity = associativity

        self.performance_metrics = performance_metrics
        self.miss_penality = miss_penality
        self.hits = 0
        self.accesses = 0
        self.memory = memory
        self.last_was_hit = False

    def read_byte(self, address: int, update_statistics: bool = True) -> UInt8:
        decoded_address = self._decode_address(address)
        block_values, hit = self._read_block(decoded_address)
        if update_statistics:
            self.accesses += 1
            self.hits += int(hit)
            self.last_was_hit = hit
            if not hit:
                self.performance_metrics.cycles += self.miss_penality
        return byte_from_block(decoded_address, block_values)

    def read_halfword(self, address: int, update_statistics: bool = True) -> UInt16:
        decoded_address = self._decode_address(address)
        block_values, hit = self._read_block(decoded_address)
        if update_statistics:
            self.accesses += 1
            self.hits += int(hit)
            self.last_was_hit = hit
            if not hit:
                self.performance_metrics.cycles += self.miss_penality
        return halfword_from_block(decoded_address, block_values)

    def read_word(self, address: int, update_statistics: bool = True) -> UInt32:
        decoded_address = self._decode_address(address)
        block_values, hit = self._read_block(decoded_address)
        if update_statistics:
            self.accesses += 1
            self.hits += int(hit)
            self.last_was_hit = hit
            if not hit:
                self.performance_metrics.cycles += self.miss_penality
        return word_from_block(decoded_address, block_values)

    def _read_block_from_memory(self, decoded_address: DecodedAddress) -> list[UInt32]:
        return [
            self.memory.read_word(decoded_address.block_alinged_address + 4 * i)
            for i in range(self.cache.num_words_in_block)
        ]

    def _decode_address(self, address: int) -> DecodedAddress:
        return DecodedAddress(
            self.cache.num_index_bits, self.cache.num_block_bits, address
        )

    def get_cache_stats(self) -> dict[str, str | bool]:
        return {
            "hits": str(self.hits),
            "accesses": str(self.accesses),
            "last_hit": self.last_was_hit,
        }

    def reset(self) -> None:
        self.cache = Cache[UInt32](
            num_index_bits=self.num_index_bits,
            num_block_bits=self.num_block_bits,
            associativity=self.associativity,
            replacement_strategy=self.replacement_strategy_class,
        )
        self.memory.reset()

    def get_address_range(self) -> range:
        return self.memory.get_address_range()

    def wordwise_repr(self) -> dict[int, tuple[str, str, str, str]]:
        return self.memory.wordwise_repr()

    def cache_repr(self) -> CacheRepr:
        return self.cache.get_repr()

    @abstractmethod
    def _read_block(self, decoded_address: DecodedAddress) -> tuple[list[UInt32], bool]:
        raise NotImplementedError
