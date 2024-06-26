import unittest
from fixedint import UInt16

from architecture_simulator.uarch.toy.toy_architectural_state import (
    ToyArchitecturalState,
)
from architecture_simulator.uarch.memory.memory import MemoryAddressError
from architecture_simulator.isa.toy.toy_instructions import (
    ADD,
    INC,
    ZRO,
    ToyInstruction,
)
from architecture_simulator.simulation.toy_simulation import ToySimulation


class TestToyArchitecture(unittest.TestCase):
    def test_memory(self):
        state = ToyArchitecturalState()
        self.assertEqual(state.memory.read_halfword(1024), 0)
        self.assertEqual(state.memory.read_halfword(2048), 0)
        self.assertEqual(state.memory.read_halfword(4095), 0)
        with self.assertRaises(MemoryAddressError):
            state.memory.read_halfword(4096)

        state.memory.write_halfword(address=1024, value=UInt16(1))
        state.memory.write_halfword(address=2000, value=UInt16(1000))
        state.memory.write_halfword(address=4095, value=UInt16(2**16 - 1))
        self.assertEqual(state.memory.read_halfword(1024), 1)
        self.assertEqual(state.memory.read_halfword(2000), 1000)
        self.assertEqual(state.memory.read_halfword(4095), 2**16 - 1)

    def test_instruction_memory(self):
        state = ToyArchitecturalState()
        instructions = [INC(), INC(), ADD(1024), ZRO(), INC()]
        for addr, instr in enumerate(instructions):
            state.memory.write_halfword(addr, int(instr))
        self.assertEqual(
            ToyInstruction.from_integer((state.memory.read_halfword(0))),
            instructions[0],
        )
        self.assertEqual(
            ToyInstruction.from_integer((state.memory.read_halfword(1))),
            instructions[1],
        )
        self.assertEqual(
            ToyInstruction.from_integer((state.memory.read_halfword(2))),
            instructions[2],
        )
        self.assertEqual(
            ToyInstruction.from_integer((state.memory.read_halfword(3))),
            instructions[3],
        )
        self.assertEqual(
            ToyInstruction.from_integer((state.memory.read_halfword(4))),
            instructions[4],
        )

        with self.assertRaises(MemoryAddressError):
            state.memory.write_halfword(-1, int(ADD(2000)))
        with self.assertRaises(MemoryAddressError):
            state.memory.read_halfword(address=-1)

    def test_memory_repr(self):
        state = ToyArchitecturalState()
        state.memory.write_halfword(address=1024, value=UInt16(0))
        state.memory.write_halfword(address=1025, value=UInt16(0xFFFF))
        state.memory.write_halfword(address=2000, value=UInt16(0x0F0F))
        state.memory.write_halfword(address=4094, value=UInt16(0xDEAD))
        state.memory.write_halfword(address=4095, value=UInt16(0x123A))
        entries = state.memory.half_wordwise_repr()
        self.assertEqual(entries[1024], ("00000000 00000000", "0", "00 00", "0"))
        self.assertEqual(entries[1025], ("11111111 11111111", "65535", "FF FF", "-1"))
        self.assertEqual(entries[2000], ("00001111 00001111", "3855", "0F 0F", "3855"))
        self.assertEqual(
            entries[4094], ("11011110 10101101", "57005", "DE AD", "-8531")
        )
        self.assertEqual(entries[4095], ("00010010 00111010", "4666", "12 3A", "4666"))

    def test_pc_overflow(self):
        simulation = ToySimulation()
        simulation.load_program("NOP\n" * 4096)
        for _ in range(4095):
            simulation.step()
        self.assertEqual(simulation.state.program_counter, 0)
