import unittest
import fixedint

from architecture_simulator.uarch.architectural_state import RegisterFile, Memory
from architecture_simulator.isa.rv32i_instructions import (
    ADD,
    SUB,
    SB,
    SH,
    SW,
    LUI,
    AUIPC,
    JAL,
    fence,
)
from architecture_simulator.uarch.architectural_state import ArchitecturalState

from architecture_simulator.isa.parser import riscv_bnf, riscv_parser


class TestInstructions(unittest.TestCase):
    def test_add(self):
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[0, 5, 9, 0]),
            memory=Memory(memory_file=()),
        )
        add_1 = ADD(rs1=1, rs2=2, rd=0)
        state = add_1.behavior(state)
        self.assertEqual(state.register_file.registers, [14, 5, 9, 0])

    def test_sub(self):
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[0, 5, 9, 0]),
            memory=Memory(memory_file=()),
        )
        sub_1 = SUB(rs1=1, rs2=2, rd=0)
        state = sub_1.behavior(state)
        self.assertEqual(state.register_file.registers, [-4, 5, 9, 0])

    def test_mem(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=()))
        # store_byte test
        state.memory.store_byte(0, fixedint.MutableUInt8(1))
        self.assertEqual(state.memory.load_byte(0), fixedint.MutableUInt8(1))

        # store_halfword test
        state.memory.store_halfword(0, fixedint.MutableUInt16(1))
        self.assertEqual(state.memory.load_halfword(0), fixedint.MutableUInt16(1))

        # store_word test
        state.memory.store_word(0, fixedint.MutableUInt32(1))
        self.assertEqual(state.memory.load_word(0), fixedint.MutableUInt32(1))

        # store_byte negative value test
        state.memory.store_byte(0, fixedint.MutableUInt8(-1))
        self.assertEqual(state.memory.load_byte(0), fixedint.MutableUInt8(-1))

        # store_halfword negative value test
        state.memory.store_halfword(0, fixedint.MutableUInt16(-1))
        self.assertEqual(state.memory.load_halfword(0), fixedint.MutableUInt16(-1))

        # store_word test
        state.memory.store_word(0, fixedint.MutableUInt32(-1))
        self.assertEqual(state.memory.load_word(0), fixedint.MutableUInt32(-1))

    def test_sb(self):
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(5),
                    fixedint.MutableUInt32(257),
                    fixedint.MutableUInt32(0),
                ]
            ),
            # memory=Memory(memory_file=()),
        )

        sb_1 = SB(rs1=1, rs2=2, imm=1, mnemonic="sb")
        state = sb_1.behavior(state)
        self.assertEqual(state.memory.memory_file[6], 1)

    def test_sh(self):
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(5),
                    fixedint.MutableUInt32(9),
                    fixedint.MutableUInt32(0),
                ]
            ),
            # memory=Memory(memory_file=()),
        )

        sh_1 = SH(rs1=1, rs2=2, imm=1, mnemonic="sh")
        state = sh_1.behavior(state)
        self.assertEqual(int(state.memory.memory_file[6]), 9)

    def test_sw(self):
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(5),
                    fixedint.MutableUInt32(65536),
                    fixedint.MutableUInt32(0),
                ]
            ),
            # memory=Memory(memory_file=()),
        )

        sw_1 = SW(rs1=1, rs2=2, imm=1, mnemonic="sw")
        state = sw_1.behavior(state)
        self.assertEqual(int(state.memory.memory_file[6]), 0)

    def test_lui(self):
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[0, 5, 9, 0]),
            # memory=Memory(memory_file=()),
        )

        lui_1 = LUI(rd=1, imm=2)
        state = lui_1.behavior(state)
        self.assertEqual(int(state.register_file.registers[1]), 8192)

        lui_2 = LUI(rd=0, imm=20)
        state = lui_2.behavior(state)
        self.assertEqual(int(state.register_file.registers[0]), 81920)

    def test_auipc(self):
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[0, 5, 9, 0]),
            # memory=Memory(memory_file=()),
        )

        state.program_counter = 0
        auipc_1 = AUIPC(rd=1, imm=2)
        state = auipc_1.behavior(state)
        self.assertEqual(int(state.register_file.registers[1]), 8192)

        state.program_counter = 3
        auipc_1 = AUIPC(rd=1, imm=2)
        state = auipc_1.behavior(state)
        self.assertEqual(int(state.register_file.registers[1]), 8195)

    def test_jal(self):
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[1, 1, 1]),
            # memory=Memory(memory_file=()),
        )
        state.program_counter = 0
        jal_1 = JAL(rd=0, imm=2)
        state = jal_1.behavior(state)
        self.assertEqual(state.program_counter, 0)
        self.assertEqual(int(state.register_file.registers[0]), 4)

        state.program_counter = 3
        jal_2 = JAL(rd=1, imm=3)
        state = jal_2.behavior(state)
        self.assertEqual(state.program_counter, 5)
        self.assertEqual(int(state.register_file.registers[1]), 7)


class TestParser(unittest.TestCase):
    program = """
add x0,x1,x2

# foo
# sub x1, x2, x4
"""
    expected = [
        ["add", ["x", "0"], ["x", "1"], ["x", "2"]],
        # ["sub", ["x", "1"], ["x", "2"], ["x", "4"]],
    ]

    def test_bnf(self):
        instr = riscv_bnf().parse_string(self.program)
        self.assertEqual(instr.as_list(), self.expected)
        self.assertNotEqual(instr[0].mnemonic, "")
        # self.assertEqual(instr[1].mnemonic, "")

    def test_parser(self):
        instr = riscv_parser(self.program)
        self.assertIsInstance(instr[0], ADD)
        self.assertEqual(instr[0].rd, 0)
        self.assertEqual(instr[0].rs1, 1)
        self.assertEqual(instr[0].rs2, 2)
        # self.assertIsInstance(instr[1], SUB)
        # self.assertEqual(instr[1].rd, 1)
        # self.assertEqual(instr[1].rs1, 2)
        # self.assertEqual(instr[1].rs2, 4)
