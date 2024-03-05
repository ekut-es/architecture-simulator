from architecture_simulator.uarch.memory.instruction_memory_system import (
    InstructionMemorySystem,
)
from architecture_simulator.uarch.memory.cache import Cache, CacheRepr
from architecture_simulator.uarch.memory.instruction_memory import InstructionMemory
from architecture_simulator.isa.riscv.rv32i_instructions import RiscvInstruction
from architecture_simulator.uarch.memory.decoded_address import DecodedAddress
from architecture_simulator.isa.riscv.instruction_types import EmptyInstruction


class InstructionMemoryCacheSystem(InstructionMemorySystem):
    def __init__(
        self,
        instruction_memory: InstructionMemory[RiscvInstruction],
        num_index_bits: int,
        num_block_bits: int,
        associativity: int,
    ) -> None:
        # TODO: check that num_index_bits, num_block_bits, associativity have legal values
        self.cache = Cache[RiscvInstruction](
            num_index_bits=num_index_bits,
            num_block_bits=num_block_bits,
            associativity=associativity,
        )

        self.num_index_bits = num_index_bits
        self.num_block_bits = num_block_bits
        self.associativity = associativity

        self.instruction_memory = instruction_memory
        self.hits = 0
        self.accesses = 0

    def reset(self) -> None:
        self.instruction_memory.reset()
        self.cache = Cache[RiscvInstruction](
            num_index_bits=self.num_index_bits,
            num_block_bits=self.num_block_bits,
            associativity=self.associativity,
        )

    def has_instructions(self) -> bool:
        return bool(self.instruction_memory.has_instructions())

    def get_address_range(self) -> range:
        return self.instruction_memory.get_address_range()

    def get_representation(self) -> list[tuple[int, str]]:
        return self.instruction_memory.get_representation()

    def read_instruction(self, address: int) -> RiscvInstruction:
        decoded_address = self._decode_address(address)
        block_values, hit = self._read_block(decoded_address)
        self.accesses += 1
        self.hits += int(hit)
        return block_values[decoded_address.block_offset]

    def write_instruction(self, address: int, instr: RiscvInstruction):
        self.instruction_memory.write_instruction(address, instr)

    def write_instructions(self, instructions: list[RiscvInstruction]):
        self.instruction_memory.write_instructions(instructions)

    def instruction_at_address(self, address: int) -> bool:
        return self.instruction_memory.instruction_at_address(address)

    def get_cache_stats(self) -> dict[str, str]:
        return {"hits": str(self.hits), "accesses": str(self.accesses)}

    def cache_repr(self) -> CacheRepr:
        return self.cache.get_repr()

    def _decode_address(self, address: int) -> DecodedAddress:
        return DecodedAddress(
            self.cache.num_index_bits, self.cache.num_block_bits, address
        )

    def _read_block(
        self, decoded_address: DecodedAddress
    ) -> tuple[list[RiscvInstruction], bool]:
        block_values = self.cache.read_block(decoded_address)
        hit = block_values is not None
        if block_values is None:
            block_values = self._read_block_from_memory(decoded_address)
            self.cache.write_block(decoded_address, block_values)
        return block_values, hit

    def _read_block_from_memory(
        self, decoded_address: DecodedAddress
    ) -> list[RiscvInstruction]:
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
