import unittest
import fixedint

from architecture_simulator.uarch.architectural_state import RegisterFile
from architecture_simulator.isa.rv32i_instructions import (
    ADD,
    BEQ,
    BLT,
    BNE,
    BTypeInstruction,
    SUB,
)
from architecture_simulator.uarch.architectural_state import ArchitecturalState

from architecture_simulator.isa.parser import riscv_bnf, riscv_parser


class TestInstructions(unittest.TestCase):
    def test_add(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 5, 9, 0]))
        add_1 = ADD(rs1=1, rs2=2, rd=0)
        state = add_1.behavior(state)
        self.assertEqual(state.register_file.registers, [14, 5, 9, 0])

    def test_sub(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 5, 9, 0]))
        sub_1 = SUB(rs1=1, rs2=2, rd=0)
        state = sub_1.behavior(state)
        self.assertEqual(state.register_file.registers, [-4, 5, 9, 0])

    def test_btype(self):
        try:
            BTypeInstruction(0, 0, 0, mnemonic="x")
            BTypeInstruction(0, 0, 2047, mnemonic="x")
            BTypeInstruction(0, 0, -2048, mnemonic="x")
        except Exception:
            print(Exception)
            self.fail("BTypeInstruction raised an exception upon instantiation")
        with self.assertRaises(ValueError):
            BTypeInstruction(0, 0, -2049, mnemonic="x")
        with self.assertRaises(ValueError):
            BTypeInstruction(0, 0, 2048, mnemonic="x")

    def test_beq(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 0, 1]))

        state.program_counter = 0
        beq_1 = BEQ(0, 1, 6)
        state = beq_1.behavior(state)
        self.assertEqual(state.program_counter, 8)

        state.program_counter = 0
        beq_2 = BEQ(0, 2, 6)
        state = beq_2.behavior(state)
        self.assertEqual(state.program_counter, 0)

        state.program_counter = 32
        beq_1 = BEQ(0, 1, -6)
        state = beq_1.behavior(state)
        self.assertEqual(state.program_counter, 16)

    def test_bne(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 0, 1]))

        state.program_counter = 0
        bne_1 = BNE(0, 1, 6)
        state = bne_1.behavior(state)
        self.assertEqual(state.program_counter, 0)

        state.program_counter = 0
        bne_2 = BNE(0, 2, 6)
        state = bne_2.behavior(state)
        self.assertEqual(state.program_counter, 8)

        state.program_counter = 32
        bne_2 = BNE(0, 2, -6)
        state = bne_2.behavior(state)
        self.assertEqual(state.program_counter, 16)

    def test_blt(self):
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[0, 0, 1, pow(2, 32) - 1, pow(2, 31)])
        )

        state.program_counter = 0
        blt_1 = BLT(0, 1, 6)
        state = blt_1.behavior(state)
        self.assertEqual(state.program_counter, 0)

        state.program_counter = 0
        blt_2 = BLT(2, 0, 6)
        state = blt_2.behavior(state)
        self.assertEqual(state.program_counter, 0)

        state.program_counter = 0
        blt_2 = BLT(0, 2, 6)
        state = blt_2.behavior(state)
        self.assertEqual(state.program_counter, 8)

        state.program_counter = 32
        blt_2 = BLT(0, 2, -6)
        state = blt_2.behavior(state)
        self.assertEqual(state.program_counter, 16)

        state.program_counter = 0
        blt_2 = BLT(0, 3, 6)
        state = blt_2.behavior(state)
        self.assertEqual(state.program_counter, 0)

        state.program_counter = 0
        blt_2 = BLT(3, 0, 6)
        state = blt_2.behavior(state)
        self.assertEqual(state.program_counter, 8)

        state.program_counter = 0
        blt_2 = BLT(4, 3, 6)
        state = blt_2.behavior(state)
        self.assertEqual(state.program_counter, 8)


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
