import unittest
import fixedint

from architecture_simulator.uarch.riscv.register_file import RegisterFile
from architecture_simulator.uarch.memory import Memory, MemoryAddressError
from architecture_simulator.uarch.riscv.riscv_architectural_state import (
    RiscvArchitecturalState,
)
from architecture_simulator.isa.riscv.rv32i_instructions import ADD, SLL
from architecture_simulator.uarch.instruction_memory import InstructionMemoryKeyError


class TestRiscvArchitecture(unittest.TestCase):
    def test_register(self):
        # x0 can not be changed
        state = RiscvArchitecturalState(register_file=RegisterFile())
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

        # reg_repr tests
        state = RiscvArchitecturalState()
        state.register_file.registers[1] = fixedint.MutableUInt32(1)
        state.register_file.registers[2] = fixedint.MutableUInt32(-1)
        state.register_file.registers[3] = fixedint.MutableUInt32(3)
        self.assertEqual(
            state.register_file.reg_repr()[1][0],
            "00000000 00000000 00000000 00000001",
        )
        self.assertEqual(state.register_file.reg_repr()[1][1], 1)
        self.assertEqual(state.register_file.reg_repr()[1][2], "00 00 00 01")
        self.assertEqual(
            state.register_file.reg_repr()[2][0],
            "11111111 11111111 11111111 11111111",
        )
        self.assertEqual(state.register_file.reg_repr()[2][1], 4294967295)
        self.assertEqual(state.register_file.reg_repr()[2][2], "FF FF FF FF")
        self.assertEqual(
            state.register_file.reg_repr()[3][0],
            "00000000 00000000 00000000 00000011",
        )
        self.assertEqual(state.register_file.reg_repr()[3][1], 3)
        self.assertEqual(state.register_file.reg_repr()[3][2], "00 00 00 03")

    def test_mem(self):
        # test the wordwise repr method
        state = RiscvArchitecturalState(memory=Memory(min_bytes=0))
        state.memory.write_word(0, fixedint.MutableUInt32(1))
        state.memory.write_word(6, fixedint.MutableUInt32(6))
        state.memory.write_byte(21, fixedint.MutableUInt32(20))
        self.assertEqual(
            state.memory.memory_wordwise_repr()[0][0],
            "00000000 00000000 00000000 00000001",
        )
        self.assertEqual(state.memory.memory_wordwise_repr()[0][1], "1")
        self.assertEqual(state.memory.memory_wordwise_repr()[0][2], "00 00 00 01")
        self.assertEqual(
            state.memory.memory_wordwise_repr()[4][0],
            "00000000 00000110 00000000 00000000",
        )
        self.assertEqual(state.memory.memory_wordwise_repr()[4][1], str(6 << 16))
        self.assertEqual(state.memory.memory_wordwise_repr()[4][2], "00 06 00 00")
        self.assertEqual(
            state.memory.memory_wordwise_repr()[8][0],
            "00000000 00000000 00000000 00000000",
        )
        self.assertEqual(state.memory.memory_wordwise_repr()[8][1], "0")
        self.assertEqual(state.memory.memory_wordwise_repr()[8][2], "00 00 00 00")
        self.assertEqual(
            state.memory.memory_wordwise_repr()[20][0],
            "00000000 00000000 00010100 00000000",
        )
        self.assertEqual(state.memory.memory_wordwise_repr()[20][1], str(20 << 8))
        self.assertEqual(state.memory.memory_wordwise_repr()[20][2], "00 00 14 00")

        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=()), memory=Memory(min_bytes=0)
        )
        # store_byte test
        state.memory.write_byte(0, fixedint.MutableUInt8(1))
        self.assertEqual(state.memory.read_byte(0), fixedint.MutableUInt8(1))

        # store_byte type test
        state.memory.write_byte(0, fixedint.MutableUInt8(1))
        self.assertIsInstance(state.memory.read_byte(0), fixedint.MutableUInt8)

        # store_halfword test
        state.memory.write_halfword(0, fixedint.MutableUInt16(1))
        self.assertEqual(state.memory.read_halfword(0), fixedint.MutableUInt16(1))

        # store_halfword type test
        state.memory.write_halfword(0, fixedint.MutableUInt16(1))
        self.assertIsInstance(state.memory.read_halfword(0), fixedint.MutableUInt16)

        # store_word test
        state.memory.write_word(0, fixedint.MutableUInt32(1))
        self.assertEqual(state.memory.read_word(0), fixedint.MutableUInt32(1))

        # store_word type test
        state.memory.write_word(0, fixedint.MutableUInt32(1))
        self.assertIsInstance(state.memory.read_word(0), fixedint.MutableUInt32)

        # store_byte negative value test
        state.memory.write_byte(0, fixedint.MutableUInt8(-1))
        self.assertEqual(state.memory.read_byte(0), fixedint.MutableUInt8(-1))

        # store_halfword negative value test
        state.memory.write_halfword(0, fixedint.MutableUInt16(-1))
        self.assertEqual(state.memory.read_halfword(0), fixedint.MutableUInt16(-1))

        # store_word test
        state.memory.write_word(0, fixedint.MutableUInt32(-1))
        self.assertEqual(state.memory.read_word(0), fixedint.MutableUInt32(-1))

        # tests are now with 16 bit length of memory
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=()),
            memory=Memory(memory_file={}, address_length=16, min_bytes=0),
        )

        # store_byte test
        state.memory.write_byte(pow(2, 16), fixedint.MutableUInt8(2))
        self.assertEqual(state.memory.read_word(0), fixedint.MutableUInt32(2))

        # store_halfword test
        state.memory.write_halfword(pow(2, 16), fixedint.MutableUInt16(3))
        self.assertEqual(state.memory.read_halfword(0), fixedint.MutableUInt16(3))

        # store_word test
        state.memory.write_word(pow(2, 16), fixedint.MutableUInt32(4))
        self.assertEqual(state.memory.read_word(0), fixedint.MutableUInt32(4))

    def test_unified_memory(self):
        state = RiscvArchitecturalState()

        # Save instr tests:
        state.instruction_memory.write_instruction(
            address=0, instr=ADD(rd=0, rs1=0, rs2=0)
        )
        self.assertEqual(
            state.instruction_memory.instructions[0], ADD(rd=0, rs1=0, rs2=0)
        )
        state.instruction_memory.write_instruction(
            address=2**14 - 4, instr=ADD(rd=1, rs1=2, rs2=3)
        )
        self.assertEqual(
            state.instruction_memory.instructions[2**14 - 4], ADD(rd=1, rs1=2, rs2=3)
        )

        # Illegal access out of bounds of instr memory
        with self.assertRaises(MemoryAddressError) as cm:
            state.instruction_memory.write_instruction(
                address=2**14, instr=ADD(rd=1, rs1=2, rs2=3)
            )
        self.assertEqual(
            cm.exception,
            MemoryAddressError(
                address=2**14,
                min_address_incl=0,
                max_address_incl=2**14 - 1,
                memory_type="instruction memory",
            ),
        )

        with self.assertRaises(MemoryAddressError) as cm:
            state.instruction_memory.write_instruction(
                address=-1, instr=ADD(rd=1, rs1=2, rs2=3)
            )
        self.assertEqual(
            cm.exception,
            MemoryAddressError(
                address=-1,
                min_address_incl=0,
                max_address_incl=2**14 - 1,
                memory_type="instruction memory",
            ),
        )

        # load instr tests:
        self.assertEqual(
            state.instruction_memory.read_instruction(0), ADD(rd=0, rs1=0, rs2=0)
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(2**14 - 4),
            ADD(rd=1, rs1=2, rs2=3),
        )

        with self.assertRaises(KeyError):
            state.instruction_memory.read_instruction(4)

        with self.assertRaises(MemoryAddressError):
            state.instruction_memory.read_instruction(2**14)

        self.assertEqual(
            state.memory.read_byte(address=2**14), fixedint.MutableUInt8(0)
        )
        self.assertEqual(
            state.memory.read_byte(address=2**32 - 1), fixedint.MutableUInt8(0)
        )

        with self.assertRaises(MemoryAddressError) as cm:
            state.memory.read_byte(address=2**14 - 1)
        self.assertEqual(
            cm.exception,
            MemoryAddressError(
                address=2**14 - 1,
                min_address_incl=2**14,
                max_address_incl=2**32 - 1,
                memory_type="data memory",
            ),
        )

        with self.assertRaises(MemoryAddressError) as cm:
            state.memory.read_byte(address=2**32)
        self.assertEqual(
            cm.exception,
            MemoryAddressError(
                address=0,
                min_address_incl=2**14,
                max_address_incl=2**32 - 1,
                memory_type="data memory",
            ),
        )

        with self.assertRaises(MemoryAddressError) as cm:
            state.memory.read_word(address=2**14 - 4)
        self.assertEqual(
            cm.exception,
            MemoryAddressError(
                address=2**14 - 4,
                min_address_incl=2**14,
                max_address_incl=2**32 - 1,
                memory_type="data memory",
            ),
        )

        with self.assertRaises(MemoryAddressError) as cm:
            state.memory.read_word(address=2**32)
        self.assertEqual(
            cm.exception,
            MemoryAddressError(
                address=0,
                min_address_incl=2**14,
                max_address_incl=2**32 - 1,
                memory_type="data memory",
            ),
        )

    def test_instruction_memory(self):
        state = RiscvArchitecturalState()
        with self.assertRaises(InstructionMemoryKeyError) as cm:
            state.instruction_memory.read_instruction(1)
        self.assertEqual(cm.exception, InstructionMemoryKeyError(1))
