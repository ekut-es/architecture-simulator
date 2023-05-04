import unittest
import fixedint

from architecture_simulator.uarch.architectural_state import RegisterFile
from architecture_simulator.isa.rv32i_instructions import (
    ADD,
    SUB,
    SLL,
    SLT,
    SLTU,
    XOR,
    SRL,
    SRA,
    OR,
    AND,
)
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
        num_612 = fixedint.MutableUInt32(612)

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
                registers=[num_0, num_max, num_31, num_612, num_msb]
            )
        )
        state = sll.behavior(state)
        self.assertEqual(
            state.register_file.registers, [num_0, num_max, num_31, num_612, num_max]
        )

        # higher bits do not affect shift amount
        sll = SLL(rs1=1, rs2=2, rd=3)
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[num_612, num_1, num_612, num_612, num_0]
            )
        )
        state = sll.behavior(state)
        self.assertEqual(
            state.register_file.registers, [num_612, num_1, num_612, num_16, num_0]
        )

    def test_slt(self):
        # Number definitions
        num_min = fixedint.MutableUInt32(2147483648)
        num_max = fixedint.MutableUInt32(2147483647)
        num_0 = fixedint.MutableUInt32(0)
        num_1 = fixedint.MutableUInt32(1)
        num_77 = fixedint.MutableUInt32(77)

        # equivalenz leads to 0
        slt = SLT(rs1=1, rs2=0, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_77, num_77, num_77])
        )
        state = slt.behavior(state)
        self.assertEqual(state.register_file.registers, [num_77, num_77, num_0])
        # numbers are treated as signed
        slt = SLT(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_min, num_max, num_77])
        )
        state = slt.behavior(state)
        self.assertEqual(state.register_file.registers, [num_min, num_max, num_1])
        # rs1 beeing smaller by one leads to 1
        slt = SLT(rs1=1, rs2=2, rd=0)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_min, num_0, num_1])
        )
        state = slt.behavior(state)
        self.assertEqual(state.register_file.registers, [num_1, num_0, num_1])
        # rs1 beeing greater by one leads to 0
        slt = SLT(rs1=1, rs2=2, rd=0)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_min, num_1, num_0])
        )
        state = slt.behavior(state)
        self.assertEqual(state.register_file.registers, [num_0, num_1, num_0])

    def test_sltu(self):
        # Number definitions
        num_0 = fixedint.MutableUInt32(0)
        num_max = fixedint.MutableUInt32(4294967295)
        num_1 = fixedint.MutableUInt32(1)
        num_77 = fixedint.MutableUInt32(77)

        # equivalenz leads to 0
        sltu = SLTU(rs1=1, rs2=0, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_77, num_77, num_77])
        )
        state = sltu.behavior(state)
        self.assertEqual(state.register_file.registers, [num_77, num_77, num_0])
        # numbers are treated as unsigned
        sltu = SLTU(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_0, num_77])
        )
        state = sltu.behavior(state)
        self.assertEqual(state.register_file.registers, [num_max, num_0, num_0])
        # rs1 beeing smaller by one leads to 1
        sltu = SLTU(rs1=1, rs2=2, rd=0)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_0, num_1])
        )
        state = sltu.behavior(state)
        self.assertEqual(state.register_file.registers, [num_1, num_0, num_1])
        # rs1 beeing greater by one leads to 0
        sltu = SLTU(rs1=1, rs2=2, rd=0)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_1, num_0])
        )
        state = sltu.behavior(state)
        self.assertEqual(state.register_file.registers, [num_0, num_1, num_0])

    def test_xor(self):
        num_all_but_msb = fixedint.MutableUInt32(2147483647)
        num_msb = fixedint.MutableUInt32(2147483648)
        num_all_bits = fixedint.MutableUInt32(4294967295)
        num_0 = fixedint.MutableUInt32(0)

        num_a = fixedint.MutableUInt32(4294902015)  # FF FF 00 FF
        num_b = fixedint.MutableUInt32(4294905615)  # FF FF 0F 0F
        num_c = fixedint.MutableUInt32(4080)  # 00 00 0F F0

        xor = XOR(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_all_but_msb, num_all_bits, num_0])
        )
        state = xor.behavior(state)
        self.assertEqual(
            state.register_file.registers, [num_all_but_msb, num_all_bits, num_msb]
        )

        xor = XOR(rs1=3, rs2=4, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[num_all_but_msb, num_all_bits, num_0, num_a, num_b]
            )
        )
        state = xor.behavior(state)
        self.assertEqual(
            state.register_file.registers,
            [num_all_but_msb, num_all_bits, num_c, num_a, num_b],
        )

    def test_srl(self):
        # Number definitions
        num_max = fixedint.MutableUInt32(4294967295)
        num_0 = fixedint.MutableUInt32(0)
        num_1 = fixedint.MutableUInt32(1)
        num_31 = fixedint.MutableUInt32(31)
        num_612 = fixedint.MutableUInt32(612)

        # one shifted by one = zero
        srl = SRL(rs1=1, rs2=2, rd=0)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_1, num_1])
        )
        state = srl.behavior(state)
        self.assertEqual(state.register_file.registers, [num_0, num_1, num_1])

        # FFFFFFFF shifted by 31 = one
        srl = SRL(rs1=0, rs2=1, rd=0)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_31, num_612])
        )
        state = srl.behavior(state)
        self.assertEqual(state.register_file.registers, [num_1, num_31, num_612])

        # shif by zero only writes state
        srl = SRL(rs1=0, rs2=1, rd=0)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_0, num_612])
        )
        state = srl.behavior(state)
        self.assertEqual(state.register_file.registers, [num_max, num_0, num_612])

        # higher bits do not affect shift amount
        srl = SRL(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_31, num_612, num_612])
        )
        state = srl.behavior(state)
        self.assertEqual(state.register_file.registers, [num_31, num_612, num_1])

    def test_sra(self):
        # Number definitions
        num_all_set = fixedint.MutableUInt32(4294967295)
        num_msb_set = fixedint.MutableUInt32(2147483648)
        num_second_set = fixedint.MutableUInt32(1073741824)
        num_0 = fixedint.MutableUInt32(0)
        num_1 = fixedint.MutableUInt32(1)
        num_30 = fixedint.MutableUInt32(30)
        num_31 = fixedint.MutableUInt32(31)
        num_38 = fixedint.MutableUInt32(38)
        num_612 = fixedint.MutableUInt32(612)
        num_2pow26 = fixedint.MutableUInt32(67108864)

        # negative numbers get extended with one´s
        sra = SRA(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_msb_set, num_31, num_0])
        )
        state = sra.behavior(state)
        self.assertEqual(
            state.register_file.registers, [num_msb_set, num_31, num_all_set]
        )
        # positive numbers get extended with zero´s
        sra = SRA(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_second_set, num_30, num_all_set])
        )
        state = sra.behavior(state)
        self.assertEqual(state.register_file.registers, [num_second_set, num_30, num_1])

        # shift amount only affected by 5 lower bits
        sra = SRA(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_second_set, num_612, num_all_set])
        )
        state = sra.behavior(state)
        self.assertEqual(
            state.register_file.registers, [num_second_set, num_612, num_2pow26]
        )
        # percision test
        sra = SRA(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_612, num_612, num_all_set])
        )
        state = sra.behavior(state)
        self.assertEqual(state.register_file.registers, [num_612, num_612, num_38])

    def test_or(self):
        num_a = fixedint.MutableUInt32(16711698)  # 00 FF 00 12
        num_b = fixedint.MutableUInt32(252641280)  # 0F 0F 00 00
        num_c = fixedint.MutableUInt32(268369938)  # 0F FF 00 12

        # Test bit wise behavior
        or_inst = OR(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_a, num_b, num_a])
        )
        state = or_inst.behavior(state)
        self.assertEqual(state.register_file.registers, [num_a, num_b, num_c])

        # Test kommutativity
        or_inst = OR(rs1=1, rs2=0, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_a, num_b, num_a])
        )
        state = or_inst.behavior(state)
        self.assertEqual(state.register_file.registers, [num_a, num_b, num_c])

    def test_and(self):
        num_a = fixedint.MutableUInt32(16711698)  # 00 FF 00 12
        num_b = fixedint.MutableUInt32(252641280)  # 0F 0F 00 00
        num_c = fixedint.MutableUInt32(983040)  # 00 0F 00 00

        # Test bit wise behavior
        and_inst = AND(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_a, num_b, num_a])
        )
        state = and_inst.behavior(state)
        self.assertEqual(state.register_file.registers, [num_a, num_b, num_c])

        # Test kommutativity
        and_inst = AND(rs1=1, rs2=0, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_a, num_b, num_a])
        )
        state = and_inst.behavior(state)
        self.assertEqual(state.register_file.registers, [num_a, num_b, num_c])


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
