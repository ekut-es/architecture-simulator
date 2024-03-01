from unittest import TestCase
from fixedint import MutableUInt8, MutableUInt16, MutableUInt32, MutableUInt64

from architecture_simulator.uarch.memory.decoded_address import DecodedAddress
from architecture_simulator.uarch.memory.memory import Memory, AddressingType
from architecture_simulator.uarch.memory.write_through_memory_system import (
    WriteThroughMemorySystem,
)


class TestCache(TestCase):
    def test_decoded_address(self) -> None:
        addr1 = DecodedAddress(8, 2, 0b1101_0100_1010_1101_0101_1101_0010_0111)
        self.assertEqual(addr1.tag, 0b1101_0100_1010_1101_0101)
        self.assertEqual(addr1.cache_set_index, 0b1101_0010)
        self.assertEqual(
            addr1.word_alinged_address, 0b1101_0100_1010_1101_0101_1101_0010_0100
        )
        self.assertEqual(addr1.byte_offset, 0b11)
        self.assertEqual(
            addr1.block_alinged_address, 0b1101_0100_1010_1101_0101_1101_0010_0000
        )
        self.assertEqual(addr1.block_offset, 0b01)

        addr2 = DecodedAddress(5, 0, 0b1101_0110_1101_1101_0101_1010_1111_1100)
        self.assertEqual(addr2.tag, 0b1101_0110_1101_1101_0101_1010_1)
        self.assertEqual(addr2.cache_set_index, 0b111_11)
        self.assertEqual(
            addr2.word_alinged_address, 0b1101_0110_1101_1101_0101_1010_1111_1100
        )
        self.assertEqual(addr2.byte_offset, 0b0)
        self.assertEqual(
            addr2.block_alinged_address, 0b1101_0110_1101_1101_0101_1010_1111_1100
        )
        self.assertEqual(addr2.block_offset, 0b0)

    def test_cache_1(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, MutableUInt32(i))
        memory_system = WriteThroughMemorySystem(
            num_index_bits=1,
            num_block_bits=1,
            associativity=1,
            memory=memory,
        )

        memory_system.read_word(0)
        memory_system.read_word(4)
        memory_system.read_word(8)
        memory_system.read_word(12)
        memory_system.read_word(16)
        memory_system.read_word(12)
        memory_system.read_word(16)
        memory_system.read_word(60)

        self.assertEqual(memory_system.hits, 4)
        self.assertEqual(memory_system.accesses, 8)

    def test_cache_2(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, MutableUInt32(i))
        memory_system = WriteThroughMemorySystem(
            num_index_bits=2,
            num_block_bits=0,
            associativity=1,
            memory=memory,
        )
        memory_system.read_word(0)
        memory_system.read_word(16)
        memory_system.read_word(0)
        memory_system.read_word(16)
        memory_system.read_word(0)
        memory_system.read_word(16)
        memory_system.read_word(0)
        memory_system.read_word(16)

        self.assertEqual(memory_system.hits, 0)
        self.assertEqual(memory_system.accesses, 8)

    def test_cache_3(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, MutableUInt32(i))
        memory_system = WriteThroughMemorySystem(
            num_index_bits=1,
            num_block_bits=0,
            associativity=2,
            memory=memory,
        )
        memory_system.read_word(0)
        memory_system.read_word(16)
        memory_system.read_word(0)
        memory_system.read_word(16)
        memory_system.read_word(0)
        memory_system.read_word(16)
        memory_system.read_word(0)
        memory_system.read_word(16)

        self.assertEqual(memory_system.hits, 6)
        self.assertEqual(memory_system.accesses, 8)

    def test_cache_4(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, MutableUInt32(i))
        memory_system = WriteThroughMemorySystem(
            num_index_bits=1,
            num_block_bits=0,
            associativity=4,
            memory=memory,
        )
        # 0 [ , , , ]
        # 1 [ , , , ]
        # 0, 8, 16, 24, 32, 0, 8, 16, 24, 32
        memory_system.read_word(0)
        memory_system.read_word(8)
        memory_system.read_word(16)
        memory_system.read_word(24)
        memory_system.read_word(32)
        memory_system.read_word(0)
        memory_system.read_word(8)
        memory_system.read_word(16)
        memory_system.read_word(24)
        memory_system.read_word(32)

        self.assertEqual(memory_system.hits, 0)
        self.assertEqual(memory_system.accesses, 10)

    def test_cache_5(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, MutableUInt32(i))
        memory_system = WriteThroughMemorySystem(
            num_index_bits=1,
            num_block_bits=0,
            associativity=4,
            memory=memory,
        )
        # 0 [ , , , ]
        # 1 [ , , , ]
        # 0, 8, 16, 24, 32, 8, 16, 0
        memory_system.read_word(0)
        memory_system.read_word(8)
        memory_system.read_word(16)
        memory_system.read_word(24)
        memory_system.read_word(32)
        memory_system.read_word(8)
        memory_system.read_word(16)
        memory_system.read_word(0)

        self.assertEqual(memory_system.hits, 2)
        self.assertEqual(memory_system.accesses, 8)
