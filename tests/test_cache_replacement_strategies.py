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

from architecture_simulator.uarch.memory.replacement_strategies import LRU, PLRU


class TestReplacementStrategies(TestCase):
    pass
