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


class WriteThroughMemorySystem(BaseCacheMemorySystem):
    """
    Cache Memory System implementing write through with write no allocate.
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
        Initialize a WriteThroughMemorySystem object.

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
        Writes the byte to the specified memory address.
        Uses write through, no allocate, so writes directly to lower memroy.

        Parameters:
            address (int): The memory address to write to.
            value (UInt8): The value to write.
            directly_write_to_lower_memory (bool, optional): If true skip cache and performance tracking. Defaults to false.

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
        self.hits += int(hit)
        self.last_was_hit = hit
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
        """
        Writes the halfword to the specified memory address.
        Uses write through, no allocate, so writes directly to lower memroy.

        Parameters:
            address (int): The memory address to write to.
            value (UInt16): The value to write.
            directly_write_to_lower_memory (bool, optional): If true skip cache and performance tracking. Defaults to false.

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
        self.hits += int(hit)
        self.last_was_hit = hit
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
        """
        Writes the word to the specified memory address.
        Uses write through, no allocate, so writes directly to lower memroy.

        Parameters:
            address (int): The memory address to write to.
            value (UInt32): The value to write.
            directly_write_to_lower_memory (bool, optional): If true skip cache and performance tracking. Defaults to false.

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
        self.hits += int(hit)
        self.last_was_hit = hit
        if not hit:
            self.performance_metrics.cycles += self.miss_penality
        self.accesses += 1

        if block_values is not None:
            block_values = word_into_block(decoded_address, block_values, value)
            self.cache.write_block(decoded_address, block_values)
        self.memory.write_word(address, value)

    def _read_block(self, decoded_address: DecodedAddress) -> tuple[list[UInt32], bool]:
        """
        Reads block.
        Will try to read from cache. If hit return, else read block from lower memory and allocate.

        Parameters:
            decoded_address (DecodedAddress): Decoded address that provides the address of the block.
        Returns:
            tuple[list[UInt32], bool]: Words of the block read from lower memory, and whether the read was a hit.
        """
        block_values = self.cache.read_block(decoded_address)
        hit = block_values is not None
        if block_values is None:
            block_values = self._read_block_from_memory(decoded_address)
            self.cache.write_block(decoded_address, block_values)
        return block_values, hit
