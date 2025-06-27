from architecture_simulator.uarch.memory.instruction_memory_system import (
    InstructionMemorySystem,
)
from architecture_simulator.uarch.memory.cache import Cache, CacheRepr
from architecture_simulator.uarch.memory.instruction_memory import InstructionMemory
from architecture_simulator.isa.riscv.rv32i_instructions import RiscvInstruction
from architecture_simulator.uarch.memory.decoded_address import DecodedAddress
from architecture_simulator.isa.riscv.instruction_types import EmptyInstruction
from architecture_simulator.uarch.memory.replacement_strategies import (
    ReplacementStrategy,
    LRU,
    PLRU,
)
from architecture_simulator.uarch.riscv.riscv_performance_metrics import (
    RiscvPerformanceMetrics,
)


class InstructionMemoryCacheSystem(InstructionMemorySystem):
    """
    Instruction cache memory system.
    """

    def __init__(
        self,
        instruction_memory: InstructionMemory[RiscvInstruction],
        num_index_bits: int,
        num_block_bits: int,
        associativity: int,
        performance_metrics: RiscvPerformanceMetrics,
        miss_penality: int = 0,
        replacement_strategy: str = "lru",
    ) -> None:
        """
        Initialize a InstructionMemoryCacheSystem object.

        Args:
            instruction_memory (InstructionMemory): Lower Memory.
            num_index_bits (int): Number of bits used to form the index.
            num_block_bits (int): Number of bits used to form a block. Block size is 2^N.
            associativity (int): Associativity.
            performance_metrics (RiscvPerformanceMetrics): Performance Metrics object to track cache performance.
            miss_penalty (int, optional): Amount of cycles to add to performance metrics if a cache miss occurs. Defaults to 0.
            replacement_strategy (str, optional): Cache replacement strategy. If 'lru', LRU will be used, otherwise PLRU will be used. Defaults to 'lru'.
        """
        self.replacement_strategy_class: type[ReplacementStrategy] = LRU if replacement_strategy == "lru" else PLRU  # type: ignore[type-abstract]
        self.cache = Cache[RiscvInstruction](
            num_index_bits=num_index_bits,
            num_block_bits=num_block_bits,
            associativity=associativity,
            replacement_strategy=self.replacement_strategy_class,
        )

        self.num_index_bits = num_index_bits
        self.num_block_bits = num_block_bits
        self.associativity = associativity

        self.instruction_memory = instruction_memory
        self.performance_metrics = performance_metrics
        self.miss_penality = miss_penality
        self.hits = 0
        self.accesses = 0
        self.last_was_hit = False

    def reset(self) -> None:
        """
        Clears all memory layers.
        """
        self.instruction_memory.reset()
        self.hits = 0
        self.accesses = 0
        self.last_was_hit = False
        self.cache = Cache[RiscvInstruction](
            num_index_bits=self.num_index_bits,
            num_block_bits=self.num_block_bits,
            associativity=self.associativity,
            replacement_strategy=self.replacement_strategy_class,
        )

    def has_instructions(self) -> bool:
        """
        Exposes has_instructions() of lower memory.
        """
        return bool(self.instruction_memory.has_instructions())

    def get_address_range(self) -> range:
        """
        Exposes get_address_range() of lower memory.
        """
        return self.instruction_memory.get_address_range()

    def get_representation(self) -> list[tuple[int, str]]:
        """
        Exposes get_representation() of lower memory.
        """
        return self.instruction_memory.get_representation()

    def read_instruction(self, address: int) -> RiscvInstruction:
        decoded_address = self._decode_address(address)
        block_values, hit = self._read_block(decoded_address)
        self.accesses += 1
        self.hits += int(hit)
        self.last_was_hit = hit
        if not hit:
            self.performance_metrics.cycles += self.miss_penality
        self.performance_metrics
        return block_values[decoded_address.block_offset]

    def write_instruction(self, address: int, instr: RiscvInstruction):
        """
        Exposes write_instruction() of lower memory.
        """
        self.instruction_memory.write_instruction(address, instr)

    def write_instructions(self, instructions: list[RiscvInstruction]):
        """
        Exposes write_instructions() of lower memory.
        """
        self.instruction_memory.write_instructions(instructions)

    def instruction_at_address(self, address: int) -> bool:
        """
        Exposes instruction_at_address() of lower memory.
        """
        return self.instruction_memory.instruction_at_address(address)

    def get_cache_stats(self) -> dict[str, str | bool]:
        """
        Returns cache stats as a dictionary.

        Returns:
            dict[str, str | bool]: Dictionary with keys 'hits', 'accesses' and 'last_hit'.
        """
        return {
            "hits": str(self.hits),
            "accesses": str(self.accesses),
            "last_hit": self.last_was_hit,
        }

    def cache_repr(self) -> CacheRepr:
        """
        Exposes get_repr() of cache.
        """
        return self.cache.get_repr()

    def _decode_address(self, address: int) -> DecodedAddress:
        """
        Method for creating a decoded address based on cache configuration.

        Args:
            address (int): Address to decode.

        Returns:
            DecodedAddress: Object holding all information implicitly contained in the address.
        """
        return DecodedAddress(
            self.cache.num_index_bits, self.cache.num_block_bits, address
        )

    def _read_block(
        self, decoded_address: DecodedAddress
    ) -> tuple[list[RiscvInstruction], bool]:
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
            self.cache.write_block(decoded_address, block_values, write_access=False)
        return block_values, hit

    def _read_block_from_memory(
        self, decoded_address: DecodedAddress
    ) -> list[RiscvInstruction]:
        """
        Reads block from lower memory.

        Parameters:
            decoded_address (DecodedAddress): Decoded address that provides the address of the block.
        Returns:
            list[RiscvInstruction]: List of instructions of the block.
        """
        return [
            (
                self.instruction_memory.read_instruction(a)
                if self.instruction_memory.instruction_at_address(
                    a := decoded_address.block_alinged_address + 4 * i
                )
                else EmptyInstruction()
            )
            for i in range(self.cache.num_words_in_block)
        ]
