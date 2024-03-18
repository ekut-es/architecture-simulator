from fixedint import UInt8, UInt16, UInt32

from architecture_simulator.uarch.memory.base_cache_memory_system import (
    BaseCacheMemorySystem,
)
from architecture_simulator.util.integer_manipulation import (
    byte_into_block,
    halfword_into_block,
    word_into_block,
)
from architecture_simulator.uarch.memory.decoded_address import DecodedAddress
from architecture_simulator.uarch.memory.memory import Memory
from architecture_simulator.uarch.riscv.riscv_performance_metrics import (
    RiscvPerformanceMetrics,
)


class WriteBackMemorySystem(BaseCacheMemorySystem):
    """
    Cache Memory System implementing write back with write allocate.
    """

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
        """
        Initialize a WriteBackMemorySystem object.

        Args:
            memory (Memory): Lower Memory.
            num_index_bits (int): Number of bits used to form the index.
            num_block_bits (int): Number of bits used to form a block. Block size is 2^N.
            associativity (int): Associativity.
            performance_metrics (RiscvPerformanceMetrics): Performance Metrics object to track cache performance.
            miss_penalty (int, optional): Amount of cycles to add to performance metrics if a cache miss occurs. Defaults to 0.
            replacement_strategy (str, optional): Cache replacement strategy. If 'lru', LRU will be used, otherwise PLRU will be used. Defaults to 'lru'.
        """
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
        """
        Writes the byte to the specified memory address in cache.
        Uses write allocate.

        Parameters:
            address (int): The memory address to write to.
            value (UInt8): The value to write.
            directly_write_to_lower_memory (bool, optional): If true, only write to lower memory. Skip cache and performance tracking. Defaults to false.

        Raises:
            MemoryAddressError: If the address is outside the valid memory range.
        """
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
        """
        Writes the halfword to the specified memory address.
        Uses write allocate.

        Parameters:
            address (int): The memory address to write to.
            value (UInt16): The value to write.
            directly_write_to_lower_memory (bool, optional): If true, only write to lower memory. Skip cache and performance tracking. Defaults to false.

        Raises:
            MemoryAddressError: If the address is outside the valid memory range.
        """
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
        """
        Writes the word to the specified memory address.
        Uses write allocate.

        Parameters:
            address (int): The memory address to write to.
            value (UInt32): The value to write.
            directly_write_to_lower_memory (bool, optional): If true, only write to lower memory. Skip cache and performance tracking. Defaults to false.

        Raises:
            MemoryAddressError: If the address is outside the valid memory range.
        """
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
        """
        Writes block to lower memory.

        Parameters:
            decoded_address (DecodedAddress): Decoded address that provides the address of the block.
            block (list[UInt32]): Block to write.
        """
        for i, word in enumerate(block):
            self.memory.write_word(decoded_address.block_alinged_address + 4 * i, word)

    def _read_block(self, decoded_address: DecodedAddress) -> tuple[list[UInt32], bool]:
        """
        Reads block.
        Will try to read from cache. If hit return, else read block from lower memory and allocate. Write back displaced block.

        Parameters:
            decoded_address (DecodedAddress): Decoded address that provides the address of the block.
        """
        block_values = self.cache.read_block(decoded_address)
        hit = block_values is not None
        if block_values is None:
            block_values = self._read_block_from_memory(decoded_address)
            h, displaced_block = self.cache.write_block(decoded_address, block_values)
            if displaced_block is not None:
                db_addr, db_block = displaced_block
                self._write_block_to_memory(db_addr, db_block)
        return block_values, hit
