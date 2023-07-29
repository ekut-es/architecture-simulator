import unittest
from fixedint import MutableUInt16

from architecture_simulator.uarch.toy.toy_architectural_state import (
    ToyArchitecturalState,
)
from architecture_simulator.uarch.memory import MemoryAddressError


class TestToyArchitecture(unittest.TestCase):
    def test_program_counter(self):
        state = ToyArchitecturalState()
        self.assertEqual(state.program_counter, 0)
        state.increment_pc()
        self.assertEqual(state.program_counter, 1)
        state.increment_pc()
        self.assertEqual(state.program_counter, 2)
        state.increment_pc()
        self.assertEqual(state.program_counter, 3)
        state.program_counter = MutableUInt16(2**16 - 1)
        state.increment_pc()
        self.assertEqual(state.program_counter, 0)

    def test_data_memory(self):
        state = ToyArchitecturalState()
        self.assertEqual(state.load(1024), 0)
        self.assertEqual(state.load(2048), 0)
        self.assertEqual(state.load(4095), 0)
        with self.assertRaises(MemoryAddressError):
            state.load(1023)
        with self.assertRaises(MemoryAddressError):
            state.load(0)
        with self.assertRaises(MemoryAddressError):
            state.load(4096)

        state.store(address=1024, value=MutableUInt16(1))
        state.store(address=2000, value=MutableUInt16(1000))
        state.store(address=4095, value=MutableUInt16(2**16 - 1))
        self.assertEqual(state.load(1024), 1)
        self.assertEqual(state.load(2000), 1000)
        self.assertEqual(state.load(4095), 2**16 - 1)

        with self.assertRaises(MemoryAddressError):
            state.store(address=1023, value=MutableUInt16(1))
        with self.assertRaises(MemoryAddressError):
            state.store(address=0, value=MutableUInt16(1000))
        with self.assertRaises(MemoryAddressError):
            state.store(address=4096, value=MutableUInt16(19192))
