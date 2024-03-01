from fixedint import UInt32
from typing import Optional

from architecture_simulator.uarch.memory.decoded_address import DecodedAddress
from architecture_simulator.uarch.memory.replacement_strategies import (
    ReplacementStrategy,
    LRU,
)


class CacheBlock:
    """A class for simulating a block inside a cache that can potentially store multiple bytes."""

    def __init__(self, block_size: int) -> None:
        """Creates a cache block.

        Args:
            block_size (int): The number of bytes that live inside the cache block. Must be a power of 2.
        """
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
    ) -> None:

        self.num_index_bits = num_index_bits
        self.num_sets = 2**num_index_bits
        self.num_block_bits = num_block_bits
        self.num_words_in_block = 2**num_block_bits

        self.sets: list[CacheSet] = [
            CacheSet(associativity, num_block_bits, LRU(associativity))
            for _ in range(2**num_index_bits)
        ]

    def read_block(self, decoded_address: DecodedAddress) -> Optional[list[UInt32]]:
        return self.sets[decoded_address.cache_set_index].read(decoded_address)

    def write_block(
        self, decoded_address: DecodedAddress, block_values: list[UInt32]
    ) -> bool:
        return self.sets[decoded_address.cache_set_index].write(
            decoded_address, block_values
        )

    def contains(self, decoded_address: DecodedAddress) -> bool:
        return self.sets[decoded_address.cache_set_index].is_block_in_set(
            decoded_address
        )
