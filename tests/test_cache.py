from unittest import TestCase
from fixedint import UInt8, UInt16, UInt32

from architecture_simulator.uarch.memory.decoded_address import DecodedAddress
from architecture_simulator.uarch.memory.memory import Memory, AddressingType
from architecture_simulator.uarch.memory.write_through_memory_system import (
    WriteThroughMemorySystem,
)
from architecture_simulator.uarch.memory.write_back_memory_system import (
    WriteBackMemorySystem,
)
from architecture_simulator.uarch.riscv.riscv_performance_metrics import (
    RiscvPerformanceMetrics,
)
from architecture_simulator.simulation.riscv_simulation import RiscvSimulation
from architecture_simulator.uarch.memory.cache import CacheOptions


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

    def test_write_through_cache_1(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, UInt32(i))
        memory_system = WriteThroughMemorySystem(
            num_index_bits=1,
            num_block_bits=1,
            associativity=1,
            memory=memory,
            performance_metrics=RiscvPerformanceMetrics(),
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

    def test_write_through_cache_2(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, UInt32(i))
        memory_system = WriteThroughMemorySystem(
            num_index_bits=2,
            num_block_bits=0,
            associativity=1,
            memory=memory,
            performance_metrics=RiscvPerformanceMetrics(),
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

    def test_write_through_cache_3(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, UInt32(i))
        memory_system = WriteThroughMemorySystem(
            num_index_bits=1,
            num_block_bits=0,
            associativity=2,
            memory=memory,
            performance_metrics=RiscvPerformanceMetrics(),
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

    def test_write_through_cache_4(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, UInt32(i))
        memory_system = WriteThroughMemorySystem(
            num_index_bits=1,
            num_block_bits=0,
            associativity=4,
            memory=memory,
            performance_metrics=RiscvPerformanceMetrics(),
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

    def test_write_through_cache_5(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, UInt32(i))
        memory_system = WriteThroughMemorySystem(
            num_index_bits=1,
            num_block_bits=0,
            associativity=4,
            memory=memory,
            performance_metrics=RiscvPerformanceMetrics(),
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

    def test_write_through_cache_6(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        memory_system = WriteThroughMemorySystem(
            num_index_bits=5,
            num_block_bits=2,
            associativity=4,
            memory=memory,
            performance_metrics=RiscvPerformanceMetrics(),
        )
        memory_system.write_byte(1, UInt8(72))
        memory_system.write_halfword(5, UInt16(500))
        memory_system.write_halfword(5, UInt16(600))
        memory_system.write_word(8, UInt32(131072))
        memory_system.write_word(8, UInt32(131073))
        memory_system.write_word(8, UInt32(131074))

        self.assertEqual(memory_system.hits, 0)
        self.assertEqual(memory_system.accesses, 6)
        self.assertEqual(memory_system.memory.read_byte(1), 72)
        self.assertEqual(memory_system.memory.read_halfword(5), 600)
        self.assertEqual(memory_system.memory.read_word(8), 131074)

    def test_write_through_cache_7(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        memory_system = WriteThroughMemorySystem(
            num_index_bits=5,
            num_block_bits=2,
            associativity=4,
            memory=memory,
            performance_metrics=RiscvPerformanceMetrics(),
        )
        memory_system.write_byte(1, UInt8(72))
        memory_system.read_byte(1)
        memory_system.write_byte(2, UInt8(73))
        memory_system.write_byte(3, UInt8(74))
        memory_system.write_byte(0, UInt8(75))
        memory_system.write_word(0, UInt32(8))

        self.assertEqual(memory_system.hits, 4)
        self.assertEqual(memory_system.accesses, 6)
        self.assertEqual(memory_system.memory.read_word(0), 8)

    def test_write_back_cache_1(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, UInt32(i))
        memory_system = WriteBackMemorySystem(
            memory=memory,
            num_index_bits=0,
            num_block_bits=1,
            associativity=2,
            performance_metrics=RiscvPerformanceMetrics(),
        )
        memory_system.read_word(0)
        memory_system.write_word(4, UInt32(44))

        self.assertEqual(memory_system.read_word(4), UInt32(44))
        self.assertEqual(memory.memory_file[0], UInt8(0))
        self.assertEqual(memory.memory_file[4], UInt8(1))

        memory_system.read_word(8)
        self.assertEqual(memory_system.read_word(12), UInt8(3))

        self.assertEqual(memory.memory_file[4], UInt8(1))

        memory_system.read_word(16)

        self.assertEqual(memory.memory_file[4], UInt8(44))

        self.assertEqual(memory_system.hits, 3)
        self.assertEqual(memory_system.accesses, 6)

    def test_byte_into_block_fix(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        memory_system = WriteBackMemorySystem(
            memory=memory,
            num_index_bits=2,
            num_block_bits=0,
            associativity=1,
            performance_metrics=RiscvPerformanceMetrics(),
        )
        memory_system.write_byte(16, UInt8(0xFF))
        memory_system.write_byte(17, UInt8(0xFF))
        memory_system.write_byte(18, UInt8(0xFF))
        memory_system.write_byte(19, UInt8(0xFF))

        self.assertEqual(memory_system.read_word(16), 0xFFFFFFFF)

    def test_halfword_into_block_fix(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        memory_system = WriteBackMemorySystem(
            memory=memory,
            num_index_bits=2,
            num_block_bits=0,
            associativity=1,
            performance_metrics=RiscvPerformanceMetrics(),
        )
        memory_system.write_halfword(16, UInt16(0xFFFF))
        memory_system.write_halfword(18, UInt16(0xFFFF))

        self.assertEqual(memory_system.read_word(16), 0xFFFFFFFF)

    def test_write_back_cache_2(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        memory.write_word(0, UInt32(0xAAAAAAAA))
        memory.write_word(4, UInt32(0xBBBBBBBB))
        memory.write_word(8, UInt32(0xCCCCCCCC))
        memory.write_word(12, UInt32(0xDDDDDDDD))
        memory.write_word(16, UInt32(0xEEEEEEEE))
        memory_system = WriteBackMemorySystem(
            memory=memory,
            num_index_bits=2,
            num_block_bits=0,
            associativity=1,
            performance_metrics=RiscvPerformanceMetrics(),
        )
        memory_system.write_byte(0, UInt8(0))
        memory_system.write_byte(1, UInt8(0))
        memory_system.write_byte(2, UInt8(0))
        memory_system.write_byte(3, UInt8(0))

        self.assertEqual(memory_system.read_word(0), UInt32(0))
        self.assertEqual(memory.read_word(0), UInt32(0xAAAAAAAA))

        memory_system.write_byte(16, UInt8(0xFF))

        self.assertEqual(memory.read_word(0), UInt32(0))

        memory_system.write_byte(17, UInt8(0xFF))
        memory_system.write_byte(18, UInt8(0xFF))
        memory_system.write_byte(19, UInt8(0xFF))

        self.assertEqual(memory_system.read_word(16), UInt32(0xFFFFFFFF))

        self.assertEqual(memory_system.get_cache_stats()["hits"], "8")
        self.assertEqual(memory_system.get_cache_stats()["accesses"], "10")

    def test_write_back_cache_3(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, UInt32(i))
        memory_system = WriteBackMemorySystem(
            memory=memory,
            num_index_bits=1,
            num_block_bits=1,
            associativity=2,
            performance_metrics=RiscvPerformanceMetrics(),
        )

        memory_system.read_word(0)
        memory_system.read_word(16)

        memory_system.read_word(8)
        memory_system.read_word(24)

        memory_system.write_word(4, UInt32(0xFFFFFFFF))

        memory_system.read_word(32)

        self.assertEqual(memory.read_halfword(4), UInt16(1))

        memory_system.read_word(16)

        self.assertEqual(memory.read_halfword(4), UInt16(0xFFFF))

        self.assertEqual(memory_system.get_cache_stats()["hits"], "1")
        self.assertEqual(memory_system.get_cache_stats()["accesses"], "7")

    def test_address_logging(self) -> None:
        simulation = RiscvSimulation(
            data_cache=CacheOptions(
                enable=True,
                num_index_bits=2,
                num_block_bits=1,
                associativity=2,
                cache_type="wb",
                replacement_strategy="lru",
                miss_penalty=0,
            )
        )

        simulation.load_program("lw x1, -4(x0)")
        simulation.run()
        stats = simulation.get_data_cache_stats()
        self.assertEqual(stats["address"], "11111111111111111111111111111100")
