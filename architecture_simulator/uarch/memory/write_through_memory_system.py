from fixedint import UInt8, UInt16, UInt32, UInt8, UInt16, UInt32

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


class WriteThroughMemorySystem(MemorySystem):
    def __init__(
        self,
        memory: Memory,
        num_index_bits: int,
        num_block_bits: int,
        associativity: int,
    ) -> None:
        # TODO: check that num_index_bits, num_block_bits, associativity have legal values
        self.cache = Cache[UInt32](
            num_index_bits=num_index_bits,
            num_block_bits=num_block_bits,
            associativity=associativity,
        )

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

    def write_byte(self, address: int, value: UInt8) -> None:
        decoded_address = self._decode_address(address)
        block_values = self.cache.read_block(decoded_address)
        hit = block_values is not None
        self.hits += int(hit)
        self.accesses += 1
        if block_values is not None:
            block_values = byte_into_block(decoded_address, block_values, value)
            self.cache.write_block(decoded_address, block_values)
        self.memory.write_byte(address, value)

    def write_halfword(self, address: int, value: UInt16) -> None:
        decoded_address = self._decode_address(address)
        block_values = self.cache.read_block(decoded_address)
        hit = block_values is not None
        self.hits += int(hit)
        self.accesses += 1
        if block_values is not None:
            block_values = halfword_into_block(decoded_address, block_values, value)
            self.cache.write_block(decoded_address, block_values)
        self.memory.write_halfword(address, value)

    def write_word(self, address: int, value: UInt32) -> None:
        decoded_address = self._decode_address(address)
        block_values = self.cache.read_block(decoded_address)
        hit = block_values is not None
        self.hits += int(hit)
        self.accesses += 1
        if block_values is not None:
            block_values = word_into_block(decoded_address, block_values, value)
            self.cache.write_block(decoded_address, block_values)
        self.memory.write_word(address, value)

    def wordwise_repr(self) -> dict[int, tuple[str, str, str, str]]:
        return self.memory.wordwise_repr()

    def reset(self) -> None:
        self.cache = Cache[UInt32](
            num_index_bits=self.num_index_bits,
            num_block_bits=self.num_block_bits,
            associativity=self.associativity,
        )
        self.memory.reset()

    def cache_repr(self) -> CacheRepr:
        return self.cache.get_repr()

    def get_cache_stats(self) -> dict[str, str]:
        return {"hits": str(self.hits), "accesses": str(self.accesses)}

    def _decode_address(self, address: int) -> DecodedAddress:
        return DecodedAddress(
            self.cache.num_index_bits, self.cache.num_block_bits, address
        )

    def _read_block(self, decoded_address: DecodedAddress) -> tuple[list[UInt32], bool]:
        block_values = self.cache.read_block(decoded_address)
        hit = block_values is not None
        if block_values is None:
            block_values = self._read_block_from_memory(decoded_address)
            self.cache.write_block(decoded_address, block_values)
        return block_values, hit

    def _read_block_from_memory(self, decoded_address: DecodedAddress) -> list[UInt32]:
        return [
            self.memory.read_word(decoded_address.block_alinged_address + 4 * i)
            for i in range(self.cache.num_words_in_block)
        ]
