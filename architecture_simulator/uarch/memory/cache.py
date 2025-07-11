from typing import TypeVar, Generic, Optional, Type, Any
from architecture_simulator.uarch.memory.decoded_address import DecodedAddress
from architecture_simulator.uarch.memory.replacement_strategies import (
    ReplacementStrategy,
)
from architecture_simulator.util.integer_representations import (
    to_hex_str,
)

T = TypeVar("T")


class CacheOptions:
    """
    Configuration object for caches.
    """

    def __init__(
        self,
        enable: bool,
        num_index_bits: int,
        num_block_bits: int,
        associativity: int,
        cache_type: str,
        replacement_strategy: str,
        miss_penalty: int,
    ) -> None:
        self.enable = enable
        self.num_index_bits = num_index_bits
        self.num_block_bits = num_block_bits
        self.associativity = associativity
        self.cache_type = cache_type  # "wb" or "wt"
        self.replacement_strategy = replacement_strategy  # "lru" or "plru"
        self.miss_penalty = miss_penalty


class CacheBlockRepr(Generic[T]):
    """
    Representation object of a single cache block.
    """

    def __init__(
        self,
        valid_bit: bool,
        dirty_bit: bool,
        values: list[T],
        block_size: int,
        base_address: int,
        tag: int,
        tag_width: int,
    ) -> None:
        self.valid_bit = str(int(valid_bit))
        self.dirty_bit = str(int(dirty_bit))
        self.address_value_list = (
            [
                ((to_hex_str(base_address + i * 4, 32), str(entry)))
                for i, entry in enumerate(values)
            ]
            if valid_bit
            else [("", "") for _ in range(block_size)]
        )
        self.tag = ("0x" + to_hex_str(tag, tag_width)) if valid_bit else " " * tag_width


class CacheBlock(Generic[T]):
    """A class for simulating a block inside a cache that can potentially store multiple bytes."""

    def __init__(self, block_size: int) -> None:
        """Creates a cache block.

        Args:
            block_size (int): The number of bytes that live inside the cache block. Must be a power of 2.
        """
        self.block_size = block_size
        self.values: list[T] = []
        self.valid_bit: bool = False
        self.dirty_bit: bool = False
        self.decoded_address: DecodedAddress = DecodedAddress(0, 0, 0)

    def write(self, values: list[T], decoded_address: DecodedAddress) -> None:
        """Writes the given values to the block and marks the block as valid

        Args:
            values (list[T]): A list of words that will be written to the block. Must have the correct length (self.block_size).
            decoded_address (DecodedAddress): The full address to write to.
        """
        assert len(values) == self.block_size
        self.values = values
        self.valid_bit = True

        self.decoded_address = decoded_address

    def get_repr(self) -> CacheBlockRepr:
        return CacheBlockRepr(
            valid_bit=self.valid_bit,
            dirty_bit=self.dirty_bit,
            values=self.values,
            block_size=self.block_size,
            base_address=self.decoded_address.block_alinged_address,
            tag=self.decoded_address.tag,
            tag_width=self.decoded_address.num_tag_bits,
        )


class CacheSetRepr:
    """
    Representation object of a single cache set.
    """

    def __init__(
        self, index_str: str, blocks: list[CacheBlockRepr], replacement_status: Any
    ) -> None:
        self.index = index_str
        self.blocks = blocks
        self.replacement_status = replacement_status


class CacheSet(Generic[T]):
    """A class for simulation a potentially associative set of a cache.
    Provides methods for reading and writing whole blocks of words (block size can be configured).
    """

    def __init__(
        self,
        associativity: int,
        block_bits: int,
        replacement_strategy: ReplacementStrategy,
        index_str: str,
    ) -> None:
        self.block_bits = block_bits
        self.blocks = [CacheBlock[T](2**block_bits) for _ in range(associativity)]
        self.replacement_strategy = replacement_strategy
        self.index_str = index_str

    def read(self, address: DecodedAddress) -> Optional[list[T]]:
        """Tries to read the value from the given address.

        Args:
            address (DecodedAddress): Full memory address.

        Returns:
            Optional[list[T]]: Returns all block values in case of a read-hit, or None in case of a read-miss.
        """
        block_index = self.get_block_index(address)
        if block_index is not None:
            self.replacement_strategy.access(block_index)
            return self.blocks[block_index].values
        return None

    def write(
        self, address: DecodedAddress, block_values: list[T], write_access: bool
    ) -> tuple[bool, Optional[tuple[DecodedAddress, list[T]]]]:
        """Writes the given block to the set.

        Args:
            address (DecodedAddress): Full memory address.
            block_values (list[T]): The block values to write.

        Returns:
            tuple[bool, Optional[tuple[DecodedAddress, list[T]]]]: First element is whether it was a cache hit.
            The second value is None if nothing dirty was replaced.
            If a dirty entry was replaced, it is a tuple of the address and the values that were stored there.
        """
        block_index = self.get_block_index(address)
        if block_index is None:  # Not in Cache Case
            block_index = self.replacement_strategy.get_next_to_replace()
            block = self.blocks[block_index]
            replaced = None
            if block.dirty_bit:
                replaced = (block.decoded_address, block.values)
            block.dirty_bit = write_access  # Bugfix: Always set to True if write is issued by a store instruction because write back will not write that data to the memory on a write miss
            block.write(block_values, address)
            self.replacement_strategy.access(block_index)
            return False, replaced
        else:  # Already in Cache Case
            self.blocks[block_index].write(block_values, address)
            self.blocks[block_index].dirty_bit = True
            self.replacement_strategy.access(block_index)
            return True, None

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
            if block.valid_bit and (block.decoded_address.tag == address.tag):
                return block_index
        return None

    def get_repr(self) -> CacheSetRepr:
        return CacheSetRepr(
            self.index_str,
            [block.get_repr() for block in self.blocks],
            self.replacement_strategy.get_repr(),
        )


class CacheRepr:
    """
    Representation object of an entire cache.
    """

    def __init__(self, sets: list[CacheSetRepr]) -> None:
        self.sets = sets


class Cache(Generic[T]):
    """
    Generic cache object.
    """

    def __init__(
        self,
        num_index_bits: int,
        num_block_bits: int,
        associativity: int,
        replacement_strategy: Type[ReplacementStrategy],
    ) -> None:

        self.num_index_bits = num_index_bits
        self.num_sets = 2**num_index_bits
        self.num_block_bits = num_block_bits
        self.num_words_in_block = 2**num_block_bits

        self.sets: list[CacheSet[T]] = [
            CacheSet[T](
                associativity,
                num_block_bits,
                replacement_strategy(associativity),
                ("0x" + to_hex_str(i, self.num_index_bits)),
            )
            for i in range(2**num_index_bits)
        ]

    def read_block(self, decoded_address: DecodedAddress) -> Optional[list[T]]:
        """
        Reads block from cache.

        Parameters:
            decoded_address (DecodedAddress): Address to read from.

        Returns:
            Optional[list[T]]: cache block or None if not in cache.
        """
        return self.sets[decoded_address.cache_set_index].read(decoded_address)

    def write_block(
        self, decoded_address: DecodedAddress, block_values: list[T], write_access: bool
    ) -> tuple[bool, Optional[tuple[DecodedAddress, list[T]]]]:
        """
        Writes block to cache.

        Parameters:
            decoded_address (DecodedAddress): Address to write to.
            block_values (list[T]): Values to write.

        Returns:
            tuple[bool, Optional[tuple[DecodedAddress, list[T]]]]: hit, address and values of displaced cache block if necessary.
        """
        return self.sets[decoded_address.cache_set_index].write(
            decoded_address, block_values, write_access
        )

    def contains(self, decoded_address: DecodedAddress) -> bool:
        """
        Returns:
            bool: whether the block that belongs to the address is contained in the cache.
        """
        return self.sets[decoded_address.cache_set_index].is_block_in_set(
            decoded_address
        )

    def get_repr(self) -> CacheRepr:
        return CacheRepr([zet.get_repr() for zet in self.sets])
