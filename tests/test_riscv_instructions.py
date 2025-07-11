import unittest
import fixedint
from architecture_simulator.isa.riscv.rv32i_instructions import (
    ADD,
    BEQ,
    BLT,
    BNE,
    SUB,
    BGE,
    BLTU,
    BGEU,
    CSRRW,
    CSRRS,
    CSRRC,
    CSRRWI,
    CSRRSI,
    CSRRCI,
    SB,
    SH,
    SW,
    LUI,
    AUIPC,
    JAL,
    SLL,
    SLT,
    SLTU,
    XOR,
    SRL,
    SRA,
    OR,
    AND,
    LB,
    LH,
    LW,
    LBU,
    LHU,
    SRAI,
    JALR,
    ECALL,
    EBREAK,
    ADDI,
    SLTI,
    SLTIU,
    XORI,
    ORI,
    ANDI,
    SLLI,
    SRLI,
    InstructionNotImplemented,
    MUL,
    MULH,
    MULHU,
    MULHSU,
    DIV,
    DIVU,
    REM,
    REMU,
)
from architecture_simulator.uarch.riscv.register_file import RegisterFile
from architecture_simulator.uarch.riscv.riscv_architectural_state import (
    RiscvArchitecturalState,
)
from architecture_simulator.uarch.memory.memory import Memory, AddressingType
from architecture_simulator.uarch.riscv.csr_registers import CSRError
from architecture_simulator.isa.riscv.riscv_parser import RiscvParser
from architecture_simulator.simulation.riscv_simulation import RiscvSimulation


class TestRiscvInstructions(unittest.TestCase):
    def test_add(self):
        # Number definitions
        num_min = fixedint.UInt32(2147483648)
        num_minus_7 = fixedint.UInt32(4294967289)
        num_minus_2 = fixedint.UInt32(4294967294)
        num_minus_1 = fixedint.UInt32(4294967295)
        num_0 = fixedint.UInt32(0)
        num_1 = fixedint.UInt32(1)
        num_9 = fixedint.UInt32(9)
        num_16 = fixedint.UInt32(16)
        num_max = fixedint.UInt32(2147483647)

        # smallest number + biggest number = -1
        add = ADD(rs1=1, rs2=0, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_min, num_max])
        )
        state = add.behavior(state)
        self.assertEqual(state.register_file.registers, [num_max, num_min, num_minus_1])

        # smallest number + smallest number = 0
        add = ADD(rs1=0, rs2=1, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_min, num_min, num_minus_1])
        )
        state = add.behavior(state)
        self.assertEqual(state.register_file.registers, [num_min, num_min, num_0])

        # biggest number + biggest number = -2
        add = ADD(rs1=0, rs2=1, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_max, num_0])
        )
        state = add.behavior(state)
        self.assertEqual(state.register_file.registers, [num_max, num_max, num_minus_2])

        # 16 + (-7) = 9 (non edge case addition)
        add = ADD(rs1=3, rs2=4, rd=1)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(
                registers=[num_max, num_max, num_0, num_16, num_minus_7]
            )
        )
        state = add.behavior(state)
        self.assertEqual(
            state.register_file.registers, [num_max, num_9, num_0, num_16, num_minus_7]
        )

        # 0 + 0 = 0
        add = ADD(rs1=2, rs2=2, rd=1)
        state = RiscvArchitecturalState(
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
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_1, num_16])
        )
        state = add.behavior(state)
        self.assertEqual(state.register_file.registers, [num_max, num_1, num_min])

    def test_sub(self):
        # Number definitions
        num_min = fixedint.UInt32(2147483648)
        num_minus_1 = fixedint.UInt32(4294967295)
        num_0 = fixedint.UInt32(0)
        num_1 = fixedint.UInt32(1)
        num_8 = fixedint.UInt32(8)
        num_15 = fixedint.UInt32(15)
        num_23 = fixedint.UInt32(23)
        num_max = fixedint.UInt32(2147483647)

        # smallest number - smallest number = 0
        sub = SUB(rs1=0, rs2=0, rd=1)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_min, num_15])
        )
        state = sub.behavior(state)
        self.assertEqual(state.register_file.registers, [num_min, num_0])

        # biggest number - biggest number = 0
        sub = SUB(rs1=0, rs2=0, rd=1)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_15])
        )
        state = sub.behavior(state)
        self.assertEqual(state.register_file.registers, [num_max, num_0])

        # smallest number - biggest number = 1
        sub = SUB(rs1=0, rs2=1, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_min, num_max, num_0])
        )
        state = sub.behavior(state)
        self.assertEqual(state.register_file.registers, [num_min, num_max, num_1])

        # biggest number - smallest number = -1
        sub = SUB(rs1=0, rs2=1, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_min, num_0])
        )
        state = sub.behavior(state)
        self.assertEqual(state.register_file.registers, [num_max, num_min, num_minus_1])

        # smallest number - 1 = biggest number
        sub = SUB(rs1=0, rs2=1, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_min, num_1, num_0])
        )
        state = sub.behavior(state)
        self.assertEqual(state.register_file.registers, [num_min, num_1, num_max])

        # biggest number - (-1) = smallest number
        sub = SUB(rs1=0, rs2=1, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_minus_1, num_0])
        )
        state = sub.behavior(state)
        self.assertEqual(state.register_file.registers, [num_max, num_minus_1, num_min])

        # 23 - 8 = 15
        sub = SUB(rs1=1, rs2=0, rd=0)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_8, num_23])
        )
        state = sub.behavior(state)
        self.assertEqual(state.register_file.registers, [num_15, num_23])

    def test_sll(self):
        # Number definitions
        num_max = fixedint.UInt32(4294967295)
        num_msb = fixedint.UInt32(2147483648)
        num_0 = fixedint.UInt32(0)
        num_1 = fixedint.UInt32(1)
        num_16 = fixedint.UInt32(16)
        num_31 = fixedint.UInt32(31)
        num_612 = fixedint.UInt32(612)

        # only most significant bit set shifted by one = zero
        sll = SLL(rs1=1, rs2=2, rd=0)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_msb, num_1])
        )
        state = sll.behavior(state)
        self.assertEqual(state.register_file.registers, [num_0, num_msb, num_1])

        # FFFFFFFF shifted by 31 = only most significant bit set
        sll = SLL(rs1=1, rs2=2, rd=0)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_0, num_max, num_31])
        )
        state = sll.behavior(state)
        self.assertEqual(state.register_file.registers, [num_msb, num_max, num_31])

        # shif by zero only writes state
        sll = SLL(rs1=1, rs2=0, rd=4)
        state = RiscvArchitecturalState(
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
        state = RiscvArchitecturalState(
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
        num_min = fixedint.UInt32(2147483648)
        num_max = fixedint.UInt32(2147483647)
        num_0 = fixedint.UInt32(0)
        num_1 = fixedint.UInt32(1)
        num_77 = fixedint.UInt32(77)

        # equivalenz leads to 0
        slt = SLT(rs1=1, rs2=0, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_77, num_77, num_77])
        )
        state = slt.behavior(state)
        self.assertEqual(state.register_file.registers, [num_77, num_77, num_0])

        # numbers are treated as signed
        slt = SLT(rs1=0, rs2=1, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_min, num_max, num_77])
        )
        state = slt.behavior(state)
        self.assertEqual(state.register_file.registers, [num_min, num_max, num_1])

        # rs1 beeing smaller by one leads to 1
        slt = SLT(rs1=1, rs2=2, rd=0)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_min, num_0, num_1])
        )
        state = slt.behavior(state)
        self.assertEqual(state.register_file.registers, [num_1, num_0, num_1])

        # rs1 beeing greater by one leads to 0
        slt = SLT(rs1=1, rs2=2, rd=0)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_min, num_1, num_0])
        )
        state = slt.behavior(state)
        self.assertEqual(state.register_file.registers, [num_0, num_1, num_0])

    def test_sltu(self):
        # Number definitions
        num_0 = fixedint.UInt32(0)
        num_max = fixedint.UInt32(4294967295)
        num_1 = fixedint.UInt32(1)
        num_77 = fixedint.UInt32(77)

        # equivalenz leads to 0
        sltu = SLTU(rs1=1, rs2=0, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_77, num_77, num_77])
        )
        state = sltu.behavior(state)
        self.assertEqual(state.register_file.registers, [num_77, num_77, num_0])

        # numbers are treated as unsigned
        sltu = SLTU(rs1=0, rs2=1, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_0, num_77])
        )
        state = sltu.behavior(state)
        self.assertEqual(state.register_file.registers, [num_max, num_0, num_0])

        # rs1 beeing smaller by one leads to 1
        sltu = SLTU(rs1=1, rs2=2, rd=0)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_0, num_1])
        )
        state = sltu.behavior(state)
        self.assertEqual(state.register_file.registers, [num_1, num_0, num_1])

        # rs1 beeing greater by one leads to 0
        sltu = SLTU(rs1=1, rs2=2, rd=0)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_1, num_0])
        )
        state = sltu.behavior(state)
        self.assertEqual(state.register_file.registers, [num_0, num_1, num_0])

    def test_xor(self):
        # Number defintions
        num_all_but_msb = fixedint.UInt32(2147483647)
        num_msb = fixedint.UInt32(2147483648)
        num_all_bits = fixedint.UInt32(4294967295)
        num_0 = fixedint.UInt32(0)

        num_a = fixedint.UInt32(0x_FF_FF_00_FF)
        num_b = fixedint.UInt32(0x_FF_FF_0F_0F)
        num_c = fixedint.UInt32(0x_00_00_0F_F0)

        # general test case
        xor = XOR(rs1=0, rs2=1, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_all_but_msb, num_all_bits, num_0])
        )
        state = xor.behavior(state)
        self.assertEqual(
            state.register_file.registers, [num_all_but_msb, num_all_bits, num_msb]
        )

        # test all combinations of bit pairs
        xor = XOR(rs1=3, rs2=4, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(
                registers=[num_all_but_msb, num_all_bits, num_0, num_a, num_b]
            )
        )
        state = xor.behavior(state)
        self.assertEqual(
            state.register_file.registers,
            [num_all_but_msb, num_all_bits, num_c, num_a, num_b],
        )

        # zero xor zero = zero
        xor = XOR(rs1=0, rs2=0, rd=1)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_0, num_b])
        )
        state = xor.behavior(state)
        self.assertEqual(state.register_file.registers, [num_0, num_0])

    def test_srl(self):
        # Number definitions
        num_max = fixedint.UInt32(4294967295)
        num_0 = fixedint.UInt32(0)
        num_1 = fixedint.UInt32(1)
        num_31 = fixedint.UInt32(31)
        num_612 = fixedint.UInt32(612)

        # one shifted by one = zero
        srl = SRL(rs1=1, rs2=2, rd=0)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_1, num_1])
        )
        state = srl.behavior(state)
        self.assertEqual(state.register_file.registers, [num_0, num_1, num_1])

        # FFFFFFFF shifted by 31 = one
        srl = SRL(rs1=0, rs2=1, rd=0)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_31, num_612])
        )
        state = srl.behavior(state)
        self.assertEqual(state.register_file.registers, [num_1, num_31, num_612])

        # shif by zero only writes state
        srl = SRL(rs1=0, rs2=1, rd=0)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_max, num_0, num_612])
        )
        state = srl.behavior(state)
        self.assertEqual(state.register_file.registers, [num_max, num_0, num_612])

        # higher bits do not affect shift amount
        srl = SRL(rs1=0, rs2=1, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_31, num_612, num_612])
        )
        state = srl.behavior(state)
        self.assertEqual(state.register_file.registers, [num_31, num_612, num_1])

    def test_sra(self):
        # Number definitions
        num_all_set = fixedint.UInt32(4294967295)
        num_msb_set = fixedint.UInt32(2147483648)
        num_second_set = fixedint.UInt32(1073741824)
        num_0 = fixedint.UInt32(0)
        num_1 = fixedint.UInt32(1)
        num_30 = fixedint.UInt32(30)
        num_31 = fixedint.UInt32(31)
        num_38 = fixedint.UInt32(38)
        num_612 = fixedint.UInt32(612)
        num_2pow26 = fixedint.UInt32(67108864)

        # negative numbers get extended with one´s
        sra = SRA(rs1=0, rs2=1, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_msb_set, num_31, num_0])
        )
        state = sra.behavior(state)
        self.assertEqual(
            state.register_file.registers, [num_msb_set, num_31, num_all_set]
        )
        # positive numbers get extended with zero´s
        sra = SRA(rs1=0, rs2=1, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_second_set, num_30, num_all_set])
        )
        state = sra.behavior(state)
        self.assertEqual(state.register_file.registers, [num_second_set, num_30, num_1])

        # shift amount only affected by 5 lower bits
        sra = SRA(rs1=0, rs2=1, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_second_set, num_612, num_all_set])
        )
        state = sra.behavior(state)
        self.assertEqual(
            state.register_file.registers, [num_second_set, num_612, num_2pow26]
        )
        # percision test
        sra = SRA(rs1=0, rs2=1, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_612, num_612, num_all_set])
        )
        state = sra.behavior(state)
        self.assertEqual(state.register_file.registers, [num_612, num_612, num_38])

    def test_or(self):
        # Number definitions
        num_a = fixedint.UInt32(0x00_FF_00_12)
        num_b = fixedint.UInt32(0x0F_0F_00_00)
        num_c = fixedint.UInt32(0x0F_FF_00_12)

        # Test bit wise behavior
        or_inst = OR(rs1=0, rs2=1, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_a, num_b, num_a])
        )
        state = or_inst.behavior(state)
        self.assertEqual(state.register_file.registers, [num_a, num_b, num_c])

        # Test kommutativity
        or_inst = OR(rs1=1, rs2=0, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_a, num_b, num_a])
        )
        state = or_inst.behavior(state)
        self.assertEqual(state.register_file.registers, [num_a, num_b, num_c])

    def test_and(self):
        # Number defintions
        num_a = fixedint.UInt32(0x00_FF_00_12)
        num_b = fixedint.UInt32(0x0F_0F_00_00)
        num_c = fixedint.UInt32(0x00_0F_00_00)

        # Test bit wise behavior
        and_inst = AND(rs1=0, rs2=1, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_a, num_b, num_a])
        )
        state = and_inst.behavior(state)
        self.assertEqual(state.register_file.registers, [num_a, num_b, num_c])

        # Test kommutativity
        and_inst = AND(rs1=1, rs2=0, rd=2)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[num_a, num_b, num_a])
        )
        state = and_inst.behavior(state)
        self.assertEqual(state.register_file.registers, [num_a, num_b, num_c])

    def test_itype(self):
        itype = LB(rs1=0, rd=0, imm=0)
        self.assertEqual(itype.imm, 0)
        itype = LH(rs1=0, rd=0, imm=1)
        self.assertEqual(itype.imm, 1)
        itype = LW(rs1=0, rd=0, imm=-1)
        self.assertEqual(itype.imm, -1)
        itype = LB(rs1=0, rd=0, imm=2047)
        self.assertEqual(itype.imm, 2047)
        itype = LH(rs1=0, rd=0, imm=-2048)
        self.assertEqual(itype.imm, -2048)
        itype = LW(rs1=0, rd=0, imm=2048)
        self.assertEqual(itype.imm, -2048)
        itype = LW(rs1=0, rd=0, imm=-2049)
        self.assertEqual(itype.imm, 2047)

    def test_shiftitype(self):
        shiftitype = SLLI(rd=0, rs1=0, imm=0)
        self.assertEqual(shiftitype.imm, 0)
        shiftitype = SLLI(rd=0, rs1=0, imm=1)
        self.assertEqual(shiftitype.imm, 1)
        shiftitype = SLLI(rd=0, rs1=0, imm=31)
        self.assertEqual(shiftitype.imm, 31)
        shiftitype = SLLI(rd=0, rs1=0, imm=32)
        self.assertEqual(shiftitype.imm, 0)
        shiftitype = SLLI(rd=0, rs1=0, imm=-1)
        self.assertEqual(shiftitype.imm, 31)
        shiftitype = SLLI(rd=0, rs1=0, imm=-2)
        self.assertEqual(shiftitype.imm, 30)

    def test_addi(self):
        b0 = fixedint.UInt32(0)
        b1 = fixedint.UInt32(1)
        bmaxint = fixedint.UInt32(pow(2, 31) - 1)
        bminint = fixedint.UInt32(-pow(2, 31))
        bmaximm = fixedint.UInt32(2047)
        bminimm = fixedint.UInt32(-2048)
        bn1 = fixedint.UInt32(-1)
        brandom = fixedint.UInt32(3320171255)
        brandomx = fixedint.UInt32(3320171260)

        # 0 + 0    == 0
        # 0 + 1    == 1
        # 1 + 0    == 1
        # 0 + -1   == -1
        # 1 + -1   == 0
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[0, 0, 1, 0, 1])
        )
        addi_1 = ADDI(rd=0, rs1=0, imm=0)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=1, rs1=1, imm=1)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=2, rs1=2, imm=0)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=3, rs1=3, imm=-1)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=4, rs1=4, imm=-1)
        state = addi_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b1, b1, bn1, b0])

        # bmaxint + 1    == bminint
        # bminint + -1   == bmaxint
        # 0 + bmaximm    == 2047
        # 0 + bminimm    == -2048
        # brandom + 5
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[bmaxint, bminint, b0, b0, brandom])
        )
        addi_1 = ADDI(rd=0, rs1=0, imm=1)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=1, rs1=1, imm=-1)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=2, rs1=2, imm=2047)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=3, rs1=3, imm=-2048)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=4, rs1=4, imm=5)
        state = addi_1.behavior(state)
        self.assertEqual(
            state.register_file.registers,
            [bminint, bmaxint, bmaximm, bminimm, brandomx],
        )

        # overflow
        # 0 +  2048 == -2048
        # 0 + -2049 == 2047
        # 0 +  4095 == -1
        # 0 + -4096 == 0
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[0, 0, 0, 0])
        )
        addi_1 = ADDI(rd=0, rs1=0, imm=2048)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=1, rs1=1, imm=-2049)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=2, rs1=2, imm=4095)
        state = addi_1.behavior(state)
        addi_1 = ADDI(rd=3, rs1=3, imm=-4096)
        state = addi_1.behavior(state)
        self.assertEqual(
            state.register_file.registers,
            [bminimm, bmaximm, bn1, b0],
        )

    def test_slti(self):
        b0 = fixedint.UInt32(0)
        b1 = fixedint.UInt32(1)
        bn1 = fixedint.UInt32(-1)
        b5 = fixedint.UInt32(5)
        bn5 = fixedint.UInt32(-5)

        # 0 <s 0   == 0
        # 0 <s 1   == 1
        # 0 <s -1  == 0
        # 1 <s 0   == 0
        # -1 <s 0  == 1
        # 1 <s -1  == 0
        # -1 <s 1  == 1
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b0, b1, bn1, b1, bn1])
        )
        slti_1 = SLTI(rd=0, rs1=0, imm=0)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=1, rs1=1, imm=1)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=2, rs1=2, imm=-1)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=3, rs1=3, imm=0)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=4, rs1=4, imm=0)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=5, rs1=5, imm=-1)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=6, rs1=6, imm=1)
        state = slti_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b1, b0, b0, b1, b0, b1])

        # -5 <s -1  == 1
        # -1 <s -5  == 0
        # 1 <s 5    == 1
        # 5 <s 1    == 0
        # -1 <s -1  == 0
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[bn5, bn1, b1, b5, bn1])
        )
        slti_1 = SLTI(rd=0, rs1=0, imm=-1)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=1, rs1=1, imm=-5)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=2, rs1=2, imm=5)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=3, rs1=3, imm=1)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=4, rs1=4, imm=-1)
        state = slti_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b1, b0, b1, b0, b0])

        # overflow
        # 0 <s 2047  == 1
        # 0 <s 2048  == 0
        # 0 <s -2048 == 0
        # 0 <s -2049 == 1
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b0, b0])
        )
        slti_1 = SLTI(rd=0, rs1=0, imm=2047)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=1, rs1=1, imm=2048)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=2, rs1=2, imm=-2048)
        state = slti_1.behavior(state)
        slti_1 = SLTI(rd=3, rs1=3, imm=-2049)
        state = slti_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b1, b0, b0, b1])

    def test_sltiu(self):
        b0 = fixedint.UInt32(0)
        b1 = fixedint.UInt32(1)
        bn1 = fixedint.UInt32(-1)
        b5 = fixedint.UInt32(5)
        bn5 = fixedint.UInt32(-5)

        # 0 <u 0   == 0
        # 0 <u 1   == 1
        # 0 <u -1  == 1
        # 1 <u 0   == 0
        # -1 <u 0  == 0
        # 1 <u -1  == 1
        # -1 <u 1  == 0
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b0, b1, bn1, b1, bn1])
        )
        slti_1 = SLTIU(rd=0, rs1=0, imm=0)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=1, rs1=1, imm=1)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=2, rs1=2, imm=-1)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=3, rs1=3, imm=0)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=4, rs1=4, imm=0)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=5, rs1=5, imm=-1)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=6, rs1=6, imm=1)
        state = slti_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b1, b1, b0, b0, b1, b0])

        # -5 <u -1  == 1
        # -1 <u -5  == 0
        # 1 <u 5    == 1
        # 5 <u 1    == 0
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[bn5, bn1, b1, b5])
        )
        slti_1 = SLTIU(rd=0, rs1=0, imm=-1)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=1, rs1=1, imm=-5)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=2, rs1=2, imm=5)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=3, rs1=3, imm=1)
        state = slti_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b1, b0, b1, b0])

        # overflow
        # 0 <u 2048  == 1
        # 0 <u 4095  == 1
        # 0 <u 4096  == 0
        # 0 <u 4097  == 1
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b0, b0])
        )
        slti_1 = SLTIU(rd=0, rs1=0, imm=2048)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=1, rs1=1, imm=4095)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=2, rs1=2, imm=4096)
        state = slti_1.behavior(state)
        slti_1 = SLTIU(rd=3, rs1=3, imm=4097)
        state = slti_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b1, b1, b0, b1])

    def test_xori(self):
        b0 = fixedint.UInt32(0)
        b1 = fixedint.UInt32(1)
        bmaxint = fixedint.UInt32(pow(2, 31) - 1)
        bminint = fixedint.UInt32(-pow(2, 31))
        bmaximm = fixedint.UInt32(2047)
        bminimm = fixedint.UInt32(-2048)
        bn1 = fixedint.UInt32(-1)
        brandom = fixedint.UInt32(3320171255)
        brandomx = fixedint.UInt32(974796040)

        # 0 ^ 0  == 0
        # 0 ^ 1  == 1
        # 1 ^ 0  == 1
        # 1 ^ 1  == 0
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b1, b1])
        )
        xori_1 = XORI(rd=0, rs1=0, imm=0)
        state = xori_1.behavior(state)
        xori_1 = XORI(rd=1, rs1=1, imm=1)
        state = xori_1.behavior(state)
        xori_1 = XORI(rd=2, rs1=2, imm=0)
        state = xori_1.behavior(state)
        xori_1 = XORI(rd=3, rs1=3, imm=1)
        state = xori_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b1, b1, b0])

        # -1 ^ 0        == -1
        # -1 ^ -1       == 0
        # bmaxint ^ -1  == bminint
        # brandom ^ -1  == brandomx
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[bn1, bn1, bmaxint, brandom])
        )
        xori_1 = XORI(rd=0, rs1=0, imm=0)
        state = xori_1.behavior(state)
        xori_1 = XORI(rd=1, rs1=1, imm=-1)
        state = xori_1.behavior(state)
        xori_1 = XORI(rd=2, rs1=2, imm=-1)
        state = xori_1.behavior(state)
        xori_1 = XORI(rd=3, rs1=3, imm=-1)
        state = xori_1.behavior(state)
        self.assertEqual(state.register_file.registers, [bn1, b0, bminint, brandomx])

        # overflow
        # 0 ^  2048 == -2048
        # 0 ^ -2049 == 2047
        # 0 ^  4095 == -1
        # 0 ^ -4096 == 0
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b0, b0])
        )
        xori_1 = XORI(rd=0, rs1=0, imm=2048)
        state = xori_1.behavior(state)
        xori_1 = XORI(rd=1, rs1=1, imm=-2049)
        state = xori_1.behavior(state)
        xori_1 = XORI(rd=2, rs1=2, imm=4095)
        state = xori_1.behavior(state)
        xori_1 = XORI(rd=3, rs1=3, imm=-4096)
        state = xori_1.behavior(state)
        self.assertEqual(state.register_file.registers, [bminimm, bmaximm, bn1, b0])

    def test_ori(self):
        b0 = fixedint.UInt32(0)
        b1 = fixedint.UInt32(1)
        bmaximm = fixedint.UInt32(2047)
        bminimm = fixedint.UInt32(-2048)
        bn1 = fixedint.UInt32(-1)
        brandom = fixedint.UInt32(3320171255)

        # 0 | 0  == 0
        # 0 | 1  == 1
        # 1 | 0  == 1
        # 1 | 1  == 1
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b1, b1])
        )
        ori_1 = ORI(rd=0, rs1=0, imm=0)
        state = ori_1.behavior(state)
        ori_1 = ORI(rd=1, rs1=1, imm=1)
        state = ori_1.behavior(state)
        ori_1 = ORI(rd=2, rs1=2, imm=0)
        state = ori_1.behavior(state)
        ori_1 = ORI(rd=3, rs1=3, imm=1)
        state = ori_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b1, b1, b1])

        # -1 | 0       == -1
        # -1 | -1      == -1
        # 0 | bminimm  == bminimm
        # brandom | 5  == brandom
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[bn1, bn1, b0, brandom])
        )
        ori_1 = ORI(rd=0, rs1=0, imm=0)
        state = ori_1.behavior(state)
        ori_1 = ORI(rd=1, rs1=1, imm=-1)
        state = ori_1.behavior(state)
        ori_1 = ORI(rd=2, rs1=2, imm=-2048)
        state = ori_1.behavior(state)
        ori_1 = ORI(rd=3, rs1=3, imm=5)
        state = ori_1.behavior(state)
        self.assertEqual(state.register_file.registers, [bn1, bn1, bminimm, brandom])

        # overflow
        # 0 |  2048 == -2048
        # 0 | -2049 == 2047
        # 0 |  4095 == -1
        # 0 | -4096 == 0
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b0, b0])
        )
        ori_1 = ORI(rd=0, rs1=0, imm=2048)
        state = ori_1.behavior(state)
        ori_1 = ORI(rd=1, rs1=1, imm=-2049)
        state = ori_1.behavior(state)
        ori_1 = ORI(rd=2, rs1=2, imm=4095)
        state = ori_1.behavior(state)
        ori_1 = ORI(rd=3, rs1=3, imm=-4096)
        state = ori_1.behavior(state)
        self.assertEqual(state.register_file.registers, [bminimm, bmaximm, bn1, b0])

    def test_andi(self):
        b0 = fixedint.UInt32(0)
        b1 = fixedint.UInt32(1)
        b5 = fixedint.UInt32(5)
        bmaxint = fixedint.UInt32(pow(2, 31) - 1)
        bmaximm = fixedint.UInt32(2047)
        bminimm = fixedint.UInt32(-2048)
        bn1 = fixedint.UInt32(-1)
        brandom = fixedint.UInt32(3320171255)

        # 0 & 0    == 0
        # 0 & 1    == 0
        # 1 & 0    == 0
        # 1 & 1    == 1
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b1, b1])
        )
        andi_1 = ANDI(rd=0, rs1=0, imm=0)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=1, rs1=1, imm=1)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=2, rs1=2, imm=0)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=3, rs1=3, imm=1)
        state = andi_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b0, b0, b1])

        # -1 & 0             == 0
        # -1 & 1             == 1
        # bmaxint & bmaximm  == bmaximm
        # bmaxint & -1       == bmaxint
        # brandom & 5        == 5
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[bn1, bn1, bmaxint, bmaxint, brandom])
        )
        andi_1 = ANDI(rd=0, rs1=0, imm=0)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=1, rs1=1, imm=1)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=2, rs1=2, imm=2047)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=3, rs1=3, imm=-1)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=4, rs1=4, imm=5)
        state = andi_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b1, bmaximm, bmaxint, b5])

        # overflow
        # -1 &  2048 == -2048
        # -1 & -2049 == 2047
        # -1 &  4095 == -1
        # -1 & -4096 == 0
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[bn1, bn1, bn1, bn1])
        )
        andi_1 = ANDI(rd=0, rs1=0, imm=2048)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=1, rs1=1, imm=-2049)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=2, rs1=2, imm=4095)
        state = andi_1.behavior(state)
        andi_1 = ANDI(rd=3, rs1=3, imm=-4096)
        state = andi_1.behavior(state)
        self.assertEqual(state.register_file.registers, [bminimm, bmaximm, bn1, b0])

    def test_slli(self):
        b0 = fixedint.UInt32(0)
        b1 = fixedint.UInt32(1)
        b2 = fixedint.UInt32(2)
        b2_20 = fixedint.UInt32(pow(2, 20))
        b111 = fixedint.UInt32(-1)  # 11111....
        b110 = fixedint.UInt32(pow(2, 32) - 2)  # 111...110
        b100 = fixedint.UInt32(pow(2, 31))  # 10000....
        brandom = fixedint.UInt32(3320171255)
        brandomx = fixedint.UInt32(395783132)

        # 0 << 0   == 0
        # 0 << 20  == 0
        # 1 << 0   == 1
        # 1 << 1   == 2
        # 1 << 20  == 2^20
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b1, b1, b1])
        )
        slli_1 = SLLI(rd=0, rs1=0, imm=0)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=1, rs1=1, imm=20)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=2, rs1=2, imm=0)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=3, rs1=3, imm=1)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=4, rs1=4, imm=20)
        state = slli_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b0, b1, b2, b2_20])

        # 111...1 << 1     == 111...10
        # 111...1 << 31    == 1000....
        # 111...1 << 127    == 1000....
        # 1000... << 1     == 0
        # 3320171255 << 2  == 395783132
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[b111, b111, b111, b100, brandom])
        )
        slli_1 = SLLI(rd=0, rs1=0, imm=1)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=1, rs1=1, imm=31)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=2, rs1=2, imm=127)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=3, rs1=3, imm=1)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=4, rs1=4, imm=2)
        state = slli_1.behavior(state)
        self.assertEqual(
            state.register_file.registers, [b110, b100, b100, b0, brandomx]
        )

        # -1 << -1  == b100
        # -1 << 32  == -1
        # -1 << 33  == 111...10
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[b111, b111, b111, b111])
        )
        slli_1 = SLLI(rd=0, rs1=0, imm=-1)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=1, rs1=1, imm=32)
        state = slli_1.behavior(state)
        slli_1 = SLLI(rd=2, rs1=2, imm=33)
        state = slli_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b100, b111, b110, b111])

    def test_srli(self):
        b0 = fixedint.UInt32(0)
        b1 = fixedint.UInt32(1)
        b111 = fixedint.UInt32(pow(2, 32) - 1)  # 11111....
        b011 = fixedint.UInt32(pow(2, 31) - 1)  # 01111....
        brandom = fixedint.UInt32(3320171255)
        brandomx = fixedint.UInt32(830042813)

        # 0 >> 0   == 0
        # 0 >> 20  == 0
        # 1 >> 0   == 1
        # 1 >> 1   == 0
        # 1 >> 20  == 0
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[b0, b0, b1, b1, b1])
        )
        srli_1 = SRLI(rd=0, rs1=0, imm=0)
        state = srli_1.behavior(state)
        srli_1 = SRLI(rd=1, rs1=1, imm=20)
        state = srli_1.behavior(state)
        srli_1 = SRLI(rd=2, rs1=2, imm=0)
        state = srli_1.behavior(state)
        srli_1 = SRLI(rd=3, rs1=3, imm=1)
        state = srli_1.behavior(state)
        srli_1 = SRLI(rd=4, rs1=4, imm=20)
        state = srli_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b0, b0, b1, b0, b0])

        # 111...1 >> 1     == 0111....
        # 111...1 >> 31    == 1
        # 111...1 >> 127   == 1
        # 3320171255 >> 2  == 395783132
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[b111, b111, b111, brandom])
        )
        srli_1 = SRLI(rd=0, rs1=0, imm=1)
        state = srli_1.behavior(state)
        srli_1 = SRLI(rd=1, rs1=1, imm=31)
        state = srli_1.behavior(state)
        srli_1 = SRLI(rd=2, rs1=2, imm=127)
        state = srli_1.behavior(state)
        srli_1 = SRLI(rd=3, rs1=3, imm=2)
        state = srli_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b011, b1, b1, brandomx])

        # -1 >> -1  == 1
        # -1 >> 32  == -1
        # -1 >> 33  == 01111
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[b111, b111, b111])
        )
        srli_1 = SRLI(rd=0, rs1=0, imm=-1)
        state = srli_1.behavior(state)
        srli_1 = SRLI(rd=1, rs1=1, imm=32)
        state = srli_1.behavior(state)
        srli_1 = SRLI(rd=2, rs1=2, imm=33)
        state = srli_1.behavior(state)
        self.assertEqual(state.register_file.registers, [b1, b111, b011])

    def test_srai(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[0, 1, -128])
        )
        # imm=0, rs1=0
        state.register_file.registers = [0, 1, -128]
        instr = SRAI(imm=0, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [0, 1, -128])

        # imm=1, rs1=0
        state.register_file.registers = [0, 1, -128]
        instr = SRAI(imm=1, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [0, 1, -128])

        # imm=0, rs1=1
        state.register_file.registers = [0, 1, -128]
        instr = SRAI(imm=0, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1, 1, -128])

        # imm=1, rs1=1
        state.register_file.registers = [0, 1, -128]
        instr = SRAI(imm=1, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [0, 1, -128])

        # imm=1, rs1=-128
        state.register_file.registers = [0, 1, -128]
        instr = SRAI(imm=1, rs1=2, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [fixedint.UInt32(-64), 1, -128])

        # imm=95, rs1= 2^30 immediate is max 32
        state.register_file.registers = [0, 1, -128, pow(2, 30)]
        instr = SRAI(imm=95, rs1=3, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [0, 1, -128, pow(2, 30)])

    def test_lb(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[0, 1, -1, pow(2, 32) - 1]),
            memory=Memory(AddressingType.BYTE, 32, True),
        )
        state.memory.memory_file = dict(
            [
                (0, fixedint.UInt8(1)),
                (1, fixedint.UInt8(2)),
                (2, fixedint.UInt8(3)),
                (3, fixedint.UInt8(-1)),
                (pow(2, 32) - 1, fixedint.UInt8(4)),
                (2047, fixedint.UInt8(5)),
            ]
        )
        # imm=0, rs1=0 try with both values at 0
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=0, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1, 1, -1, pow(2, 32) - 1])

        # imm=1, rs1=0 try with imm = 1
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=1, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [2, 1, -1, pow(2, 32) - 1])

        # imm=0, rs1=1 try with rs1 value = 1
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=0, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [2, 1, -1, pow(2, 32) - 1])

        # imm=1, rs1=1 try with both values = 1
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=1, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [3, 1, -1, pow(2, 32) - 1])

        # imm=1, rs1=-1 try with negative value in rs1, equates to acces to memory 0
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=1, rs1=2, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1, 1, -1, pow(2, 32) - 1])

        # imm=1, rs1=2^32-1 try with really high value in rs1, equates to 0 because memory is circular
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=1, rs1=3, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1, 1, -1, pow(2, 32) - 1])

        # imm=0, rs1=-1 negative value of -1 gets converted to 2^32-1
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=0, rs1=2, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [4, 1, -1, pow(2, 32) - 1])

        # imm=10239, rs1=0 too high value in imm gets convertet to 12 bit i e 2047
        # FIXME
        # state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        # instr = LB(imm=10239, rs1=0, rd=0)
        # state = instr.behavior(state)
        # self.assertEqual(state.register_file.registers, [5, 1, -1, pow(2, 32) - 1])

        # imm=3, rs1=0 load negative value
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=3, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers,
            [fixedint.UInt32(-1), 1, -1, pow(2, 32) - 1],
        )

        # try memory acces to non existant address
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=4, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [0, 1, -1, pow(2, 32) - 1])

    def test_lh(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[0, 2, -2, pow(2, 32) - 1]),
            memory=Memory(AddressingType.BYTE, 32, True),
        )
        state.memory.memory_file = dict(
            [
                (0, fixedint.UInt8(1)),
                (1, fixedint.UInt8(2)),
                (2, fixedint.UInt8(3)),
                (3, fixedint.UInt8(4)),
                (4, fixedint.UInt8(5)),
                (5, fixedint.UInt8(6)),
                (6, fixedint.UInt8(-1)),
                (7, fixedint.UInt8(-1)),
                (pow(2, 32) - 2, fixedint.UInt8(7)),
                (pow(2, 32) - 1, fixedint.UInt8(8)),
                (2047, fixedint.UInt8(5)),
            ]
        )
        # imm=0, rs1=0 try with both values at 0
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LH(imm=0, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [513, 2, -2, pow(2, 32) - 1])

        # imm=2, rs1=0 try with imm = 2
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LH(imm=2, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1027, 2, -2, pow(2, 32) - 1])

        # imm=0, rs1=2 try with rs1 value = 2
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LH(imm=0, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1027, 2, -2, pow(2, 32) - 1])

        # imm=2, rs1=2 try with both values = 2
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LH(imm=2, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1541, 2, -2, pow(2, 32) - 1])

        # imm=2, rs1=-2 try with negative value in rs1, equates to acces to memory 0
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LH(imm=2, rs1=2, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [513, 2, -2, pow(2, 32) - 1])

        # imm=1, rs1=2^32-1 try with really high value in rs1, equates to 0 because memory is circular
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

        # imm=10239, rs1=0 too high value in imm gets convertet to 12 bit i e 2047
        # FIXME
        # state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        # instr = LH(imm=10239, rs1=0, rd=0)
        # state = instr.behavior(state)
        # self.assertEqual(state.register_file.registers, [5, 1, -1, pow(2, 32) - 1])

        # imm=6, rs1=0 load negative value
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LH(imm=6, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers,
            [fixedint.UInt32(-1), 2, -2, pow(2, 32) - 1],
        )

        # try memory acces to non existant address
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=8, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [0, 1, -1, pow(2, 32) - 1])

    def test_lw(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[0, 4, -4, pow(2, 32) - 1]),
            memory=Memory(AddressingType.BYTE, 32, True),
        )
        state.memory.memory_file = dict(
            [
                (0, fixedint.UInt8(1)),
                (1, fixedint.UInt8(1)),
                (2, fixedint.UInt8(1)),
                (3, fixedint.UInt8(1)),
                (4, fixedint.UInt8(2)),
                (5, fixedint.UInt8(2)),
                (6, fixedint.UInt8(2)),
                (7, fixedint.UInt8(2)),
                (8, fixedint.UInt8(3)),
                (9, fixedint.UInt8(3)),
                (10, fixedint.UInt8(3)),
                (11, fixedint.UInt8(3)),
                (12, fixedint.UInt8(-1)),
                (13, fixedint.UInt8(-1)),
                (14, fixedint.UInt8(-1)),
                (15, fixedint.UInt8(-1)),
                (pow(2, 32) - 4, fixedint.UInt8(4)),
                (pow(2, 32) - 3, fixedint.UInt8(4)),
                (pow(2, 32) - 2, fixedint.UInt8(4)),
                (pow(2, 32) - 1, fixedint.UInt8(4)),
                (2047, fixedint.UInt8(5)),
            ]
        )
        # imm=0, rs1=0 try with both values at 0
        state.register_file.registers = [0, 4, -4, pow(2, 32) - 1]
        instr = LW(imm=0, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers, [16843009, 4, -4, pow(2, 32) - 1]
        )

        # imm=4, rs1=0 try with imm = 4
        state.register_file.registers = [0, 4, -4, pow(2, 32) - 1]
        instr = LW(imm=4, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers, [33686018, 4, -4, pow(2, 32) - 1]
        )

        # imm=0, rs1=4 try with rs1 value = 4
        state.register_file.registers = [0, 4, -4, pow(2, 32) - 1]
        instr = LW(imm=0, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers, [33686018, 4, -4, pow(2, 32) - 1]
        )

        # imm=4, rs1=4 try with both values = 4
        state.register_file.registers = [0, 4, -4, pow(2, 32) - 1]
        instr = LW(imm=4, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers, [50529027, 4, -4, pow(2, 32) - 1]
        )

        # imm=4, rs1=-4 try with negative value in rs1, equates to acces to memory 0
        state.register_file.registers = [0, 4, -4, pow(2, 32) - 1]
        instr = LW(imm=4, rs1=2, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers, [16843009, 4, -4, pow(2, 32) - 1]
        )

        # imm=1, rs1=2^32-1 try with really high value in rs1, equates to 0 because memory is circular
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

        # imm=10239, rs1=0 too high value in imm gets convertet to 12 bit i e 2047
        # FIXME
        # state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        # instr = LW(imm=10239, rs1=0, rd=0)
        # state = instr.behavior(state)
        # self.assertEqual(state.register_file.registers, [5, 1, -1, pow(2, 32) - 1])

        # imm=12, rs1=0 load negative value
        state.register_file.registers = [0, 4, -4, pow(2, 32) - 1]
        instr = LW(imm=12, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers,
            [fixedint.UInt32(-1), 4, -4, pow(2, 32) - 1],
        )

        # try memory acces to non existant address
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=16, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [0, 1, -1, pow(2, 32) - 1])

    def test_lbu(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[0, 1, -1, pow(2, 32) - 1]),
            memory=Memory(AddressingType.BYTE, 32, True),
        )
        state.memory.memory_file = dict(
            [
                (0, fixedint.UInt8(1)),
                (1, fixedint.UInt8(2)),
                (2, fixedint.UInt8(3)),
                (3, fixedint.UInt8(-1)),
                (pow(2, 32) - 1, fixedint.UInt8(4)),
                (2047, fixedint.UInt8(5)),
            ]
        )
        # imm=0, rs1=0 try with both values at 0
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LBU(imm=0, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1, 1, -1, pow(2, 32) - 1])

        # imm=1, rs1=0 try with imm = 1
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LBU(imm=1, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [2, 1, -1, pow(2, 32) - 1])

        # imm=0, rs1=1 try with rs1 value = 1
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LBU(imm=0, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [2, 1, -1, pow(2, 32) - 1])

        # imm=1, rs1=1 try with both values = 1
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LBU(imm=1, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [3, 1, -1, pow(2, 32) - 1])

        # imm=1, rs1=-1 try with negative value in rs1, equates to acces to memory 0
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LBU(imm=1, rs1=2, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1, 1, -1, pow(2, 32) - 1])

        # imm=1, rs1=2^32-1 try with really high value in rs1, equates to 0 because memory is circular
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LBU(imm=1, rs1=3, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1, 1, -1, pow(2, 32) - 1])

        # imm=0, rs1=-1 negative value of -1 gets converted to 2^32-1
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LBU(imm=0, rs1=2, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [4, 1, -1, pow(2, 32) - 1])

        # imm=10239, rs1=0 too high value in imm gets convertet to 12 bit i e 2047
        # FIXME
        # state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        # instr = LBU(imm=10239, rs1=0, rd=0)
        # state = instr.behavior(state)
        # self.assertEqual(state.register_file.registers, [5, 1, -1, pow(2, 32) - 1])

        # imm=3, rs1=0 load negative value
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LBU(imm=3, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [255, 1, -1, pow(2, 32) - 1])

        # try memory acces to non existant address
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=4, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [0, 1, -1, pow(2, 32) - 1])

    def test_lhu(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[0, 2, -2, pow(2, 32) - 1]),
            memory=Memory(AddressingType.BYTE, 32, True),
        )
        state.memory.memory_file = dict(
            [
                (0, fixedint.UInt8(1)),
                (1, fixedint.UInt8(2)),
                (2, fixedint.UInt8(3)),
                (3, fixedint.UInt8(4)),
                (4, fixedint.UInt8(5)),
                (5, fixedint.UInt8(6)),
                (6, fixedint.UInt8(-1)),
                (7, fixedint.UInt8(-1)),
                (pow(2, 32) - 2, fixedint.UInt8(7)),
                (pow(2, 32) - 1, fixedint.UInt8(8)),
                (2047, fixedint.UInt8(5)),
            ]
        )
        # imm=0, rs1=0 try with both values at 0
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LHU(imm=0, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [513, 2, -2, pow(2, 32) - 1])

        # imm=2, rs1=0 try with imm = 2
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LHU(imm=2, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1027, 2, -2, pow(2, 32) - 1])

        # imm=0, rs1=2 try with rs1 value = 2
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LHU(imm=0, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1027, 2, -2, pow(2, 32) - 1])

        # imm=2, rs1=2 try with both values = 2
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LHU(imm=2, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1541, 2, -2, pow(2, 32) - 1])

        # imm=2, rs1=-2 try with negative value in rs1, equates to acces to memory 0
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LHU(imm=2, rs1=2, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [513, 2, -2, pow(2, 32) - 1])

        # imm=1, rs1=2^32-1 try with really high value in rs1, equates to 0 because memory is circular
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LHU(imm=1, rs1=3, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [513, 2, -2, pow(2, 32) - 1])

        # imm=1, rs1=2 align error on memory address 3
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LHU(imm=1, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [1284, 2, -2, pow(2, 32) - 1])

        # imm=0, rs1=-2 negative value of -2 gets converted to 2^32-2
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LHU(imm=0, rs1=2, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [2055, 2, -2, pow(2, 32) - 1])

        # imm=10239, rs1=0 too high value in imm gets convertet to 12 bit i e 2047
        # FIXME
        # state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        # instr = LHU(imm=10239, rs1=0, rd=0)
        # state = instr.behavior(state)
        # self.assertEqual(state.register_file.registers, [5, 1, -1, pow(2, 32) - 1])

        # imm=6, rs1=0 load negative value
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LHU(imm=6, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [65535, 2, -2, pow(2, 32) - 1])

        # try memory acces to non existant address
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=8, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [0, 1, -1, pow(2, 32) - 1])

    def test_jalr(self):
        state = RiscvArchitecturalState(register_file=RegisterFile(registers=[0, 8]))
        # imm=8, rs1=0
        state.register_file.registers = [0, 8]
        state.program_counter = 0
        instr = JALR(imm=8, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [4, 8])
        self.assertEqual(state.program_counter, 4)

        # imm=0, rs1=8
        state.register_file.registers = [0, 8]
        state.program_counter = 0
        instr = JALR(imm=0, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [4, 8])
        self.assertEqual(state.program_counter, 4)

        # imm=8, rs1=8
        state.register_file.registers = [0, 8]
        state.program_counter = 0
        instr = JALR(imm=8, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [4, 8])
        self.assertEqual(state.program_counter, 12)

        # imm=7, rs1=8 seeing if least significant bit is set to 0
        state.register_file.registers = [0, 8]
        state.program_counter = 0
        instr = JALR(imm=7, rs1=1, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [4, 8])
        self.assertEqual(state.program_counter, 10)

    def test_ecall(self):
        # test 10 (exit 0)
        simulation = RiscvSimulation()
        simulation.state.instruction_memory.write_instructions(
            [ADDI(17, 0, 10), ECALL(), ADD(0, 0, 0)]
        )
        simulation.step()
        self.assertTrue(not simulation.is_done())
        simulation.step()
        self.assertTrue(simulation.is_done())
        self.assertEqual(simulation.state.exit_code, 0)

        # test 1, 11, 34, 35 (sint, char, hex, bin)
        simulation = RiscvSimulation()
        simulation.state.instruction_memory.write_instructions(
            [
                ADDI(17, 0, 1),
                ADDI(10, 0, 65),
                ECALL(),
                ADDI(17, 0, 11),
                ECALL(),
                ADDI(17, 0, 34),
                ECALL(),
                ADDI(17, 0, 35),
                ECALL(),
            ]
        )
        simulation.run()
        self.assertEqual(simulation.state.output, "65A0x410b1000001")

        # test 1, 36 (sint, uint)
        simulation = RiscvSimulation()
        simulation.state.instruction_memory.write_instructions(
            [ADDI(17, 0, 1), LUI(10, 0x80000), ECALL(), ADDI(17, 0, 36), ECALL()]
        )
        simulation.run()
        self.assertEqual(simulation.state.output, "-21474836482147483648")

        # test 2 (float)
        simulation = RiscvSimulation()
        simulation.state.instruction_memory.write_instructions(
            [ADDI(17, 0, 2), LUI(10, 0xBF400), ECALL()]
        )
        simulation.run()
        self.assertEqual(simulation.state.output, "-0.75")

        # test 4 (string)
        simulation = RiscvSimulation()
        simulation.state.instruction_memory.write_instructions(
            [
                ADDI(17, 0, 4),
                LUI(10, 0xF0000),
                ADDI(5, 0, 65),
                SB(10, 5, 0),
                ADDI(5, 0, 66),
                SB(10, 5, 1),
                ADDI(5, 0, 67),
                SB(10, 5, 2),
                ECALL(),
            ]
        )
        simulation.run()
        self.assertEqual(simulation.state.output, "ABC")

        # test 93 (exit with code)
        simulation = RiscvSimulation()
        simulation.state.instruction_memory.write_instructions(
            [ADDI(17, 0, 93), ADDI(10, 0, 42), ECALL(), ADD(0, 0, 0)]
        )
        simulation.step()
        simulation.step()
        self.assertTrue(not simulation.is_done())
        simulation.step()
        self.assertTrue(simulation.is_done())
        self.assertEqual(simulation.state.exit_code, 42)

    def test_ebreak(self):
        state = RiscvArchitecturalState(register_file=RegisterFile(registers=()))
        with self.assertRaises(InstructionNotImplemented) as cm:
            instr = EBREAK(imm=0, rs1=0, rd=0)
            state = instr.behavior(state)
        self.assertEqual(cm.exception, InstructionNotImplemented(mnemonic="ebreak"))

    def test_stype(self):
        stype = SB(rs1=0, rs2=0, imm=0)
        self.assertEqual(stype.imm, 0)
        stype = SB(rs1=0, rs2=0, imm=1)
        self.assertEqual(stype.imm, 1)
        stype = SB(rs1=0, rs2=0, imm=-1)
        self.assertEqual(stype.imm, -1)
        stype = SB(rs1=0, rs2=0, imm=2047)
        self.assertEqual(stype.imm, 2047)
        stype = SB(rs1=0, rs2=0, imm=-2048)
        self.assertEqual(stype.imm, -2048)
        stype = SB(rs1=0, rs2=0, imm=2048)
        self.assertEqual(stype.imm, -2048)
        stype = SB(rs1=0, rs2=0, imm=-2049)
        self.assertEqual(stype.imm, 2047)

    def test_sb(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.UInt32(0),
                    fixedint.UInt32(261),
                    fixedint.UInt32(257),
                    fixedint.UInt32(256),
                    fixedint.UInt32(128),
                    fixedint.UInt32(1024),
                ]
            ),
            memory=Memory(AddressingType.BYTE, 32, True),
        )
        sb_0 = SB(rs1=0, rs2=0, imm=0)
        state = sb_0.behavior(state)
        self.assertEqual(state.memory.read_byte(0), 0)

        sb_1 = SB(rs1=0, rs2=2, imm=1)
        state = sb_1.behavior(state)
        self.assertEqual(state.memory.read_byte(1), 1)

        sb_2 = SB(rs1=0, rs2=1, imm=1)
        state = sb_2.behavior(state)
        self.assertEqual(state.memory.read_byte(1), 5)

        sb_3 = SB(rs1=0, rs2=3, imm=0)
        state = sb_3.behavior(state)
        self.assertEqual(state.memory.read_byte(0), 0)

        sb_4 = SB(rs1=0, rs2=3, imm=1)
        state = sb_4.behavior(state)
        self.assertEqual(state.memory.read_byte(1), 0)

        sb_5 = SB(rs1=0, rs2=4, imm=2)
        state = sb_5.behavior(state)
        self.assertEqual(state.memory.read_byte(2), 128)

        sb_6 = SB(rs1=0, rs2=5, imm=2)
        state = sb_6.behavior(state)
        self.assertEqual(state.memory.read_byte(2), 0)

    def test_sh(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.UInt32(0),
                    fixedint.UInt32(65536),
                    fixedint.UInt32(65537),
                    fixedint.UInt32(65538),
                    fixedint.UInt32(3),
                    fixedint.UInt32(2),
                    fixedint.UInt32(255),
                    fixedint.UInt32(256),
                    fixedint.UInt32(65535),
                ]
            ),
            memory=Memory(AddressingType.BYTE, 32, True),
        )

        sh_0 = SH(rs1=0, rs2=0, imm=0)
        state = sh_0.behavior(state)
        self.assertEqual(int(state.memory.read_halfword(0)), 0)

        sh_1 = SH(rs1=0, rs2=1, imm=0)
        state = sh_1.behavior(state)
        self.assertEqual(int(state.memory.read_halfword(0)), 0)

        sh_2 = SH(rs1=0, rs2=2, imm=1)
        state = sh_2.behavior(state)
        self.assertEqual(int(state.memory.read_halfword(1)), 1)

        sh_3 = SH(rs1=0, rs2=3, imm=2)
        state = sh_3.behavior(state)
        self.assertEqual(int(state.memory.read_halfword(2)), 2)

        sh_4 = SH(rs1=0, rs2=4, imm=3)
        state = sh_4.behavior(state)
        self.assertEqual(int(state.memory.read_halfword(3)), 3)

        sh_5 = SH(rs1=0, rs2=6, imm=3)
        state = sh_5.behavior(state)
        self.assertEqual(int(state.memory.read_halfword(3)), 255)

        sh_6 = SH(rs1=0, rs2=7, imm=3)
        state = sh_6.behavior(state)
        self.assertEqual(int(state.memory.read_halfword(3)), 256)

        sh_7 = SH(rs1=0, rs2=8, imm=6)
        state = sh_7.behavior(state)
        self.assertEqual(int(state.memory.read_halfword(6)), 65535)

    def test_sw(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.UInt32(0),
                    fixedint.UInt32(1),
                    fixedint.UInt32(2),
                    fixedint.UInt32(100),
                    fixedint.UInt32(10),
                    fixedint.UInt32(255),
                    fixedint.UInt32(256),
                    fixedint.UInt32(4294967295),
                ]
            ),
            memory=Memory(AddressingType.BYTE, 32, True),
        )

        sw_0 = SW(rs1=0, rs2=0, imm=0)
        state = sw_0.behavior(state)
        self.assertEqual(int(state.memory.read_word(0)), 0)

        sw_1 = SW(rs1=0, rs2=1, imm=1)
        state = sw_1.behavior(state)
        self.assertEqual(int(state.memory.read_word(1)), 1)

        sw_2 = SW(rs1=0, rs2=2, imm=2)
        state = sw_2.behavior(state)
        self.assertEqual(int(state.memory.read_word(2)), 2)

        sw_3 = SW(rs1=0, rs2=3, imm=3)
        state = sw_3.behavior(state)
        self.assertEqual(int(state.memory.read_word(3)), 100)

        sw_4 = SW(rs1=0, rs2=4, imm=0)
        state = sw_4.behavior(state)
        self.assertEqual(int(state.memory.read_word(0)), 10)

        sw_5 = SW(rs1=0, rs2=5, imm=0)
        state = sw_5.behavior(state)
        self.assertEqual(int(state.memory.read_word(0)), 255)

        sw_6 = SW(rs1=0, rs2=6, imm=0)
        state = sw_6.behavior(state)
        self.assertEqual(int(state.memory.read_word(0)), 256)

        sw_7 = SW(rs1=0, rs2=7, imm=8)
        state = sw_7.behavior(state)
        self.assertEqual(int(state.memory.read_word(8)), 4294967295)

    def test_btype(self):
        btype = BEQ(rs1=0, rs2=0, imm=0)
        self.assertEqual(btype.imm, 0)
        btype = BEQ(rs1=0, rs2=0, imm=2)
        self.assertEqual(btype.imm, 2)
        btype = BEQ(rs1=0, rs2=0, imm=4094)
        self.assertEqual(btype.imm, 4094)
        btype = BEQ(rs1=0, rs2=0, imm=4096)
        self.assertEqual(btype.imm, -4096)
        btype = BEQ(rs1=0, rs2=0, imm=-4098)
        self.assertEqual(btype.imm, 4094)

    def test_beq(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.UInt32(0),
                    fixedint.UInt32(0),
                    fixedint.UInt32(1),
                ]
            )
        )

        # 0, 0
        state.program_counter = 0
        instruction = BEQ(rs1=0, rs2=1, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1
        state.program_counter = 0
        instruction = BEQ(rs1=0, rs2=2, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 0, 0 - negative immediate
        state.program_counter = 32
        instruction = BEQ(rs1=0, rs2=1, imm=-12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

    def test_bne(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.UInt32(0),
                    fixedint.UInt32(0),
                    fixedint.UInt32(1),
                ]
            )
        )

        # 0, 0
        state.program_counter = 0
        instruction = BNE(rs1=0, rs2=1, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 0, 1
        state.program_counter = 0
        instruction = BNE(rs1=0, rs2=2, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1 - negative immediate
        state.program_counter = 32
        instruction = BNE(rs1=0, rs2=2, imm=-12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

    def test_blt(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.UInt32(0),
                    fixedint.UInt32(0),
                    fixedint.UInt32(1),
                    fixedint.UInt32(pow(2, 32) - 1),
                    fixedint.UInt32(pow(2, 31)),
                ]
            )
        )

        # 0, 0
        state.program_counter = 0
        instruction = BLT(rs1=0, rs2=1, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 1, 0
        state.program_counter = 0
        instruction = BLT(rs1=2, rs2=0, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 0, 1
        state.program_counter = 0
        instruction = BLT(rs1=0, rs2=2, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1 - negative immediate
        state.program_counter = 32
        instruction = BLT(rs1=0, rs2=2, imm=-12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

        # 0, -1
        state.program_counter = 0
        instruction = BLT(rs1=0, rs2=3, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # -1, 0
        state.program_counter = 0
        instruction = BLT(rs1=3, rs2=0, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # -2^31, -1
        state.program_counter = 0
        instruction = BLT(rs1=4, rs2=3, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

    def test_bge(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.UInt32(0),
                    fixedint.UInt32(0),
                    fixedint.UInt32(1),
                    fixedint.UInt32(pow(2, 32) - 1),
                    fixedint.UInt32(pow(2, 31)),
                ]
            )
        )

        # 0, 0
        state.program_counter = 0
        instruction = BGE(rs1=0, rs2=1, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1
        state.program_counter = 0
        instruction = BGE(rs1=0, rs2=2, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 1, 0
        state.program_counter = 0
        instruction = BGE(rs1=2, rs2=0, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 1, 0 - negative immediate
        state.program_counter = 32
        instruction = BGE(rs1=2, rs2=0, imm=-12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

        # 0, -1
        state.program_counter = 0
        instruction = BGE(rs1=0, rs2=3, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # -2^31, -1
        state.program_counter = 0
        instruction = BGE(rs1=4, rs2=3, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

    def test_bltu(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.UInt32(0),
                    fixedint.UInt32(0),
                    fixedint.UInt32(1),
                    fixedint.UInt32(pow(2, 32) - 1),
                    fixedint.UInt32(pow(2, 31)),
                ]
            )
        )

        # 0, 0
        state.program_counter = 0
        instruction = BLTU(rs1=0, rs2=1, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 1, 0
        state.program_counter = 0
        instruction = BLTU(rs1=2, rs2=0, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 0, 1
        state.program_counter = 0
        instruction = BLTU(rs1=0, rs2=2, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1 - negative immediate
        state.program_counter = 32
        instruction = BLTU(rs1=0, rs2=2, imm=-12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

        # 0, (2^32 - 1)
        state.program_counter = 0
        instruction = BLTU(rs1=0, rs2=3, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # (2^32 - 1), 0
        state.program_counter = 0
        instruction = BLTU(rs1=3, rs2=0, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 2^31, (2^32 - 1)
        state.program_counter = 0
        instruction = BLTU(rs1=4, rs2=3, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

    def test_bgeu(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.UInt32(0),
                    fixedint.UInt32(0),
                    fixedint.UInt32(1),
                    fixedint.UInt32(pow(2, 32) - 1),
                    fixedint.UInt32(pow(2, 31)),
                ]
            )
        )

        # 0, 0
        state.program_counter = 0
        instruction = BGEU(rs1=0, rs2=1, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1
        state.program_counter = 0
        instruction = BGEU(rs1=0, rs2=2, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 1, 0
        state.program_counter = 0
        instruction = BGEU(rs1=2, rs2=0, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 1, 0 - negative immediate
        state.program_counter = 32
        instruction = BGEU(rs1=2, rs2=0, imm=-12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

        # 0, (2^32 - 1)
        state.program_counter = 0
        instruction = BGEU(rs1=0, rs2=3, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 2^31, (2^32 - 1)
        state.program_counter = 0
        instruction = BGEU(rs1=4, rs2=3, imm=12)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

    def test_utype(self):
        utype = LUI(rd=0, imm=0)
        self.assertEqual(utype.imm, 0)
        utype = LUI(rd=0, imm=1)
        self.assertEqual(utype.imm, 1)
        utype = LUI(rd=0, imm=-1)
        self.assertEqual(utype.imm, -1)
        utype = LUI(rd=0, imm=(2**19) - 1)
        self.assertEqual(utype.imm, (2**19) - 1)
        utype = LUI(rd=0, imm=-(2**19))
        self.assertEqual(utype.imm, -(2**19))
        utype = LUI(rd=0, imm=2**19)
        self.assertEqual(utype.imm, -(2**19))
        utype = LUI(rd=0, imm=-(2**19) - 1)
        self.assertEqual(utype.imm, (2**19) - 1)

    def test_lui(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[0, 1, 2, 3])
        )

        lui_0 = LUI(rd=0, imm=0)
        state = lui_0.behavior(state)
        self.assertEqual(int(state.register_file.registers[0]), 0)

        lui_1 = LUI(rd=0, imm=1)
        state = lui_1.behavior(state)
        self.assertEqual(int(state.register_file.registers[0]), 4096)

        lui_2 = LUI(rd=2, imm=2)
        state = lui_2.behavior(state)
        self.assertEqual(int(state.register_file.registers[2]), 8192)

        lui_3 = LUI(rd=1, imm=3)
        state = lui_3.behavior(state)
        self.assertEqual(int(state.register_file.registers[1]), 12288)

        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[0, 0, 0, 0, 0])
        )
        lui_1 = LUI(rd=0, imm=2097151)
        state = lui_1.behavior(state)
        self.assertEqual(int(state.register_file.registers[0]), fixedint.UInt32(-4096))
        lui_1 = LUI(rd=0, imm=2097152)
        state = lui_1.behavior(state)
        self.assertEqual(int(state.register_file.registers[0]), fixedint.UInt32(0))
        lui_1 = LUI(rd=0, imm=-1)
        state = lui_1.behavior(state)
        self.assertEqual(int(state.register_file.registers[0]), fixedint.UInt32(-4096))

    def test_auipc(self):
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[0, 1, 2, 3])
        )

        state.program_counter = 0
        auipc_0 = AUIPC(rd=0, imm=0)
        state = auipc_0.behavior(state)
        self.assertEqual(int(state.register_file.registers[0]), 0)

        auipc_1 = AUIPC(rd=0, imm=1)
        state = auipc_1.behavior(state)
        self.assertEqual(int(state.register_file.registers[0]), 4096)

        state.program_counter = 1
        auipc_2 = AUIPC(rd=1, imm=2)
        state = auipc_2.behavior(state)
        self.assertEqual(int(state.register_file.registers[1]), 8193)

        state.program_counter = 2
        auipc_3 = AUIPC(rd=3, imm=3)
        state = auipc_3.behavior(state)
        self.assertEqual(int(state.register_file.registers[3]), 12290)

        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[0, 0, 0, 0])
        )

        state.program_counter = 0
        auipc_0 = AUIPC(rd=0, imm=2097151)
        state = auipc_0.behavior(state)
        self.assertEqual(int(state.register_file.registers[0]), fixedint.UInt32(-4096))
        auipc_0 = AUIPC(rd=0, imm=2097152)
        state = auipc_0.behavior(state)
        self.assertEqual(int(state.register_file.registers[0]), fixedint.UInt32(0))
        auipc_0 = AUIPC(rd=0, imm=-1)
        state = auipc_0.behavior(state)
        self.assertEqual(int(state.register_file.registers[0]), fixedint.UInt32(-4096))
        state.program_counter = 4
        auipc_0 = AUIPC(rd=0, imm=2097151)
        state = auipc_0.behavior(state)
        self.assertEqual(int(state.register_file.registers[0]), fixedint.UInt32(-4092))

    def test_jtype(self):
        jtype = JAL(rd=0, imm=0)
        self.assertEqual(jtype.imm, 0)
        jtype = JAL(rd=0, imm=2)
        self.assertEqual(jtype.imm, 2)
        jtype = JAL(rd=0, imm=-2)
        self.assertEqual(jtype.imm, -2)
        jtype = JAL(rd=0, imm=(2**20) - 2)
        self.assertEqual(jtype.imm, (2**20) - 2)
        jtype = JAL(rd=0, imm=-(2**20))
        self.assertEqual(jtype.imm, -(2**20))
        jtype = JAL(rd=0, imm=(2**20))
        self.assertEqual(jtype.imm, -(2**20))
        jtype = JAL(rd=0, imm=-(2**20) - 2)
        self.assertEqual(jtype.imm, (2**20) - 2)

    def test_jal(self):
        state = RiscvArchitecturalState(register_file=RegisterFile(registers=[1, 1, 1]))
        state.program_counter = 0
        jal_1 = JAL(rd=0, imm=4)
        state = jal_1.behavior(state)
        self.assertEqual(state.program_counter, 0)
        self.assertEqual(int(state.register_file.registers[0]), 4)

        state.program_counter = 2
        jal_2 = JAL(rd=0, imm=10)
        state = jal_2.behavior(state)
        self.assertEqual(state.program_counter, 8)
        self.assertEqual(int(state.register_file.registers[0]), 6)

        state.program_counter = 2
        jal_3 = JAL(rd=0, imm=8)
        state = jal_3.behavior(state)
        self.assertEqual(state.program_counter, 6)
        self.assertEqual(int(state.register_file.registers[0]), 6)

        state.program_counter = 4
        jal_4 = JAL(rd=1, imm=8)
        state = jal_4.behavior(state)
        self.assertEqual(state.program_counter, 8)
        self.assertEqual(int(state.register_file.registers[1]), 8)

        state.program_counter = 8
        jal_5 = JAL(rd=1, imm=10)
        state = jal_5.behavior(state)
        self.assertEqual(state.program_counter, 14)
        self.assertEqual(int(state.register_file.registers[1]), 12)

    def test_csrrw_privilege_level_too_low(self):
        state = RiscvArchitecturalState(register_file=RegisterFile(registers=[0, 2]))
        state.csr_registers.privilege_level = 0
        with self.assertRaises(CSRError) as context:
            state.csr_registers.write_word(3000, fixedint.UInt32(3))
        self.assertTrue(
            "illegal action: privilege level too low to access this csr register"
            in str(context.exception)
        )

    def test_csrrw_attempting_to_write_to_read_only(self):
        state = RiscvArchitecturalState(register_file=RegisterFile(registers=[0, 2]))
        with self.assertRaises(CSRError) as context:
            state.csr_registers.write_word(3072, fixedint.UInt32(3))
        self.assertTrue(
            "illegal action: attempting to write into read-only csr register"
            in str(context.exception)
        )

    def test_csrrw_invalid_address(self):
        state = RiscvArchitecturalState(register_file=RegisterFile(registers=[0, 2]))
        state.csr_registers.privilege_level = 4
        with self.assertRaises(CSRError) as context:
            state.csr_registers.write_word(7000, fixedint.UInt32(3))
        self.assertTrue(
            "illegal action: csr register does not exist" in str(context.exception)
        )

    def test_csrrw(self):
        fixedint.UInt32(0)
        fixedint.UInt32(1)
        state = RiscvArchitecturalState(register_file=RegisterFile(registers=[0, 2]))
        cssrw_1 = CSRRW(csr=0, rs1=1, rd=0)
        state.csr_registers.write_word(0, fixedint.UInt32(3))
        state.csr_registers.privilege_level = 4
        state = cssrw_1.behavior(state)
        self.assertEqual(state.register_file.registers, [3, 2])
        self.assertEqual(state.csr_registers.read_word(cssrw_1.csr), 2)

    def test_csrrs(self):
        max_number = fixedint.UInt32(0xFF_FF_FF_FF)
        test_number_1 = fixedint.UInt32(0xFF_FF_FF_FE)
        test_mask_1 = fixedint.UInt32(0x00_00_00_01)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[0, test_mask_1])
        )
        state.csr_registers.write_word(0, test_number_1)
        cssrs_1 = CSRRS(csr=0, rs1=1, rd=0)
        state = cssrs_1.behavior(state)
        self.assertEqual(state.register_file.registers, [test_number_1, test_mask_1])
        self.assertEqual(state.csr_registers.read_word(cssrs_1.csr), max_number)

    def test_csrrc(self):
        max_number = fixedint.UInt32(0xFF_FF_FF_FF)
        test_result_1 = fixedint.UInt32(0x00_00_00_01)
        test_mask_1 = fixedint.UInt32(0xFF_FF_FF_FE)
        state = RiscvArchitecturalState(
            register_file=RegisterFile(registers=[0, test_mask_1])
        )
        state.csr_registers.write_word(0, max_number)
        cssrc_1 = CSRRC(csr=0, rs1=1, rd=0)
        state = cssrc_1.behavior(state)
        self.assertEqual(state.register_file.registers, [max_number, test_mask_1])
        self.assertEqual(state.csr_registers.read_word(cssrc_1.csr), test_result_1)

    def test_csritype(self):
        cssrwi_1 = CSRRWI(csr=0, rd=0, uimm=0)
        self.assertEqual(cssrwi_1.uimm, 0)
        cssrwi_1 = CSRRWI(csr=0, rd=0, uimm=1)
        self.assertEqual(cssrwi_1.uimm, 1)
        cssrwi_1 = CSRRWI(csr=0, rd=0, uimm=31)
        self.assertEqual(cssrwi_1.uimm, 31)
        cssrwi_1 = CSRRWI(csr=0, rd=0, uimm=32)
        self.assertEqual(cssrwi_1.uimm, 0)
        cssrwi_1 = CSRRWI(csr=0, rd=0, uimm=-1)
        self.assertEqual(cssrwi_1.uimm, 31)

    def test_csrrwi(self):
        state = RiscvArchitecturalState(register_file=RegisterFile(registers=[0]))
        state.csr_registers.write_word(0, 3)
        cssrwi_1 = CSRRWI(csr=0, uimm=4, rd=0)
        state = cssrwi_1.behavior(state)
        self.assertEqual(state.register_file.registers, [3])
        self.assertEqual(state.csr_registers.read_word(cssrwi_1.csr), 4)

    def test_csrrsi(self):
        max_number = fixedint.UInt32(0xFF_FF_FF_FF)
        test_number_1 = fixedint.UInt32(0xFF_FF_FF_FE)
        test_mask_1 = 1
        state = RiscvArchitecturalState(register_file=RegisterFile(registers=[0]))
        cssrsi_1 = CSRRSI(csr=0, uimm=test_mask_1, rd=0)
        state.csr_registers.write_word(0, test_number_1)
        state = cssrsi_1.behavior(state)
        self.assertEqual(state.register_file.registers, [test_number_1])
        self.assertEqual(state.csr_registers.read_word(cssrsi_1.csr), max_number)

    def test_csrrci(self):
        max_number = fixedint.UInt32(0xFF_FF_FF_FF)
        test_result_1 = fixedint.UInt32(0xFF_FF_FF_FE)
        test_mask_1 = 1
        state = RiscvArchitecturalState(register_file=RegisterFile(registers=[0]))
        state.csr_registers.write_word(0, max_number)
        cssrci_1 = CSRRCI(csr=0, uimm=test_mask_1, rd=0)
        state = cssrci_1.behavior(state)
        self.assertEqual(state.register_file.registers, [max_number])
        self.assertEqual(state.csr_registers.read_word(cssrci_1.csr), test_result_1)

    def test_repr_1(self):
        # Tests that the __repr__() method for the instructions works as intended
        # Test R-Type
        r_type_ex_add = ADD(rd=4, rs1=5, rs2=6)
        self.assertEqual(r_type_ex_add.__repr__(), "add x4, x5, x6")

        r_type_ex_or = OR(rd=0, rs1=31, rs2=30)
        self.assertEqual(r_type_ex_or.__repr__(), "or x0, x31, x30")

        # Test I-Type
        # Test instructions that use default repr
        i_type_ex_addi = ADDI(rd=3, rs1=4, imm=32)
        self.assertEqual(i_type_ex_addi.__repr__(), "addi x3, x4, 32")

        i_type_ex_ori = ORI(rd=31, rs1=30, imm=-12)
        self.assertEqual(i_type_ex_ori.__repr__(), "ori x31, x30, -12")

        # Test e-instructions
        i_type_ex_ecall = ECALL(rd=0, rs1=0, imm=0)
        self.assertEqual(i_type_ex_ecall.__repr__(), "ecall")

        i_type_ex_ebreak = EBREAK(rd=0, rs1=0, imm=0)
        self.assertEqual(i_type_ex_ebreak.__repr__(), "ebreak")

        # Test instructions that use memory layout
        i_type_ex_lb = LB(rd=0, rs1=8, imm=-12)
        self.assertEqual(i_type_ex_lb.__repr__(), "lb x0, -12(x8)")

        i_type_ex_lh = LH(rd=0, rs1=8, imm=-12)
        self.assertEqual(i_type_ex_lh.__repr__(), "lh x0, -12(x8)")

        i_type_ex_lw = LW(rd=0, rs1=8, imm=-12)
        self.assertEqual(i_type_ex_lw.__repr__(), "lw x0, -12(x8)")

        i_type_ex_lbu = LBU(rd=0, rs1=8, imm=4)
        self.assertEqual(i_type_ex_lbu.__repr__(), "lbu x0, 4(x8)")

        i_type_ex_lhu = LHU(rd=0, rs1=8, imm=4)
        self.assertEqual(i_type_ex_lhu.__repr__(), "lhu x0, 4(x8)")

        # Test S-Type
        s_type_ex_sb = SB(rs1=8, rs2=11, imm=16)
        self.assertEqual(s_type_ex_sb.__repr__(), "sb x11, 16(x8)")

        s_type_ex_sw = SW(rs1=5, rs2=31, imm=-4)
        self.assertEqual(s_type_ex_sw.__repr__(), "sw x31, -4(x5)")

        # Test B-Type
        b_type_ex_beq = BEQ(rs1=4, rs2=5, imm=24)
        self.assertEqual(b_type_ex_beq.__repr__(), "beq x4, x5, 24")

        b_type_ex_bltu = BLTU(rs1=30, rs2=31, imm=-6)
        self.assertEqual(b_type_ex_bltu.__repr__(), "bltu x30, x31, -6")

        # Test U-Type
        u_type_ex_lui = LUI(rd=16, imm=123)
        self.assertEqual(u_type_ex_lui.__repr__(), "lui x16, 123")

        u_type_ex_auipc = AUIPC(rd=31, imm=-4)
        self.assertEqual(u_type_ex_auipc.__repr__(), "auipc x31, -4")

        # Test J-Type
        j_type_ex_jal = JAL(rd=23, imm=60)
        self.assertEqual(j_type_ex_jal.__repr__(), "jal x23, 60")

        # TODO: Change me, if Fence gets implemented
        # fence_ex = FENCE()
        # self.assertEqual(fence_ex.__repr__(),"fence")

        # Test CSR-Type
        csr_type_ex_csrrw = CSRRW(rd=0, csr=0xF, rs1=12)
        self.assertEqual(csr_type_ex_csrrw.__repr__(), "csrrw x0, 0xf, x12")

        csr_type_ex_csrrs = CSRRS(rd=31, csr=0xAC, rs1=7)
        self.assertEqual(csr_type_ex_csrrs.__repr__(), "csrrs x31, 0xac, x7")

        # Test CSR-imm-Type
        csri_type_ex_csrrwi = CSRRWI(rd=12, csr=0x448, uimm=20)
        self.assertEqual(csri_type_ex_csrrwi.__repr__(), "csrrwi x12, 0x448, 20")

        csri_type_ex_csrrci = CSRRCI(rd=0, csr=0x40F, uimm=16)
        self.assertEqual(csri_type_ex_csrrci.__repr__(), "csrrci x0, 0x40f, 16")

    def test_repr_2(self):
        # Test using the parser
        text = """add x4, x5, x6
or x0, x31, x30
addi x3, x4, 32
ori x31, x30, 12
ecall
ebreak
lb x0, 12(x8)
lh x0, 12(x8)
lw x0, 12(x8)
lbu x0, 4(x8)
lhu x0, 4(x8)
sb x11, 16(x8)
sw x31, 4(x5)
beq x4, x5, 48
bltu x30, x31, 12
lui x16, 123
auipc x31, 4
jal x23, 120
csrrw x0, 0xf, x12
csrrs x31, 0xac, x7
csrrwi x12, 0x448, 20
csrrci x0, 0x40f, 16"""
        parser = RiscvParser()
        state = RiscvArchitecturalState()

        parser.parse(text, state)

        instructions = list(state.instruction_memory.instructions.values())
        for instruction, line in zip(instructions, text.splitlines()):
            self.assertEqual(str(instruction), line)

    def test_mul(self):

        left_right_res_values = [
            (2**16 - 1, 2**16 - 1, 4294836225),
            (0, 101, 0),
            (1, 1, 1),
            (2**16, 2**16, 0),
            (-1, -1, 1),
            (-10, 1, -10),
            (110, -7, -770),
            (55, 11, 605),
            (2**24 + 17, 2**23 + 81, 1501562209),
        ]
        mul = MUL(rs1=0, rs2=1, rd=2)
        for left, right, res in left_right_res_values:
            state = RiscvArchitecturalState(
                register_file=RegisterFile(
                    registers=[
                        fixedint.UInt32(left),
                        fixedint.UInt32(right),
                        fixedint.UInt32(0),
                    ]
                )
            )
            state = mul.behavior(state)
            self.assertEqual(
                state.register_file.registers,
                [fixedint.UInt32(left), fixedint.UInt32(right), fixedint.UInt32(res)],
            )

            self.assertEqual(
                fixedint.UInt32(mul.alu_compute(left, right)[1]), fixedint.UInt32(res)
            )

    def test_mulh(self):

        left_right_res_values = [
            (0x80000000, 0x7FFFFFFF, 0xC0000000),
            (0xFFFFFFFF, 0xFFFFFFFF, 0x0),
            (0xFFFFFF9D, 0x6F, 0xFFFFFFFF),
            (0, -1, 0),
            (0xF000000E, 0xFFFFFF, 0xFFF00000),
        ]
        mulh = MULH(rs1=0, rs2=1, rd=2)
        for left, right, res in left_right_res_values:
            state = RiscvArchitecturalState(
                register_file=RegisterFile(
                    registers=[
                        fixedint.UInt32(left),
                        fixedint.UInt32(right),
                        fixedint.UInt32(0),
                    ]
                )
            )
            state = mulh.behavior(state)
            self.assertEqual(
                state.register_file.registers,
                [fixedint.UInt32(left), fixedint.UInt32(right), fixedint.UInt32(res)],
            )

            self.assertEqual(
                fixedint.UInt32(mulh.alu_compute(left, right)[1]), fixedint.UInt32(res)
            )

    def test_mulhu(self):

        left_right_res_values = [
            (0x80000000, 0x7FFFFFFF, 0x3FFFFFFF),
            (0xFFFFFFFF, 0xFFFFFFFF, 2**64 - 2**33 + 1 >> 32),
            (0xFFFFFF9D, 0x6F, 0x6E),
            (0x0, 0xFFFFFFFF, 0x0),
            (0xF000000E, 0xFFFFFF, 0xEFFFFF),
            (2**31, 2**31, 2**30),
        ]
        mulhu = MULHU(rs1=0, rs2=1, rd=2)
        for left, right, res in left_right_res_values:
            state = RiscvArchitecturalState(
                register_file=RegisterFile(
                    registers=[
                        fixedint.UInt32(left),
                        fixedint.UInt32(right),
                        fixedint.UInt32(0),
                    ]
                )
            )
            state = mulhu.behavior(state)
            self.assertEqual(
                state.register_file.registers,
                [fixedint.UInt32(left), fixedint.UInt32(right), fixedint.UInt32(res)],
            )

            self.assertEqual(
                fixedint.UInt32(mulhu.alu_compute(left, right)[1]), fixedint.UInt32(res)
            )

    def test_mulhsu(self):

        left_right_res_values = [
            (0x80000000, 0x7FFFFFFF, 0xC0000000),
            (0x7FFFFFFF, 0x80000000, 0x3FFFFFFF),
            (0x0, 0x457, 0x0),
            (0x457, 0x0, 0x0),
            (0xFFFE72AC, 0x7, 0xFFFFFFFF),
            (0x7, 0xFFFE72AC, 0x6),
        ]
        mulhsu = MULHSU(rs1=0, rs2=1, rd=2)
        for left, right, res in left_right_res_values:
            state = RiscvArchitecturalState(
                register_file=RegisterFile(
                    registers=[
                        fixedint.UInt32(left),
                        fixedint.UInt32(right),
                        fixedint.UInt32(0),
                    ]
                )
            )
            state = mulhsu.behavior(state)
            self.assertEqual(
                state.register_file.registers,
                [fixedint.UInt32(left), fixedint.UInt32(right), fixedint.UInt32(res)],
            )

            self.assertEqual(
                fixedint.UInt32(mulhsu.alu_compute(left, right)[1]),
                fixedint.UInt32(res),
            )

    def test_div(self):

        left_right_res_values = [
            (11, 0, -1),
            (0, 11, 0),
            (-1, -1, 1),
            (2**31 - 1, 1, 2**31 - 1),
            (100, -10, -10),
            (-100, 10, -10),
            (79, 11, 7),
            (-(2**31), -1, -(2**31)),
            (121, -12, -10),
        ]
        div = DIV(rs1=0, rs2=1, rd=2)
        for left, right, res in left_right_res_values:
            state = RiscvArchitecturalState(
                register_file=RegisterFile(
                    registers=[
                        fixedint.UInt32(left),
                        fixedint.UInt32(right),
                        fixedint.UInt32(0),
                    ]
                )
            )
            state = div.behavior(state)
            self.assertEqual(
                state.register_file.registers,
                [fixedint.UInt32(left), fixedint.UInt32(right), fixedint.UInt32(res)],
            )

            self.assertEqual(
                fixedint.UInt32(div.alu_compute(left, right)[1]),
                fixedint.UInt32(res),
            )

    def test_divu(self):

        left_right_res_values = [
            (10, 0, -1),
            (0, 0, -1),
            (2**16, 2, 2**15),
            (0, 100, 0),
            (2**32 - 1, 5, 858_993_459),
        ]
        divu = DIVU(rs1=0, rs2=1, rd=2)
        for left, right, res in left_right_res_values:
            state = RiscvArchitecturalState(
                register_file=RegisterFile(
                    registers=[
                        fixedint.UInt32(left),
                        fixedint.UInt32(right),
                        fixedint.UInt32(0),
                    ]
                )
            )
            state = divu.behavior(state)
            self.assertEqual(
                state.register_file.registers,
                [fixedint.UInt32(left), fixedint.UInt32(right), fixedint.UInt32(res)],
            )

            self.assertEqual(
                fixedint.UInt32(divu.alu_compute(left, right)[1]),
                fixedint.UInt32(res),
            )

    def test_rem(self):

        left_right_res_values = [
            (7, 2, 1),
            (111, 0, 111),
            (-(2**31), -1, 0),
            (7, 10, 7),
            (-10, -10, 0),
            (-7, 3, -1),
            (11, -3, 2),
            (121, -12, 1),
        ]
        rem = REM(rs1=0, rs2=1, rd=2)
        for left, right, res in left_right_res_values:
            state = RiscvArchitecturalState(
                register_file=RegisterFile(
                    registers=[
                        fixedint.UInt32(left),
                        fixedint.UInt32(right),
                        fixedint.UInt32(0),
                    ]
                )
            )
            state = rem.behavior(state)
            self.assertEqual(
                state.register_file.registers,
                [fixedint.UInt32(left), fixedint.UInt32(right), fixedint.UInt32(res)],
            )

            self.assertEqual(
                fixedint.UInt32(rem.alu_compute(left, right)[1]),
                fixedint.UInt32(res),
            )

    def test_remu(self):

        left_right_res_values = [
            (110, 0, 110),
            (0, 0, 0),
            (0xFFFFFFFE, 0xFFFFFFFF, 0xFFFFFFFE),
            (10, -1, 10),
            (-107, -1, -107),
            (17, 20, 17),
            (11, 5, 1),
        ]
        remu = REMU(rs1=0, rs2=1, rd=2)
        for left, right, res in left_right_res_values:
            state = RiscvArchitecturalState(
                register_file=RegisterFile(
                    registers=[
                        fixedint.UInt32(left),
                        fixedint.UInt32(right),
                        fixedint.UInt32(0),
                    ]
                )
            )
            state = remu.behavior(state)
            self.assertEqual(
                state.register_file.registers,
                [fixedint.UInt32(left), fixedint.UInt32(right), fixedint.UInt32(res)],
            )

            self.assertEqual(
                fixedint.UInt32(remu.alu_compute(left, right)[1]),
                fixedint.UInt32(res),
            )
