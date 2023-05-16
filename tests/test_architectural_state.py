import unittest

from architecture_simulator.uarch.architectural_state import RegisterFile

from architecture_simulator.uarch.architectural_state import ArchitecturalState

from architecture_simulator.isa.rv32i_instructions import ADD, SLL
import fixedint


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
        state = ArchitecturalState(register_file=RegisterFile(registers=()))
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
