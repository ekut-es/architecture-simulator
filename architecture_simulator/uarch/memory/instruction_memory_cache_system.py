from architecture_simulator.uarch.memory.instruction_memory_system import (
    InstructionMemorySystem,
)
from architecture_simulator.uarch.memory.cache import Cache
from architecture_simulator.uarch.memory.instruction_memory import InstructionMemory
from architecture_simulator.isa.riscv.rv32i_instructions import RiscvInstruction
from architecture_simulator.isa.instruction import Instruction
from architecture_simulator.uarch.memory.decoded_address import DecodedAddress


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
        return self.instruction_at_address(address)

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
            self.instruction_memory.read_instruction(
                decoded_address.block_alinged_address + 4 * i
            )
            for i in range(self.cache.num_words_in_block)
        ]
