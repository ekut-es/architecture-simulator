from unittest import TestCase
from fixedint import MutableUInt8, MutableUInt16, MutableUInt32, MutableUInt64

from architecture_simulator.uarch.cache import select_bits, DecodedAddress, Cache
from architecture_simulator.uarch.memory import Memory, AddressingType


class TestCache(TestCase):
    def test_select_bits(self) -> None:
        self.assertEqual(select_bits(0xFF0, 4, 8), 0xF)
        self.assertEqual(select_bits(0xFFFF, 0, 0), 0)
        self.assertEqual(select_bits(0xE, 0, 1), 0)
        self.assertEqual(select_bits(0xABCDABCD, 0, 32), 0xABCDABCD)
        self.assertEqual(select_bits(0xDCBAABCD, 12, 20), 0xAA)

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
        cache = Cache(
            num_index_bits=1,
            num_block_bits=1,
            associativity=1,
            main_memory=memory,
        )
        c = 0
        c += int(cache.read_word(0)[1])
        c += int(cache.read_word(4)[1])
        c += int(cache.read_word(8)[1])
        c += int(cache.read_word(12)[1])
        c += int(cache.read_word(16)[1])
        c += int(cache.read_word(12)[1])
        c += int(cache.read_word(16)[1])
        c += int(cache.read_word(60)[1])

        self.assertEqual(c, 4)

    def test_cache_2(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, MutableUInt32(i))
        cache = Cache(
            num_index_bits=2,
            num_block_bits=0,
            associativity=1,
            main_memory=memory,
        )
        c = 0
        c += int(cache.read_word(0)[1])
        c += int(cache.read_word(16)[1])
        c += int(cache.read_word(0)[1])
        c += int(cache.read_word(16)[1])
        c += int(cache.read_word(0)[1])
        c += int(cache.read_word(16)[1])
        c += int(cache.read_word(0)[1])
        c += int(cache.read_word(16)[1])

        self.assertEqual(c, 0)

    def test_cache_3(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, MutableUInt32(i))
        cache = Cache(
            num_index_bits=1,
            num_block_bits=0,
            associativity=2,
            main_memory=memory,
        )
        c = 0
        c += int(cache.read_word(0)[1])
        c += int(cache.read_word(16)[1])
        c += int(cache.read_word(0)[1])
        c += int(cache.read_word(16)[1])
        c += int(cache.read_word(0)[1])
        c += int(cache.read_word(16)[1])
        c += int(cache.read_word(0)[1])
        c += int(cache.read_word(16)[1])

        self.assertEqual(c, 6)

    def test_cache_4(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, MutableUInt32(i))
        cache = Cache(
            num_index_bits=1,
            num_block_bits=0,
            associativity=4,
            main_memory=memory,
        )
        # 0 [ , , , ]
        # 1 [ , , , ]
        # 0, 8, 16, 24, 32, 0, 8, 16, 24, 32
        c = 0
        c += int(cache.read_word(0)[1])
        c += int(cache.read_word(8)[1])
        c += int(cache.read_word(16)[1])
        c += int(cache.read_word(24)[1])
        c += int(cache.read_word(32)[1])
        c += int(cache.read_word(0)[1])
        c += int(cache.read_word(8)[1])
        c += int(cache.read_word(16)[1])
        c += int(cache.read_word(24)[1])
        c += int(cache.read_word(32)[1])

        self.assertEqual(c, 0)

    def test_cache_5(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, MutableUInt32(i))
        cache = Cache(
            num_index_bits=1,
            num_block_bits=0,
            associativity=4,
            main_memory=memory,
        )
        # 0 [ , , , ]
        # 1 [ , , , ]
        # 0, 8, 16, 24, 32, 8, 16, 0
        c = 0
        c += int(cache.read_word(0)[1])
        c += int(cache.read_word(8)[1])
        c += int(cache.read_word(16)[1])
        c += int(cache.read_word(24)[1])
        c += int(cache.read_word(32)[1])
        c += int(cache.read_word(8)[1])
        c += int(cache.read_word(16)[1])
        c += int(cache.read_word(0)[1])

        self.assertEqual(c, 2)
