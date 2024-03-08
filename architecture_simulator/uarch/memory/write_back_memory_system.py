from fixedint import UInt8, UInt16, UInt32

from architecture_simulator.uarch.memory.memory_system import MemorySystem
from architecture_simulator.util.integer_manipulation import (
    byte_from_block,
    halfword_from_block,
    word_from_block,
    byte_into_block,
    halfword_into_block,
    word_into_block,
)

from architecture_simulator.uarch.memory.cache import Cache, CacheRepr
from architecture_simulator.uarch.memory.decoded_address import DecodedAddress
from architecture_simulator.uarch.memory.memory import Memory
from typing import Type
from architecture_simulator.uarch.memory.replacement_strategies import (
    ReplacementStrategy,
    LRU,
)


class WriteBackMemorySystem(MemorySystem):
    def __init__(
        self,
        memory: Memory,
        num_index_bits: int,
        num_block_bits: int,
        associativity: int,
        replacement_strategy: Type[ReplacementStrategy] = LRU,
    ) -> None:
        # TODO: check that num_index_bits, num_block_bits, associativity have legal values
        self.cache = Cache[UInt32](
            num_index_bits=num_index_bits,
            num_block_bits=num_block_bits,
            associativity=associativity,
            replacement_strategy=replacement_strategy,
        )

        self.replacement_strategy = replacement_strategy

        self.num_index_bits = num_index_bits
        self.num_block_bits = num_block_bits
        self.associativity = associativity

        self.hits = 0
        self.accesses = 0
        self.memory = memory

    def read_byte(self, address: int, update_statistics: bool = True) -> UInt8:
        decoded_address = self._decode_address(address)
        block_values, hit = self._read_block(decoded_address)
        if update_statistics:
            self.accesses += 1
            self.hits += int(hit)
        return byte_from_block(decoded_address, block_values)

    def read_halfword(self, address: int, update_statistics: bool = True) -> UInt16:
        decoded_address = self._decode_address(address)
        block_values, hit = self._read_block(decoded_address)
        if update_statistics:
            self.accesses += 1
            self.hits += int(hit)
        return halfword_from_block(decoded_address, block_values)

    def read_word(self, address: int, update_statistics: bool = True) -> UInt32:
        decoded_address = self._decode_address(address)
        block_values, hit = self._read_block(decoded_address)
        if update_statistics:
            self.accesses += 1
            self.hits += int(hit)
        return word_from_block(decoded_address, block_values)

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

    def _read_block_from_memory(self, decoded_address: DecodedAddress) -> list[UInt32]:
        return [
            self.memory.read_word(decoded_address.block_alinged_address + 4 * i)
            for i in range(self.cache.num_words_in_block)
        ]

    def _decode_address(self, address: int) -> DecodedAddress:
        return DecodedAddress(
            self.cache.num_index_bits, self.cache.num_block_bits, address
        )

    def get_cache_stats(self) -> dict[str, str]:
        return {"hits": str(self.hits), "accesses": str(self.accesses)}

    def reset(self) -> None:
        self.cache = Cache[UInt32](
            num_index_bits=self.num_index_bits,
            num_block_bits=self.num_block_bits,
            associativity=self.associativity,
            replacement_strategy=self.replacement_strategy,
        )
        self.memory.reset()

    def get_address_range(self) -> range:
        return self.memory.get_address_range()

    def wordwise_repr(self) -> dict[int, tuple[str, str, str, str]]:
        return self.memory.wordwise_repr()

    def cache_repr(self) -> CacheRepr:
        return self.cache.get_repr()
