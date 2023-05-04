import unittest
import fixedint

from architecture_simulator.uarch.architectural_state import RegisterFile
from architecture_simulator.uarch.architectural_state import Memory
from architecture_simulator.isa.rv32i_instructions import ADD, SUB, LB, LH, LW, LBU, LHU
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

    def test_lb(self):
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[0, 1, -1, pow(2, 32) - 1]),
            memory=Memory(
                memory_file=dict(
                    [
                        (0, fixedint.MutableUInt8(1)),
                        (1, fixedint.MutableUInt8(2)),
                        (2, fixedint.MutableUInt8(3)),
                        (pow(2, 32) - 1, fixedint.MutableUInt8(4)),
                    ]
                )
            ),
        )
        # imm=0, rs1=0
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=0, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1, 1, -1, pow(2, 32) - 1])

        # imm=1, rs1=0
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=1, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [2, 1, -1, pow(2, 32) - 1])

        # imm=0, rs1=1
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=0, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [2, 1, -1, pow(2, 32) - 1])

        # imm=1, rs1=1
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=1, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [3, 1, -1, pow(2, 32) - 1])

        # imm=1, rs1=-1
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=1, rs1=2, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1, 1, -1, pow(2, 32) - 1])

        # imm=1, rs1=2^32-1
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=1, rs1=3, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1, 1, -1, pow(2, 32) - 1])

        # imm=0, rs1=-1 negative value of -1 gets converted to 2^32-1
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=0, rs1=2, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [4, 1, -1, pow(2, 32) - 1])

        # try memory acces to non existant address
        with self.assertRaises(KeyError):
            instr = LH(imm=3, rs1=0, rd=0)
            state = instr.behavior(state)

    def test_lh(self):
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[0, 2, -2, pow(2, 32) - 1]),
            memory=Memory(
                memory_file=dict(
                    [
                        (0, fixedint.MutableUInt8(1)),
                        (1, fixedint.MutableUInt8(2)),
                        (2, fixedint.MutableUInt8(3)),
                        (3, fixedint.MutableUInt8(4)),
                        (4, fixedint.MutableUInt8(5)),
                        (5, fixedint.MutableUInt8(6)),
                        (pow(2, 32) - 2, fixedint.MutableUInt8(7)),
                        (pow(2, 32) - 1, fixedint.MutableUInt8(8)),
                    ]
                )
            ),
        )
        # imm=0, rs1=0
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LH(imm=0, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [513, 2, -2, pow(2, 32) - 1])

        # imm=2, rs1=0
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LH(imm=2, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1027, 2, -2, pow(2, 32) - 1])

        # imm=0, rs1=2
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LH(imm=0, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1027, 2, -2, pow(2, 32) - 1])

        # imm=2, rs1=2
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LH(imm=2, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1541, 2, -2, pow(2, 32) - 1])

        # imm=2, rs1=-2
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LH(imm=2, rs1=2, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [513, 2, -2, pow(2, 32) - 1])

        # imm=1, rs1=2^32-1 equates to 0
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LH(imm=1, rs1=3, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [513, 2, -2, pow(2, 32) - 1])

        # imm=1, rs1=2 align error on memory address 3
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LH(imm=1, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1284, 2, -2, pow(2, 32) - 1])

        # imm=0, rs1=-2 negative value of -2 gets converted to 2^32-2
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LH(imm=0, rs1=2, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [2055, 2, -2, pow(2, 32) - 1])

        # try memory acces to non existant address
        with self.assertRaises(KeyError):
            instr = LH(imm=6, rs1=0, rd=0)
            state = instr.behavior(state)

    def test_lw(self):
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[0, 4, -4, pow(2, 32) - 1]),
            memory=Memory(
                memory_file=dict(
                    [
                        (0, fixedint.MutableUInt8(1)),
                        (1, fixedint.MutableUInt8(1)),
                        (2, fixedint.MutableUInt8(1)),
                        (3, fixedint.MutableUInt8(1)),
                        (4, fixedint.MutableUInt8(2)),
                        (5, fixedint.MutableUInt8(2)),
                        (6, fixedint.MutableUInt8(2)),
                        (7, fixedint.MutableUInt8(2)),
                        (8, fixedint.MutableUInt8(3)),
                        (9, fixedint.MutableUInt8(3)),
                        (10, fixedint.MutableUInt8(3)),
                        (11, fixedint.MutableUInt8(3)),
                        (12, fixedint.MutableUInt8(3)),
                        (pow(2, 32) - 4, fixedint.MutableUInt8(4)),
                        (pow(2, 32) - 3, fixedint.MutableUInt8(4)),
                        (pow(2, 32) - 2, fixedint.MutableUInt8(4)),
                        (pow(2, 32) - 1, fixedint.MutableUInt8(4)),
                    ]
                )
            ),
        )
        # imm=0, rs1=0
        state.register_file.registers = [0, 4, -4, pow(2, 32) - 1]
        instr = LW(imm=0, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers, [16843009, 4, -4, pow(2, 32) - 1]
        )

        # imm=4, rs1=0
        state.register_file.registers = [0, 4, -4, pow(2, 32) - 1]
        instr = LW(imm=4, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers, [33686018, 4, -4, pow(2, 32) - 1]
        )

        # imm=0, rs1=4
        state.register_file.registers = [0, 4, -4, pow(2, 32) - 1]
        instr = LW(imm=0, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers, [33686018, 4, -4, pow(2, 32) - 1]
        )

        # imm=4, rs1=4
        state.register_file.registers = [0, 4, -4, pow(2, 32) - 1]
        instr = LW(imm=4, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers, [50529027, 4, -4, pow(2, 32) - 1]
        )

        # imm=4, rs1=-4
        state.register_file.registers = [0, 4, -4, pow(2, 32) - 1]
        instr = LW(imm=4, rs1=2, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers, [16843009, 4, -4, pow(2, 32) - 1]
        )

        # imm=1, rs1=2^32-1 equates to 0
        state.register_file.registers = [0, 4, -4, pow(2, 32) - 1]
        instr = LW(imm=1, rs1=3, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers, [16843009, 4, -4, pow(2, 32) - 1]
        )

        # imm=1, rs1=4 align error on memory address 5
        state.register_file.registers = [0, 4, -4, pow(2, 32) - 1]
        instr = LW(imm=1, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers, [50463234, 4, -4, pow(2, 32) - 1]
        )

        # imm=0, rs1=-4 negative value of -4 gets converted to 2^32-4
        state.register_file.registers = [0, 4, -4, pow(2, 32) - 1]
        instr = LW(imm=0, rs1=2, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers, [67372036, 4, -4, pow(2, 32) - 1]
        )

        # try memory acces to non existant address
        with self.assertRaises(KeyError):
            instr = LW(imm=13, rs1=0, rd=0)
            state = instr.behavior(state)


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
