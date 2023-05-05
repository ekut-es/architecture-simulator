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
    BGE,
    BLTU,
    BGEU,
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
        # valid immediates
        try:
            BTypeInstruction(0, 0, 0, mnemonic="x")
            BTypeInstruction(0, 0, 2047, mnemonic="x")
            BTypeInstruction(0, 0, -2048, mnemonic="x")
        except Exception:
            print(Exception)
            self.fail("BTypeInstruction raised an exception upon instantiation")

        # invalid immediates
        with self.assertRaises(ValueError):
            BTypeInstruction(0, 0, -2049, mnemonic="x")
        with self.assertRaises(ValueError):
            BTypeInstruction(0, 0, 2048, mnemonic="x")

    def test_beq(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 0, 1]))

        # 0, 0
        state.program_counter = 0
        instruction = BEQ(0, 1, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1
        state.program_counter = 0
        instruction = BEQ(0, 2, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 0, 0 - negative immediate
        state.program_counter = 32
        instruction = BEQ(0, 1, -6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

    def test_bne(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 0, 1]))

        # 0, 0
        state.program_counter = 0
        instruction = BNE(0, 1, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 0, 1
        state.program_counter = 0
        instruction = BNE(0, 2, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1 - negative immediate
        state.program_counter = 32
        instruction = BNE(0, 2, -6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

    def test_blt(self):
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[0, 0, 1, pow(2, 32) - 1, pow(2, 31)])
        )

        # 0, 0
        state.program_counter = 0
        instruction = BLT(0, 1, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 1, 0
        state.program_counter = 0
        instruction = BLT(2, 0, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 0, 1
        state.program_counter = 0
        instruction = BLT(0, 2, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1 - negative immediate
        state.program_counter = 32
        instruction = BLT(0, 2, -6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

        # 0, -1
        state.program_counter = 0
        instruction = BLT(0, 3, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # -1, 0
        state.program_counter = 0
        instruction = BLT(3, 0, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # -2^31, -1
        state.program_counter = 0
        instruction = BLT(4, 3, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

    def test_bge(self):
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[0, 0, 1, pow(2, 32) - 1, pow(2, 31)])
        )

        # 0, 0
        state.program_counter = 0
        instruction = BGE(0, 1, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1
        state.program_counter = 0
        instruction = BGE(0, 2, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 1, 0
        state.program_counter = 0
        instruction = BGE(2, 0, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 1, 0 - negative immediate
        state.program_counter = 32
        instruction = BGE(2, 0, -6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

        # 0, -1
        state.program_counter = 0
        instruction = BGE(0, 3, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # -2^31, -1
        state.program_counter = 0
        instruction = BGE(4, 3, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

    def test_bltu(self):
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[0, 0, 1, pow(2, 32) - 1, pow(2, 31)])
        )

        # 0, 0
        state.program_counter = 0
        instruction = BLTU(0, 1, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 1, 0
        state.program_counter = 0
        instruction = BLTU(2, 0, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 0, 1
        state.program_counter = 0
        instruction = BLTU(0, 2, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1 - negative immediate
        state.program_counter = 32
        instruction = BLTU(0, 2, -6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

        # 0, (2^32 - 1)
        state.program_counter = 0
        instruction = BLTU(0, 3, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # (2^32 - 1), 0
        state.program_counter = 0
        instruction = BLTU(3, 0, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 2^31, (2^32 - 1)
        state.program_counter = 0
        instruction = BLTU(4, 3, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

    def test_bgeu(self):
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[0, 0, 1, pow(2, 32) - 1, pow(2, 31)])
        )

        # 0, 0
        state.program_counter = 0
        instruction = BGEU(0, 1, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1
        state.program_counter = 0
        instruction = BGEU(0, 2, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 1, 0
        state.program_counter = 0
        instruction = BGEU(2, 0, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 1, 0 - negative immediate
        state.program_counter = 32
        instruction = BGEU(2, 0, -6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

        # 0, (2^32 - 1)
        state.program_counter = 0
        instruction = BGEU(0, 3, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 2^31, (2^32 - 1)
        state.program_counter = 0
        instruction = BGEU(4, 3, 6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)


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
