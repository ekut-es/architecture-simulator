import unittest
from fixedint import MutableUInt16

from architecture_simulator.uarch.toy.toy_architectural_state import (
    ToyArchitecturalState,
)
from architecture_simulator.uarch.memory import MemoryAddressError
from architecture_simulator.isa.toy.toy_instructions import ADD, INC, ZRO


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
        self.assertEqual(state.data_memory.read_halfword(1024), 0)
        self.assertEqual(state.data_memory.read_halfword(2048), 0)
        self.assertEqual(state.data_memory.read_halfword(4095), 0)
        with self.assertRaises(MemoryAddressError):
            state.data_memory.read_halfword(1023)
        with self.assertRaises(MemoryAddressError):
            state.data_memory.read_halfword(0)
        with self.assertRaises(MemoryAddressError):
            state.data_memory.read_halfword(4096)

        state.data_memory.write_halfword(address=1024, value=MutableUInt16(1))
        state.data_memory.write_halfword(address=2000, value=MutableUInt16(1000))
        state.data_memory.write_halfword(address=4095, value=MutableUInt16(2**16 - 1))
        self.assertEqual(state.data_memory.read_halfword(1024), 1)
        self.assertEqual(state.data_memory.read_halfword(2000), 1000)
        self.assertEqual(state.data_memory.read_halfword(4095), 2**16 - 1)

        with self.assertRaises(MemoryAddressError):
            state.data_memory.write_halfword(address=1023, value=MutableUInt16(1))
        with self.assertRaises(MemoryAddressError):
            state.data_memory.write_halfword(address=0, value=MutableUInt16(1000))
        with self.assertRaises(MemoryAddressError):
            state.data_memory.write_halfword(address=4096, value=MutableUInt16(19192))

    def test_instruction_memory(self):
        state = ToyArchitecturalState()
        instructions = [INC(), INC(), ADD(1024), ZRO(), INC()]
        state.instruction_memory.write_instructions(instructions)
        self.assertEqual(state.instruction_memory.read_instruction(0), instructions[0])
        self.assertEqual(state.instruction_memory.read_instruction(1), instructions[1])
        self.assertEqual(state.instruction_memory.read_instruction(2), instructions[2])
        self.assertEqual(state.instruction_memory.read_instruction(3), instructions[3])
        self.assertEqual(state.instruction_memory.read_instruction(4), instructions[4])

        with self.assertRaises(MemoryAddressError):
            state.instruction_memory.write_instruction(address=-1, instr=ADD(2000))
        with self.assertRaises(MemoryAddressError):
            state.instruction_memory.write_instruction(address=1024, instr=ADD(2000))
        with self.assertRaises(MemoryAddressError):
            state.instruction_memory.read_instruction(address=-1)
        with self.assertRaises(MemoryAddressError):
            state.instruction_memory.read_instruction(address=1024)
