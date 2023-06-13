import unittest
import fixedint

from architecture_simulator.uarch.architectural_state import (
    RegisterFile,
    ArchitecturalState,
    Memory,
)
from architecture_simulator.isa.rv32i_instructions import ADD, SLL


class TestArchitecture(unittest.TestCase):
    def test_register(self):
        # x0 can not be changed
        state = ArchitecturalState(register_file=RegisterFile())
        state.register_file.registers[0] = 187
        self.assertEqual(state.register_file.registers[0], 0)

        # x31 can still be accessed
        state.register_file.registers[31] = 12345
        self.assertEqual(state.register_file.registers[31], 12345)

        # x32 can not be accessed
        with self.assertRaises(IndexError):
            state.register_file.registers[32]

        # x32 can not be set
        state.register_file.registers[32] = 187
        with self.assertRaises(IndexError):
            state.register_file.registers[32]

        # instructions still work as intended
        state.register_file.registers[1] = fixedint.MutableUInt32(0x_80_00_00_00)
        state.register_file.registers[2] = fixedint.MutableUInt32(0x_FF_FF_FF_FF)
        add = ADD(rd=3, rs1=1, rs2=2)
        state = add.behavior(state)
        self.assertEqual(
            state.register_file.registers[3], fixedint.MutableUInt32(0x_7F_FF_FF_FF)
        )

        state.register_file.registers[4] = fixedint.MutableUInt32(31)
        state.register_file.registers[5] = fixedint.MutableUInt32(7)
        sll = SLL(rd=4, rs1=5, rs2=4)
        state = sll.behavior(state)
        self.assertEqual(
            state.register_file.registers[4], fixedint.MutableUInt32(0x_80_00_00_00)
        )

    def test_mem(self):
        state = ArchitecturalState(
            register_file=RegisterFile(registers=()), memory=Memory(min_bytes=0)
        )
        # store_byte test
        state.memory.store_byte(0, fixedint.MutableUInt8(1))
        self.assertEqual(state.memory.load_byte(0), fixedint.MutableUInt8(1))

        # store_byte type test
        state.memory.store_byte(0, fixedint.MutableUInt8(1))
        self.assertIsInstance(state.memory.load_byte(0), fixedint.MutableUInt8)

        # store_halfword test
        state.memory.store_halfword(0, fixedint.MutableUInt16(1))
        self.assertEqual(state.memory.load_halfword(0), fixedint.MutableUInt16(1))

        # store_halfword type test
        state.memory.store_halfword(0, fixedint.MutableUInt16(1))
        self.assertIsInstance(state.memory.load_halfword(0), fixedint.MutableUInt16)

        # store_word test
        state.memory.store_word(0, fixedint.MutableUInt32(1))
        self.assertEqual(state.memory.load_word(0), fixedint.MutableUInt32(1))

        # store_word type test
        state.memory.store_word(0, fixedint.MutableUInt32(1))
        self.assertIsInstance(state.memory.load_word(0), fixedint.MutableUInt32)

        # store_byte negative value test
        state.memory.store_byte(0, fixedint.MutableUInt8(-1))
        self.assertEqual(state.memory.load_byte(0), fixedint.MutableUInt8(-1))

        # store_halfword negative value test
        state.memory.store_halfword(0, fixedint.MutableUInt16(-1))
        self.assertEqual(state.memory.load_halfword(0), fixedint.MutableUInt16(-1))

        # store_word test
        state.memory.store_word(0, fixedint.MutableUInt32(-1))
        self.assertEqual(state.memory.load_word(0), fixedint.MutableUInt32(-1))

        # tests are now with 16 bit length of memory
        state = ArchitecturalState(
            register_file=RegisterFile(registers=()),
            memory=Memory(memory_file={}, address_length=16, min_bytes=0),
        )

        # store_byte test
        state.memory.store_byte(pow(2, 16), fixedint.MutableUInt8(2))
        self.assertEqual(state.memory.load_word(0), fixedint.MutableUInt32(2))

        # store_halfword test
        state.memory.store_halfword(pow(2, 16), fixedint.MutableUInt16(3))
        self.assertEqual(state.memory.load_halfword(0), fixedint.MutableUInt16(3))

        # store_word test
        state.memory.store_word(pow(2, 16), fixedint.MutableUInt32(4))
        self.assertEqual(state.memory.load_word(0), fixedint.MutableUInt32(4))

    def test_unified_memory(self):
        state = ArchitecturalState()

        # Save instr tests:
        state.instruction_memory.save_instruction(
            address=0, instr=ADD(rd=0, rs1=0, rs2=0)
        )
        self.assertEqual(
            state.instruction_memory.instructions[0], ADD(rd=0, rs1=0, rs2=0)
        )
        state.instruction_memory.save_instruction(
            address=2**14 - 4, instr=ADD(rd=1, rs1=2, rs2=3)
        )
        self.assertEqual(
            state.instruction_memory.instructions[2**14 - 4], ADD(rd=1, rs1=2, rs2=3)
        )

        # Illegal access out of bounds of instr memory
        with self.assertRaises(ValueError):
            state.instruction_memory.save_instruction(
                address=2**14, instr=ADD(rd=1, rs1=2, rs2=3)
            )

        with self.assertRaises(ValueError):
            state.instruction_memory.save_instruction(
                address=-1, instr=ADD(rd=1, rs1=2, rs2=3)
            )

        # load instr tests:
        self.assertEqual(
            state.instruction_memory.load_instruction(0), ADD(rd=0, rs1=0, rs2=0)
        )
        self.assertEqual(
            state.instruction_memory.load_instruction(2**14 - 4),
            ADD(rd=1, rs1=2, rs2=3),
        )

        with self.assertRaises(KeyError):
            state.instruction_memory.load_instruction(4)

        with self.assertRaises(KeyError):
            state.instruction_memory.load_instruction(2**14)
