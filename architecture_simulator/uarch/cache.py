from fixedint import UInt32, UInt16, UInt8
from typing import Optional

from architecture_simulator.uarch.memory import Memory


def select_bits(number: int, start: int, stop: int) -> int:
    return (number >> start) & ((2 ** (stop - start)) - 1)


def is_power_of_two(n: int) -> bool:
    return (n > 0) and ((n & (n - 1)) == 0)
    # TODO: Use everywhere instead of % 2 == 0


class CacheBlock:
    """A class for simulating a block inside a cache that can potentially store multiple bytes."""

    def __init__(self, block_size: int) -> None:
        """Creates a cache block.

        Args:
            block_size (int): The number of bytes that live inside the cache block. Must be a power of 2.
        """
        assert is_power_of_two(block_size)
        self.block_size = block_size
        self.values: list[UInt32] = [UInt32(0) for _ in range(block_size)]
        self.valid_bit: bool = False
        self.tag: int = 0

    def write(self, values: list[UInt32]) -> None:
        """Writes the given values to the block and marks the block as valid

        Args:
            values (list[UInt32]): A list of words that will be written to the block. Must have the correct length (self.block_size).
        """
        assert len(values) == self.block_size
        self.values = values
        self.valid_bit = True


class CacheSet:
    """A class for simulation a potentially associative set of a cache.
    Provides methods for reading and writing whole blocks of words (block size can be configured).
    """

    # is_in_set
    # read (addresse zu lesen, wert an den der HS glaubt zum allocate wenn nicht im Cache) -> wert, hit? Optional[(addresse, wert) (verängt)]
    # write (addresse zu beschreiben, wert zu beschreiben) -> hit?, Optional[list[(adresse, wert) zum in HS schreiben] (entweder verängtes oder write no allocate)
    def __init__(self, tag_bits: int, associativity: int, block_size: int) -> None:
        assert block_size % 2 == 0
        assert associativity % 2 == 0
        self.tag_bits = tag_bits
        self.block_bits = block_size ** (1 / 2)
        self.blocks = [CacheBlock(block_size) for _ in range(associativity)]
        self.lru = [i for i in range(associativity)]

    #                       was i memory steht falls du es nicht hast und reinschreiben musst
    def read(self, address: int) -> Optional[list[UInt32]]:
        """Tries to read the value from the given address.

        Args:
            address (int): Full memory address.

        Returns:
            Optional[UInt32]: Returns the full block in case of a read-hit, or None in case of a read-miss.
        """
        block_index = self.get_block_index(address)
        if block_index is not None:
            self._prioritize(block_index)
            return self.blocks[block_index].values
        return None

    def write(self, address: int, block_values: list[UInt32]) -> bool:
        """Writes the given block to the set.

        Args:
            address (int): Full memory address.
            block_values (list[UInt32]): The block values to write.

        Returns:
            bool: Whether it was a write-hit.
        """
        block_index = self.get_block_index(address)
        is_hit = block_index is not None
        if block_index is None:
            block_index = self.lru[-1]
        self.blocks[block_index].write(block_values)
        self._prioritize(block_index)
        return is_hit

    def is_block_in_set(self, address: int) -> bool:
        """Returns whether the address is stored in the set.

        Args:
            address (int): Full memory address.

        Returns:
            bool: Whether the address is stored in the set ('cache hit')
        """
        return self.get_block_index(address) is not None

    def get_block_index(self, address: int) -> Optional[int]:
        """Checks whether the address is in the set and returns the index of the block if it is.

        Args:
            address (int): Full memory address.

        Returns:
            Optional[int]: Returns the index of the block, if it is stored in the set, or None if it is not.
        """
        target_tag = select_bits(
            number=address, start=(32 - self.tag_bits), stop=self.tag_bits
        )
        for block_index, block in enumerate(self.blocks):
            if (block.tag == target_tag) and block.valid_bit:
                return block_index
        return None

    def _prioritize(self, block_index: int) -> None:
        self.lru.remove(block_index)
        self.lru.insert(0, block_index)


class Cache:
    def __init__(
        self, number_sets: int, associativity: int, block_size: int, main_memory: Memory
    ) -> None:
        assert number_sets % 2 == 0
        assert associativity % 2 == 0
        assert block_size % 2 == 0

        self.block_size = block_size
        self.block_size_bits = block_size // 2
        self.block_mask = 0xFFFFFFFF ^ (block_size * 4 - 1)
        self.tag_bits = 32 - (number_sets // 2) - (block_size // 2) - 2

        assert (
            2**self.tag_bits >= associativity
        )  # cache can fit everything if this is not true :)

        self.index_bits_start = 2 + (block_size // 2)
        self.index_bits_stop = self.index_bits_start + (number_sets // 2)

        self.sets: list[CacheSet] = [
            CacheSet(self.tag_bits, associativity, block_size)
            for _ in range(number_sets)
        ]

        self.main_memory = main_memory

    def write_byte(self, address: int, value: UInt8) -> bool:
        return False

    def write_halfword(self, address: int, value: UInt16) -> bool:
        return False

    def write_word(self, address: int, value: UInt32) -> bool:
        return False

    def read_byte(self, address: int) -> tuple[UInt8, bool]:
        index = select_bits(address, self.index_bits_start, self.index_bits_stop)
        block_content = self.sets[index].read(address)
        block_content is not None
        if block_content is None:
            block_content = self._read_block_data_from_main_memory(address)
            self.sets[index].write(address, block_content)
        word = block_content[
            (address % (self.block_size << 2)) >> 2
        ]  # TODO: is this correct

        return (UInt8(0), False)

    def read_halfword(self, address: int) -> tuple[UInt16, bool]:
        return (UInt16(0), False)

    def read_word(self, address: int) -> tuple[UInt32, bool]:
        return (UInt32(0), False)

    def _read_block_data_from_main_memory(self, address: int) -> list[UInt32]:
        start_address = address & self.block_mask
        return [
            UInt32(int(self.main_memory.read_word(start_address + 4 * i)))
            for i in range(self.block_size)
        ]
