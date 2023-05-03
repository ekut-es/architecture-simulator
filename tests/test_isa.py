import unittest
import fixedint

from architecture_simulator.uarch.architectural_state import RegisterFile
from architecture_simulator.isa.rv32i_instructions import ADD, SUB, SLL
from architecture_simulator.uarch.architectural_state import ArchitecturalState

from architecture_simulator.isa.parser import riscv_bnf, riscv_parser


class TestInstructions(unittest.TestCase):
    def test_add(self):
        # Number definitions
        num_min = fixedint.MutableUInt32(2147483648)
        num_minus_7 = fixedint.MutableUInt32(4294967289)
        num_minus_2 = fixedint.MutableUInt32(4294967294)
        num_minus_1 = fixedint.MutableUInt32(4294967295)
        num_0 = fixedint.MutableUInt32(0)
        num_1 = fixedint.MutableUInt32(1)
        num_9 = fixedint.MutableUInt32(9)
        num_16 = fixedint.MutableUInt32(16)
        num_max = fixedint.MutableUInt32(2147483647)

        # smallest number + biggest number = -1
        add = ADD(rs1=1, rs2=0, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_min, num_max])
        )
        state = add.behavior(state)
        self.assertEqual(state.register_file.registers, [num_max, num_min, num_minus_1])

        # smallest number + smallest number = 0
        add = ADD(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_min, num_min, num_minus_1])
        )
        state = add.behavior(state)
        self.assertEqual(state.register_file.registers, [num_min, num_min, num_0])

        # biggest number + biggest number = -2
        add = ADD(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_max, num_0])
        )
        state = add.behavior(state)
        self.assertEqual(state.register_file.registers, [num_max, num_max, num_minus_2])

        # 16 + (-7) = 9 non edge case addition
        add = ADD(rs1=3, rs2=4, rd=1)
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[num_max, num_max, num_0, num_16, num_minus_7]
            )
        )
        state = add.behavior(state)
        self.assertEqual(
            state.register_file.registers, [num_max, num_9, num_0, num_16, num_minus_7]
        )

        # 0 + 0 = 0 :)
        add = ADD(rs1=2, rs2=2, rd=1)
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[num_max, num_max, num_0, num_16, num_minus_7]
            )
        )
        state = add.behavior(state)
        self.assertEqual(
            state.register_file.registers, [num_max, num_0, num_0, num_16, num_minus_7]
        )

        # biggest number + 1 = smallest number
        add = ADD(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_1, num_16])
        )
        state = add.behavior(state)
        self.assertEqual(state.register_file.registers, [num_max, num_1, num_min])

    def test_sub(self):
        # Number definitions
        num_min = fixedint.MutableUInt32(2147483648)
        num_minus_1 = fixedint.MutableUInt32(4294967295)
        num_0 = fixedint.MutableUInt32(0)
        num_1 = fixedint.MutableUInt32(1)
        num_8 = fixedint.MutableUInt32(8)
        num_15 = fixedint.MutableUInt32(15)
        num_23 = fixedint.MutableUInt32(23)
        num_max = fixedint.MutableUInt32(2147483647)

        # smallest number - smallest number = 0
        sub = SUB(rs1=0, rs2=0, rd=1)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_min, num_15])
        )
        state = sub.behavior(state)
        self.assertEqual(state.register_file.registers, [num_min, num_0])

        # biggest number - biggest number = 0
        sub = SUB(rs1=0, rs2=0, rd=1)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_15])
        )
        state = sub.behavior(state)
        self.assertEqual(state.register_file.registers, [num_max, num_0])

        # smallest number - biggest number = 1
        sub = SUB(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_min, num_max, num_0])
        )
        state = sub.behavior(state)
        self.assertEqual(state.register_file.registers, [num_min, num_max, num_1])

        # biggest number - smallest number = -1
        sub = SUB(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_min, num_0])
        )
        state = sub.behavior(state)
        self.assertEqual(state.register_file.registers, [num_max, num_min, num_minus_1])

        # smallest number - 1 = biggest number
        sub = SUB(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_min, num_1, num_0])
        )
        state = sub.behavior(state)
        self.assertEqual(state.register_file.registers, [num_min, num_1, num_max])

        # biggest number - (-1) = smallest number
        sub = SUB(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_minus_1, num_0])
        )
        state = sub.behavior(state)
        self.assertEqual(state.register_file.registers, [num_max, num_minus_1, num_min])

        # 23 - 8 = 15
        sub = SUB(rs1=1, rs2=0, rd=0)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_8, num_23])
        )
        state = sub.behavior(state)
        self.assertEqual(state.register_file.registers, [num_15, num_23])

    def test_sll(self):
        # Number definitions
        num_max = fixedint.MutableUInt32(4294967295)
        num_msb = fixedint.MutableUInt32(2147483648)
        num_0 = fixedint.MutableUInt32(0)
        num_1 = fixedint.MutableUInt32(1)
        num_16 = fixedint.MutableUInt32(16)
        num_31 = fixedint.MutableUInt32(31)
        num_32 = fixedint.MutableUInt32(32)
        num_580 = fixedint.MutableUInt32(580)

        # only most significant bit set shifted by one = zero
        sll = SLL(rs1=1, rs2=2, rd=0)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_msb, num_1])
        )
        state = sll.behavior(state)
        self.assertEqual(state.register_file.registers, [num_0, num_msb, num_1])

        # FFFFFFFF shifted by 31 = only most significant bit set
        sll = SLL(rs1=1, rs2=2, rd=0)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_0, num_max, num_31])
        )
        state = sll.behavior(state)
        self.assertEqual(state.register_file.registers, [num_msb, num_max, num_31])

        # shif by zero only writes state
        sll = SLL(rs1=1, rs2=0, rd=4)
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[num_0, num_max, num_31, num_580, num_msb]
            )
        )
        state = sll.behavior(state)
        self.assertEqual(
            state.register_file.registers, [num_0, num_max, num_31, num_580, num_max]
        )

        # shift by 32 will write zero
        sll = SLL(rs1=1, rs2=0, rd=4)
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[num_32, num_max, num_31, num_580, num_msb]
            )
        )
        state = sll.behavior(state)
        self.assertEqual(
            state.register_file.registers, [num_32, num_max, num_31, num_580, num_0]
        )

        # higher bits do not affect shift amount
        sll = SLL(rs1=1, rs2=2, rd=3)
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[num_32, num_1, num_580, num_580, num_0]
            )
        )
        state = sll.behavior(state)
        self.assertEqual(
            state.register_file.registers, [num_32, num_1, num_580, num_16, num_0]
        )

    def test_slt(self):
        pass

    def test_sltu(self):
        pass

    def test_xor(self):
        pass

    def test_srl(self):
        pass

    def test_sra(self):
        pass

    def test_or(self):
        pass

    def test_and(self):
        pass


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
