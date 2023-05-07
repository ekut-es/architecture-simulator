import unittest
import fixedint

from architecture_simulator.uarch.architectural_state import RegisterFile
from architecture_simulator.isa.rv32i_instructions import (
    ADD,
    SUB,
    ADDI,
    SLTI,
    SLTIU,
    XORI,
    ORI,
    ANDI,
    SLLI,
    SRLI,
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

    def test_addi(self):
        b0 = fixedint.MutableUInt32(0)
        b1 = fixedint.MutableUInt32(1)
        b5 = fixedint.MutableUInt32(5)
        bmaxint = fixedint.MutableUInt32(pow(2, 31) - 1)
        bminint = fixedint.MutableUInt32(-pow(2, 31))
        bmaximm = fixedint.MutableUInt32(2047)
        bminimm = fixedint.MutableUInt32(-2048)
        bn1 = fixedint.MutableUInt32(-1)
        brandom = fixedint.MutableUInt32(3320171255)
        brandomx = fixedint.MutableUInt32(3320171260)

        # 0 + 0    == 0
        # 0 + 1    == 1
        # 1 + 0    == 1
        # 0 + -1   == -1
        # 1 + -1   == 0
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b1, b0, b1])
        )
        addi_1 = ADDI(rd=0, rs1=0, imm=b0)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=1, rs1=1, imm=b1)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=2, rs1=2, imm=b0)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=3, rs1=3, imm=bn1)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=4, rs1=4, imm=bn1)
        state = addi_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b1, b1, bn1, b0])

        # bmaxint + 1    == bminint
        # bminint + -1   == bmaxint
        # 0 + bmaximm    == 2048
        # 0 + bminimm    == -2047
        # brandom + 5
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[bmaxint, bminint, b0, b0, brandom])
        )
        addi_1 = ADDI(rd=0, rs1=0, imm=b1)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=1, rs1=1, imm=bn1)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=2, rs1=2, imm=bmaximm)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=3, rs1=3, imm=bminimm)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=4, rs1=4, imm=b5)
        state = addi_1.behavior(state)
        self.assertEqual(
            state.register_file.registers,
            [bminint, bmaxint, bmaximm, bminimm, brandomx],
        )

    def test_andi(self):
        b0 = fixedint.MutableUInt32(0)
        b1 = fixedint.MutableUInt32(1)
        b5 = fixedint.MutableUInt32(5)
        bmaxint = fixedint.MutableUInt32(pow(2, 31) - 1)
        bmaximm = fixedint.MutableUInt32(2047)
        bn1 = fixedint.MutableUInt32(-1)
        brandom = fixedint.MutableUInt32(3320171255)

        # 0 & 0    == 0
        # 0 & 1    == 0
        # 1 & 0    == 0
        # 1 & 1    == 1
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b1, b1])
        )
        andi_1 = ANDI(rd=0, rs1=0, imm=b0)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=1, rs1=1, imm=b1)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=2, rs1=2, imm=b0)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=3, rs1=3, imm=b1)
        state = andi_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b0, b0, b1])

        # -1 & 0             == 0
        # -1 & 1             == 1
        # bmaxint & bmaximm  == bmaximm
        # bmaxint & -1       == bmaxint
        # brandom & b5
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[bn1, bn1, bmaxint, bmaxint, brandom])
        )
        andi_1 = ANDI(rd=0, rs1=0, imm=b0)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=1, rs1=1, imm=b1)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=2, rs1=2, imm=bmaximm)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=3, rs1=3, imm=bn1)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=4, rs1=4, imm=b5)
        state = andi_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b1, bmaximm, bmaxint, b5])

    def test_ori(self):
        b0 = fixedint.MutableUInt32(0)
        b1 = fixedint.MutableUInt32(1)
        b5 = fixedint.MutableUInt32(5)
        bminimm = fixedint.MutableUInt32(-2048)
        bn1 = fixedint.MutableUInt32(-1)
        brandom = fixedint.MutableUInt32(3320171255)

        # 0 | 0  == 0
        # 0 | 1  == 1
        # 1 | 0  == 1
        # 1 | 1  == 1
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b1, b1])
        )
        ori_1 = ORI(rd=0, rs1=0, imm=b0)
        state = ori_1.behavior(state)
        ori_1 = ORI(rd=1, rs1=1, imm=b1)
        state = ori_1.behavior(state)
        ori_1 = ORI(rd=2, rs1=2, imm=b0)
        state = ori_1.behavior(state)
        ori_1 = ORI(rd=3, rs1=3, imm=b1)
        state = ori_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b1, b1, b1])

        # -1 | 0       == -1
        # -1 | -1      == -1
        # 0 | bminimm  == bminimm
        # brandom | 5  == brandom
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[bn1, bn1, b0, brandom])
        )
        ori_1 = ORI(rd=0, rs1=0, imm=b0)
        state = ori_1.behavior(state)
        ori_1 = ORI(rd=1, rs1=1, imm=bn1)
        state = ori_1.behavior(state)
        ori_1 = ORI(rd=2, rs1=2, imm=bminimm)
        state = ori_1.behavior(state)
        ori_1 = ORI(rd=3, rs1=3, imm=b5)
        state = ori_1.behavior(state)
        self.assertEqual(state.register_file.registers, [bn1, bn1, bminimm, brandom])

    def test_xori(self):
        b0 = fixedint.MutableUInt32(0)
        b1 = fixedint.MutableUInt32(1)
        bmaxint = fixedint.MutableUInt32(pow(2, 31) - 1)
        bminint = fixedint.MutableUInt32(-pow(2, 31))
        bn1 = fixedint.MutableUInt32(-1)
        brandom = fixedint.MutableUInt32(3320171255)
        brandomx = fixedint.MutableUInt32(974796040)

        # 0 ^ 0  == 0
        # 0 ^ 1  == 1
        # 1 ^ 0  == 1
        # 1 ^ 1  == 0
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b1, b1])
        )
        xori_1 = XORI(rd=0, rs1=0, imm=b0)
        state = xori_1.behavior(state)
        xori_1 = XORI(rd=1, rs1=1, imm=b1)
        state = xori_1.behavior(state)
        xori_1 = XORI(rd=2, rs1=2, imm=b0)
        state = xori_1.behavior(state)
        xori_1 = XORI(rd=3, rs1=3, imm=b1)
        state = xori_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b1, b1, b0])

        # -1 ^ 0        == -1
        # -1 ^ -1       == 0
        # bmaxint ^ -1  == bminint
        # brandom ^ -1  == brandomx
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[bn1, bn1, bmaxint, brandom])
        )
        xori_1 = XORI(rd=0, rs1=0, imm=b0)
        state = xori_1.behavior(state)
        xori_1 = XORI(rd=1, rs1=1, imm=bn1)
        state = xori_1.behavior(state)
        xori_1 = XORI(rd=2, rs1=2, imm=bn1)
        state = xori_1.behavior(state)
        xori_1 = XORI(rd=3, rs1=3, imm=bn1)
        state = xori_1.behavior(state)
        self.assertEqual(state.register_file.registers, [bn1, b0, bminint, brandomx])

    def test_slli(self):
        b0 = fixedint.MutableUInt32(0)
        b1 = fixedint.MutableUInt32(1)
        b2 = fixedint.MutableUInt32(2)
        b20 = fixedint.MutableUInt32(20)
        b31 = fixedint.MutableUInt32(31)
        b127 = fixedint.MutableUInt32(127)
        b2_20 = fixedint.MutableUInt32(pow(2, 20))
        b111 = fixedint.MutableUInt32(pow(2, 32) - 1)  # 11111....
        b110 = fixedint.MutableUInt32(pow(2, 32) - 2)  # 111...110
        b100 = fixedint.MutableUInt32(pow(2, 31))  # 10000....
        brandom = fixedint.MutableUInt32(3320171255)
        brandomx = fixedint.MutableUInt32(395783132)

        # 0 << 0   == 0
        # 0 << 20  == 0
        # 1 << 0   == 1
        # 1 << 1   == 2
        # 1 << 20  == 2^20
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b1, b1, b1])
        )
        slli_1 = SLLI(rd=0, rs1=0, imm=b0)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=1, rs1=1, imm=b20)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=2, rs1=2, imm=b0)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=3, rs1=3, imm=b1)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=4, rs1=4, imm=b20)
        state = slli_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b0, b1, b2, b2_20])

        # 111...1 << 1     == 111...10
        # 111...1 << 31    == 1000....
        # 111...1 << 127    == 0
        # 1000... << 1     == 0
        # 3320171255 << 2  == 395783132
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[b111, b111, b111, b100, brandom])
        )
        slli_1 = SLLI(rd=0, rs1=0, imm=b1)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=1, rs1=1, imm=b31)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=2, rs1=2, imm=b127)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=3, rs1=3, imm=b1)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=4, rs1=4, imm=b2)
        state = slli_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b110, b100, b0, b0, brandomx])

    def test_srli(self):
        b0 = fixedint.MutableUInt32(0)
        b1 = fixedint.MutableUInt32(1)
        b2 = fixedint.MutableUInt32(2)
        b20 = fixedint.MutableUInt32(20)
        b31 = fixedint.MutableUInt32(31)
        b127 = fixedint.MutableUInt32(127)
        b111 = fixedint.MutableUInt32(pow(2, 32) - 1)  # 11111....
        b011 = fixedint.MutableUInt32(pow(2, 31) - 1)  # 01111....
        brandom = fixedint.MutableUInt32(3320171255)
        brandomx = fixedint.MutableUInt32(830042813)

        # 0 >> 0   == 0
        # 0 >> 20  == 0
        # 1 >> 0   == 1
        # 1 >> 1   == 0
        # 1 >> 20  == 0
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b1, b1, b1])
        )
        srli_1 = SRLI(rd=0, rs1=0, imm=b0)
        state = srli_1.behavior(state)
        srli_1 = SRLI(rd=1, rs1=1, imm=b20)
        state = srli_1.behavior(state)
        srli_1 = SRLI(rd=2, rs1=2, imm=b0)
        state = srli_1.behavior(state)
        srli_1 = SRLI(rd=3, rs1=3, imm=b1)
        state = srli_1.behavior(state)
        srli_1 = SRLI(rd=4, rs1=4, imm=b20)
        state = srli_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b0, b1, b0, b0])

        # 111...1 >> 1     == 0111....
        # 111...1 >> 31    == 1
        # 111...1 >> 127   == 0
        # 3320171255 >> 2  == 395783132
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[b111, b111, b111, brandom])
        )
        srli_1 = SRLI(rd=0, rs1=0, imm=b1)
        state = srli_1.behavior(state)
        srli_1 = SRLI(rd=1, rs1=1, imm=b31)
        state = srli_1.behavior(state)
        srli_1 = SRLI(rd=2, rs1=2, imm=b127)
        state = srli_1.behavior(state)
        srli_1 = SRLI(rd=3, rs1=3, imm=b2)
        state = srli_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b011, b1, b0, brandomx])

    def test_slti(self):
        b0 = fixedint.MutableInt32(0)
        b1 = fixedint.MutableInt32(1)
        bn1 = fixedint.MutableInt32(-1)
        b5 = fixedint.MutableInt32(5)
        bn5 = fixedint.MutableInt32(-5)

        # 0 <s 0   == 0
        # 0 <s 1   == 1
        # 0 <s -1  == 0
        # 1 <s 0   == 0
        # -1 <s 0  == 1
        # 1 <s -1  == 0
        # -1 <s 1  == 1
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b0, b1, bn1, b1, bn1])
        )
        slti_1 = SLTI(rd=0, rs1=0, imm=b0)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=1, rs1=1, imm=b1)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=2, rs1=2, imm=bn1)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=3, rs1=3, imm=b0)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=4, rs1=4, imm=b0)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=5, rs1=5, imm=bn1)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=6, rs1=6, imm=b1)
        state = slti_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b1, b0, b0, b1, b0, b1])

        # -5 <s -1  == 1
        # -1 <s -5  == 0
        # 1 <s 5    == 1
        # 5 <s 1    == 0
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[bn5, bn1, b1, b5])
        )
        slti_1 = SLTI(rd=0, rs1=0, imm=bn1)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=1, rs1=1, imm=bn5)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=2, rs1=2, imm=b5)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=3, rs1=3, imm=b1)
        state = slti_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b1, b0, b1, b0])

    def test_sltiu(self):
        b0 = fixedint.MutableInt32(0)
        b1 = fixedint.MutableInt32(1)
        bn1 = fixedint.MutableInt32(-1)
        b5 = fixedint.MutableInt32(5)
        bn5 = fixedint.MutableInt32(-5)

        # 0 <u 0   == 0
        # 0 <u 1   == 1
        # 0 <u -1  == 1
        # 1 <u 0   == 0
        # -1 <u 0  == 0
        # 1 <u -1  == 1
        # -1 <u 1  == 0
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b0, b1, bn1, b1, bn1])
        )
        slti_1 = SLTIU(rd=0, rs1=0, imm=b0)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=1, rs1=1, imm=b1)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=2, rs1=2, imm=bn1)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=3, rs1=3, imm=b0)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=4, rs1=4, imm=b0)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=5, rs1=5, imm=bn1)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=6, rs1=6, imm=b1)
        state = slti_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b1, b1, b0, b1, b1, b1])

        # -5 <u -1  == 1
        # -1 <u -5  == 0
        # 1 <u 5    == 1
        # 5 <u 1    == 0
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[bn5, bn1, b1, b5])
        )
        slti_1 = SLTIU(rd=0, rs1=0, imm=bn1)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=1, rs1=1, imm=bn5)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=2, rs1=2, imm=b5)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=3, rs1=3, imm=b1)
        state = slti_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b1, b1, b1, b0])


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
