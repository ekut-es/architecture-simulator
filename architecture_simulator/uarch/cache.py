from fixedint import UInt32, UInt16, UInt8, MutableUInt32, MutableUInt16, MutableUInt8
from typing import Optional
from abc import ABC, abstractmethod

from architecture_simulator.uarch.memory import Memory


def select_bits(number: int, start: int, stop: int) -> int:
    return (number >> start) & ((2 ** (stop - start)) - 1)


def is_power_of_two(n: int) -> bool:
    return (n > 0) and ((n & (n - 1)) == 0)
    # TODO: Use everywhere instead of % 2 == 0


class DecodedAddress:
    """A class that contains a lot of information about an address that is relevant for caches,
    like the tag, the index and offsets.
    All this information depends on the width of the index and the number of bits used for the block offset.
    """

    def __init__(self, num_index_bits: int, num_block_bits: int, address: int) -> None:
        """Constructs a DecodedAddress object.

        Args:
            num_index_bits (int): The width of the index in bits.
            num_block_bits (int): The number of bits that are used for the block offset.
            address (int): The full address.
        """

        self.full_address: int = address
        """The full address"""

        self.tag: int = address >> (num_index_bits + num_block_bits + 2)
        """The tag"""

        self.cache_set_index: int = (address >> (num_block_bits + 2)) & (
            2**num_index_bits - 1
        )
        """The index"""

        self.word_alinged_address: int = address & 0xFFFFFFFC
        """The address, but with the lower two bits cleared."""

        self.byte_offset: int = address & 0x3
        """The index of the byte within the word."""

        self.block_alinged_address: int = (address >> (2 + num_block_bits)) << (
            2 + num_block_bits
        )
        """The address, but with the bits for the block and byte offsets cleared."""

        self.block_offset: int = (address >> 2) & (2**num_block_bits - 1)
        """The index of the block within its set."""


class ReplacementStrategy(ABC):
    """A class that stores and updates the state of the replacement strategy for a set of the cache."""

    def __init__(self, associativity: int) -> None:
        self.associativity = associativity

    @abstractmethod
    def access(self, index: int) -> None:
        """Informs the replacement strategy that an element has been accessed.

        Args:
            index (int): The index of the block inside the set that was accessed.
        """

    @abstractmethod
    def get_next_to_replace(self) -> int:
        """Returns the index of the block that shall be replaced next.

        Returns:
            int: The index of the block inside the set to be replaced next.
        """


class LRU(ReplacementStrategy):
    def __init__(self, associativity: int) -> None:
        super().__init__(associativity)
        self.lru = [i for i in range(associativity)]

    def access(self, index: int) -> None:
        self.lru.remove(index)
        self.lru.append(index)

    def get_next_to_replace(self) -> int:
        return self.lru[0]


class CacheBlock:
    """A class for simulating a block inside a cache that can potentially store multiple bytes."""

    def __init__(self, block_size: int) -> None:
        """Creates a cache block.

        Args:
            block_size (int): The number of bytes that live inside the cache block. Must be a power of 2.
        """
        # TODO: Fix that ? assert is_power_of_two(block_size)
        self.block_size = block_size
        self.values: list[UInt32] = [UInt32(0) for _ in range(block_size)]
        self.valid_bit: bool = False
        self.tag: int = 0

    def write(self, values: list[UInt32], tag: int) -> None:
        """Writes the given values to the block and marks the block as valid

        Args:
            values (list[UInt32]): A list of words that will be written to the block. Must have the correct length (self.block_size).
        """
        assert len(values) == self.block_size
        self.values = values
        self.valid_bit = True
        self.tag = tag


class CacheSet:
    """A class for simulation a potentially associative set of a cache.
    Provides methods for reading and writing whole blocks of words (block size can be configured).
    """

    # is_in_set
    # read (addresse zu lesen, wert an den der HS glaubt zum allocate wenn nicht im Cache) -> wert, hit? Optional[(addresse, wert) (verängt)]
    # write (addresse zu beschreiben, wert zu beschreiben) -> hit?, Optional[list[(adresse, wert) zum in HS schreiben] (entweder verängtes oder write no allocate)
    def __init__(
        self,
        associativity: int,
        block_bits: int,
        replacement_strategy: ReplacementStrategy,
    ) -> None:
        # TODO: Fix ? assert block_size % 2 == 0
        # TODO: Fix ? assert associativity % 2 == 0
        self.block_bits = block_bits
        self.blocks = [CacheBlock(2**block_bits) for _ in range(associativity)]
        self.replacement_strategy = replacement_strategy

    #                       was i memory steht falls du es nicht hast und reinschreiben musst
    def read(self, address: DecodedAddress) -> Optional[list[UInt32]]:
        """Tries to read the value from the given address.

        Args:
            address (DecodedAddress): Full memory address.

        Returns:
            Optional[UInt32]: Returns the full block in case of a read-hit, or None in case of a read-miss.
        """
        block_index = self.get_block_index(address)
        if block_index is not None:
            self.replacement_strategy.access(block_index)
            return self.blocks[block_index].values
        return None

    def write(self, address: DecodedAddress, block_values: list[UInt32]) -> bool:
        """Writes the given block to the set.

        Args:
            address (DecodedAddress): Full memory address.
            block_values (list[UInt32]): The block values to write.

        Returns:
            bool: Whether it was a write-hit.
        """
        block_index = self.get_block_index(address)
        is_hit = block_index is not None
        if block_index is None:
            block_index = self.replacement_strategy.get_next_to_replace()
        self.blocks[block_index].write(block_values, address.tag)
        self.replacement_strategy.access(block_index)
        return is_hit

    def is_block_in_set(self, address: DecodedAddress) -> bool:
        """Returns whether the address is stored in the set.

        Args:
            address (DecodedAddress): Full memory address.

        Returns:
            bool: Whether the address is stored in the set ('cache hit')
        """
        return self.get_block_index(address) is not None

    def get_block_index(self, address: DecodedAddress) -> Optional[int]:
        """Checks whether the address is in the set and returns the index of the block if it is.

        Args:
            address (DecodedAddress): Full memory address.

        Returns:
            Optional[int]: Returns the index of the block, if it is stored in the set, or None if it is not.
        """
        for block_index, block in enumerate(self.blocks):
            if (block.tag == address.tag) and block.valid_bit:
                return block_index
        return None


class Cache:
    def __init__(
        self,
        num_index_bits: int,
        num_block_bits: int,
        associativity: int,
        main_memory: Memory,
    ) -> None:

        # TODO: Check for legality of input

        self.num_index_bits = num_index_bits
        self.num_sets = 2**num_index_bits
        self.num_block_bits = num_block_bits
        self.num_words_in_block = 2**num_block_bits

        self.sets: list[CacheSet] = [
            CacheSet(associativity, num_block_bits, LRU(associativity))
            for _ in range(2**num_index_bits)
        ]

        self.main_memory = main_memory

    def write_byte(self, address: int, value: UInt8) -> bool:
        decoded_address = DecodedAddress(
            self.num_index_bits, self.num_block_bits, address
        )
        target_set = self.sets[decoded_address.cache_set_index]
        hit = target_set.is_block_in_set(decoded_address)
        self.main_memory.write_byte(address, MutableUInt8(value))
        if hit:
            block = self._read_block_data_from_main_memory(decoded_address)
            target_set.write(decoded_address, block)
        return hit

    def write_halfword(self, address: int, value: UInt16) -> bool:
        decoded_address = DecodedAddress(
            self.num_index_bits, self.num_block_bits, address
        )
        target_set = self.sets[decoded_address.cache_set_index]
        hit = target_set.is_block_in_set(decoded_address)
        self.main_memory.write_halfword(address, MutableUInt16(value))
        if hit:
            block = self._read_block_data_from_main_memory(decoded_address)
            target_set.write(decoded_address, block)
        return hit

    def write_word(self, address: int, value: UInt32) -> bool:
        decoded_address = DecodedAddress(
            self.num_index_bits, self.num_block_bits, address
        )
        target_set = self.sets[decoded_address.cache_set_index]
        hit = target_set.is_block_in_set(decoded_address)
        self.main_memory.write_word(address, MutableUInt32(value))
        if hit:
            block = self._read_block_data_from_main_memory(decoded_address)
            target_set.write(decoded_address, block)
        return hit

    def read_byte(self, address: int) -> tuple[UInt8, bool]:
        decoded_address = DecodedAddress(
            self.num_index_bits, self.num_block_bits, address
        )
        word, hit = self._read_word_from_anywhere(decoded_address)
        read_b = (int(word) >> (8 * decoded_address.byte_offset)) & 0xFF
        return (UInt8(read_b), hit)

    def read_halfword(self, address: int) -> tuple[UInt16, bool]:
        assert not address & 0x1  # TODO: Custom Error!
        decoded_address = DecodedAddress(
            self.num_index_bits, self.num_block_bits, address
        )
        word, hit = self._read_word_from_anywhere(decoded_address)
        read_hw = (int(word) >> (16 * decoded_address.byte_offset)) & 0xFFFF
        return (UInt16(read_hw), hit)

    def read_word(self, address: int) -> tuple[UInt32, bool]:
        assert not address & 0x3  # TODO: Cutom Error!
        decoded_address = DecodedAddress(
            self.num_index_bits, self.num_block_bits, address
        )
        return self._read_word_from_anywhere(decoded_address)

    def _read_word_from_anywhere(
        self, decoded_address: DecodedAddress
    ) -> tuple[UInt32, bool]:
        block_content = self.sets[decoded_address.cache_set_index].read(decoded_address)
        hit = block_content is not None
        if block_content is None:
            block_content = self._read_block_data_from_main_memory(decoded_address)
            self.sets[decoded_address.cache_set_index].write(
                decoded_address, block_content
            )
        word = block_content[decoded_address.block_offset]
        return (word, hit)

    def _read_block_data_from_main_memory(
        self, address: DecodedAddress
    ) -> list[UInt32]:
        return [
            UInt32(
                int(self.main_memory.read_word(address.block_alinged_address + 4 * i))
            )
            for i in range(self.num_words_in_block)
        ]
