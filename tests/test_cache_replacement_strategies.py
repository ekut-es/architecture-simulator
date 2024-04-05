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

from architecture_simulator.uarch.memory.replacement_strategies import PLRU
from architecture_simulator.uarch.riscv.riscv_performance_metrics import (
    RiscvPerformanceMetrics,
)


class TestReplacementStrategies(TestCase):
    def test_plru_1(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, UInt32(i))
        memory_system = WriteThroughMemorySystem(
            num_index_bits=0,
            num_block_bits=0,
            associativity=1,
            memory=memory,
            replacement_strategy="plru",
            performance_metrics=RiscvPerformanceMetrics(),
        )

        memory_system.read_word(0)
        memory_system.read_word(0)
        memory_system.read_word(8)
        memory_system.read_word(4)
        memory_system.read_word(4)
        self.assertEqual(memory_system.get_cache_stats()["hits"], "2")
        self.assertEqual(memory_system.get_cache_stats()["accesses"], "5")

    def test_plru_2(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, UInt32(i))
        memory_system = WriteThroughMemorySystem(
            num_index_bits=0,
            num_block_bits=0,
            associativity=2,
            memory=memory,
            replacement_strategy="plru",
            performance_metrics=RiscvPerformanceMetrics(),
        )

        memory_system.read_word(0)
        memory_system.read_word(4)
        memory_system.read_word(0)
        memory_system.read_word(4)
        self.assertEqual(memory_system.get_cache_stats()["hits"], "2")
        self.assertEqual(memory_system.get_cache_stats()["accesses"], "4")

    def test_plru_3(self) -> None:
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, UInt32(i))
        memory_system = WriteThroughMemorySystem(
            num_index_bits=0,
            num_block_bits=0,
            associativity=2,
            memory=memory,
            replacement_strategy="plru",
            performance_metrics=RiscvPerformanceMetrics(),
        )

        memory_system.read_word(0)
        memory_system.read_word(4)
        memory_system.read_word(4)
        memory_system.read_word(8)
        memory_system.read_word(0)
        memory_system.read_word(4)
        self.assertEqual(memory_system.get_cache_stats()["hits"], "1")
        self.assertEqual(memory_system.get_cache_stats()["accesses"], "6")

    def test_plru_4(self):
        memory = Memory(AddressingType.BYTE, 32, True)
        for i in range(32):
            memory.write_word(i * 4, UInt32(i))
        memory_system = WriteThroughMemorySystem(
            num_index_bits=0,
            num_block_bits=0,
            associativity=4,
            memory=memory,
            replacement_strategy="plru",
            performance_metrics=RiscvPerformanceMetrics(),
        )

        self.assertEqual(
            memory_system.cache.sets[0].replacement_strategy.tree_array, [0, 0, 0]
        )
        memory_system.read_word(0)
        self.assertEqual(
            memory_system.cache.sets[0].replacement_strategy.tree_array, [1, 1, 0]
        )
        memory_system.read_word(0)
        self.assertEqual(
            memory_system.cache.sets[0].replacement_strategy.tree_array, [1, 1, 0]
        )
        memory_system.read_word(4)
        self.assertEqual(
            memory_system.cache.sets[0].replacement_strategy.tree_array, [0, 1, 1]
        )
        memory_system.read_word(8)
        self.assertEqual(
            memory_system.cache.sets[0].replacement_strategy.tree_array, [1, 0, 1]
        )
        memory_system.read_word(12)
        memory_system.read_word(12)
        self.assertEqual(
            memory_system.cache.sets[0].replacement_strategy.tree_array, [0, 0, 0]
        )

        self.assertEqual(
            memory_system.cache.sets[0].blocks[0].decoded_address.full_address, 0
        )
        self.assertEqual(
            memory_system.cache.sets[0].blocks[1].decoded_address.full_address, 8
        )
        self.assertEqual(
            memory_system.cache.sets[0].blocks[2].decoded_address.full_address, 4
        )
        self.assertEqual(
            memory_system.cache.sets[0].blocks[3].decoded_address.full_address, 12
        )

        memory_system.read_word(0)
        self.assertEqual(
            memory_system.cache.sets[0].replacement_strategy.tree_array, [1, 1, 0]
        )

        self.assertEqual(memory_system.get_cache_stats()["hits"], "3")
        self.assertEqual(memory_system.get_cache_stats()["accesses"], "7")
