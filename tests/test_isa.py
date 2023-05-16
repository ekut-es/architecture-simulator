import unittest

from architecture_simulator.uarch.architectural_state import RegisterFile, Memory
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
    fence,
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
    EBREAKException,
    ECALLException,
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

import fixedint


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

        # 16 + (-7) = 9 (non edge case addition)
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

        # 0 + 0 = 0
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
        # Number defintions
        num_all_but_msb = fixedint.MutableUInt32(2147483647)
        num_msb = fixedint.MutableUInt32(2147483648)
        num_all_bits = fixedint.MutableUInt32(4294967295)
        num_0 = fixedint.MutableUInt32(0)

        num_a = fixedint.MutableUInt32(0x_FF_FF_00_FF)
        num_b = fixedint.MutableUInt32(0x_FF_FF_0F_0F)
        num_c = fixedint.MutableUInt32(0x_00_00_0F_F0)

        # general test case
        xor = XOR(rs1=0, rs2=1, rd=2)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[num_all_but_msb, num_all_bits, num_0])
        )
        state = xor.behavior(state)
        self.assertEqual(
            state.register_file.registers, [num_all_but_msb, num_all_bits, num_msb]
        )

        # test all combinations of bit pairs
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

        # zero xor zero = zero
        xor = XOR(rs1=0, rs2=0, rd=1)
        state = ArchitecturalState(register_file=RegisterFile(registers=[num_0, num_b]))
        state = xor.behavior(state)
        self.assertEqual(state.register_file.registers, [num_0, num_0])

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
        # Number definitions
        num_a = fixedint.MutableUInt32(0x00_FF_00_12)
        num_b = fixedint.MutableUInt32(0x0F_0F_00_00)
        num_c = fixedint.MutableUInt32(0x0F_FF_00_12)

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
        # Number defintions
        num_a = fixedint.MutableUInt32(0x00_FF_00_12)
        num_b = fixedint.MutableUInt32(0x0F_0F_00_00)
        num_c = fixedint.MutableUInt32(0x00_0F_00_00)

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

    def test_csrrw_privilege_level_too_low(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 2]))
        state.csr_registers.privilege_level = 0
        with self.assertRaises(Exception) as context:
            state.csr_registers.store_word(3000, fixedint.MutableUInt32(3))
        self.assertTrue(
            "illegal action: privilege level too low to access this csr register"
            in str(context.exception)
        )

    def test_csrrw_attempting_to_write_to_read_only(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 2]))
        with self.assertRaises(Exception) as context:
            state.csr_registers.store_word(3072, fixedint.MutableUInt32(3))
        self.assertTrue(
            "illegal action: attempting to write into read-only csr register"
            in str(context.exception)
        )

    def test_csrrw_invalid_adress(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 2]))
        state.csr_registers.privilege_level = 4
        with self.assertRaises(Exception) as context:
            state.csr_registers.store_word(7000, fixedint.MutableUInt32(3))
        self.assertTrue(
            "illegal action: csr register does not exist" in str(context.exception)
        )

    def test_csrrw(self):
        fixedint.MutableUInt32(0)
        fixedint.MutableUInt32(1)
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 2]))
        cssrw_1 = CSRRW(csr=0, rs1=1, rd=0)
        state.csr_registers.store_word(0, fixedint.MutableUInt32(3))
        state.csr_registers.privilege_level = 4
        state = cssrw_1.behavior(state)
        self.assertEqual(state.register_file.registers, [3, 2])
        self.assertEqual(state.csr_registers.load_word(cssrw_1.csr), 2)

    def test_csrrs(self):
        max_number = fixedint.MutableUInt32(0xFF_FF_FF_FF)
        test_number_1 = fixedint.MutableUInt32(0xFF_FF_FF_FE)
        test_mask_1 = fixedint.MutableUInt32(0x00_00_00_01)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[0, test_mask_1])
        )
        state.csr_registers.store_word(0, test_number_1)
        cssrs_1 = CSRRS(csr=0, rs1=1, rd=0)
        state = cssrs_1.behavior(state)
        self.assertEqual(state.register_file.registers, [test_number_1, test_mask_1])
        self.assertEqual(state.csr_registers.load_word(cssrs_1.csr), max_number)

    def test_csrrc(self):
        max_number = fixedint.MutableUInt32(0xFF_FF_FF_FF)
        test_result_1 = fixedint.MutableUInt32(0x00_00_00_01)
        test_mask_1 = fixedint.MutableUInt32(0xFF_FF_FF_FE)
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[0, test_mask_1])
        )
        state.csr_registers.store_word(0, max_number)
        cssrc_1 = CSRRC(csr=0, rs1=1, rd=0)
        state = cssrc_1.behavior(state)
        self.assertEqual(state.register_file.registers, [max_number, test_mask_1])
        self.assertEqual(state.csr_registers.load_word(cssrc_1.csr), test_result_1)

    def test_csrrwi(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0]))
        state.csr_registers.store_word(0, 3)
        cssrwi_1 = CSRRWI(csr=0, uimm=4, rd=0)
        state = cssrwi_1.behavior(state)
        self.assertEqual(state.register_file.registers, [3])
        self.assertEqual(state.csr_registers.load_word(cssrwi_1.csr), 4)

    def test_csrrsi(self):
        max_number = fixedint.MutableUInt32(0xFF_FF_FF_FF)
        test_number_1 = fixedint.MutableUInt32(0xFF_FF_FF_FE)
        test_mask_1 = fixedint.MutableUInt32(0x00_00_00_01)
        state = ArchitecturalState(register_file=RegisterFile(registers=[0]))
        cssrsi_1 = CSRRSI(csr=0, uimm=test_mask_1, rd=0)
        state.csr_registers.store_word(0, test_number_1)
        state = cssrsi_1.behavior(state)
        self.assertEqual(state.register_file.registers, [test_number_1])
        self.assertEqual(state.csr_registers.load_word(cssrsi_1.csr), max_number)

    def test_csrrci(self):
        max_number = fixedint.MutableUInt32(0xFF_FF_FF_FF)
        test_result_1 = fixedint.MutableUInt32(0x00_00_00_01)
        test_mask_1 = fixedint.MutableUInt32(0xFF_FF_FF_FE)
        state = ArchitecturalState(register_file=RegisterFile(registers=[0]))
        state.csr_registers.store_word(0, max_number)
        cssrci_1 = CSRRCI(csr=0, uimm=test_mask_1, rd=0)
        state = cssrci_1.behavior(state)
        self.assertEqual(state.register_file.registers, [max_number])
        self.assertEqual(state.csr_registers.load_word(cssrci_1.csr), test_result_1)

    def test_btype(self):
        # valid immediates
        try:
            BTypeInstruction(rs1=0, rs2=0, imm=0, mnemonic="x")
            BTypeInstruction(rs1=0, rs2=0, imm=2047, mnemonic="x")
            BTypeInstruction(rs1=0, rs2=0, imm=-2048, mnemonic="x")
        except Exception:
            print(Exception)
            self.fail("BTypeInstruction raised an exception upon instantiation")

        # invalid immediates
        with self.assertRaises(ValueError):
            BTypeInstruction(rs1=0, rs2=0, imm=-2049, mnemonic="x")
        with self.assertRaises(ValueError):
            BTypeInstruction(rs1=0, rs2=0, imm=2048, mnemonic="x")

    def test_beq(self):
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(1),
                ]
            )
        )

        # 0, 0
        state.program_counter = 0
        instruction = BEQ(rs1=0, rs2=1, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1
        state.program_counter = 0
        instruction = BEQ(rs1=0, rs2=2, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 0, 0 - negative immediate
        state.program_counter = 32
        instruction = BEQ(rs1=0, rs2=1, imm=-6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

    def test_bne(self):
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(1),
                ]
            )
        )

        # 0, 0
        state.program_counter = 0
        instruction = BNE(rs1=0, rs2=1, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 0, 1
        state.program_counter = 0
        instruction = BNE(rs1=0, rs2=2, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1 - negative immediate
        state.program_counter = 32
        instruction = BNE(rs1=0, rs2=2, imm=-6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

    def test_blt(self):
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(1),
                    fixedint.MutableUInt32(pow(2, 32) - 1),
                    fixedint.MutableUInt32(pow(2, 31)),
                ]
            )
        )

        # 0, 0
        state.program_counter = 0
        instruction = BLT(rs1=0, rs2=1, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 1, 0
        state.program_counter = 0
        instruction = BLT(rs1=2, rs2=0, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 0, 1
        state.program_counter = 0
        instruction = BLT(rs1=0, rs2=2, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1 - negative immediate
        state.program_counter = 32
        instruction = BLT(rs1=0, rs2=2, imm=-6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

        # 0, -1
        state.program_counter = 0
        instruction = BLT(rs1=0, rs2=3, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # -1, 0
        state.program_counter = 0
        instruction = BLT(rs1=3, rs2=0, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # -2^31, -1
        state.program_counter = 0
        instruction = BLT(rs1=4, rs2=3, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

    def test_bge(self):
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(1),
                    fixedint.MutableUInt32(pow(2, 32) - 1),
                    fixedint.MutableUInt32(pow(2, 31)),
                ]
            )
        )

        # 0, 0
        state.program_counter = 0
        instruction = BGE(rs1=0, rs2=1, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1
        state.program_counter = 0
        instruction = BGE(rs1=0, rs2=2, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 1, 0
        state.program_counter = 0
        instruction = BGE(rs1=2, rs2=0, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 1, 0 - negative immediate
        state.program_counter = 32
        instruction = BGE(rs1=2, rs2=0, imm=-6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

        # 0, -1
        state.program_counter = 0
        instruction = BGE(rs1=0, rs2=3, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # -2^31, -1
        state.program_counter = 0
        instruction = BGE(rs1=4, rs2=3, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

    def test_bltu(self):
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(1),
                    fixedint.MutableUInt32(pow(2, 32) - 1),
                    fixedint.MutableUInt32(pow(2, 31)),
                ]
            )
        )

        # 0, 0
        state.program_counter = 0
        instruction = BLTU(rs1=0, rs2=1, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 1, 0
        state.program_counter = 0
        instruction = BLTU(rs1=2, rs2=0, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 0, 1
        state.program_counter = 0
        instruction = BLTU(rs1=0, rs2=2, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1 - negative immediate
        state.program_counter = 32
        instruction = BLTU(rs1=0, rs2=2, imm=-6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

        # 0, (2^32 - 1)
        state.program_counter = 0
        instruction = BLTU(rs1=0, rs2=3, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # (2^32 - 1), 0
        state.program_counter = 0
        instruction = BLTU(rs1=3, rs2=0, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 2^31, (2^32 - 1)
        state.program_counter = 0
        instruction = BLTU(rs1=4, rs2=3, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

    def test_bgeu(self):
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(1),
                    fixedint.MutableUInt32(pow(2, 32) - 1),
                    fixedint.MutableUInt32(pow(2, 31)),
                ]
            )
        )

        # 0, 0
        state.program_counter = 0
        instruction = BGEU(rs1=0, rs2=1, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 0, 1
        state.program_counter = 0
        instruction = BGEU(rs1=0, rs2=2, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 1, 0
        state.program_counter = 0
        instruction = BGEU(rs1=2, rs2=0, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 8)

        # 1, 0 - negative immediate
        state.program_counter = 32
        instruction = BGEU(rs1=2, rs2=0, imm=-6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 16)

        # 0, (2^32 - 1)
        state.program_counter = 0
        instruction = BGEU(rs1=0, rs2=3, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

        # 2^31, (2^32 - 1)
        state.program_counter = 0
        instruction = BGEU(rs1=4, rs2=3, imm=6)
        state = instruction.behavior(state)
        self.assertEqual(state.program_counter, 0)

    def test_lb(self):
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[0, 1, -1, pow(2, 32) - 1]),
            memory=Memory(
                memory_file=dict(
                    [
                        (0, fixedint.MutableUInt8(1)),
                        (1, fixedint.MutableUInt8(2)),
                        (2, fixedint.MutableUInt8(3)),
                        (3, fixedint.MutableUInt8(-1)),
                        (pow(2, 32) - 1, fixedint.MutableUInt8(4)),
                        (2047, fixedint.MutableUInt8(5)),
                    ]
                )
            ),
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
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=10239, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [5, 1, -1, pow(2, 32) - 1])

        # imm=3, rs1=0 load negative value
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=3, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers,
            [fixedint.MutableUInt32(-1), 1, -1, pow(2, 32) - 1],
        )

        # try memory acces to non existant address
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=4, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [0, 1, -1, pow(2, 32) - 1])

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
                        (6, fixedint.MutableUInt8(-1)),
                        (7, fixedint.MutableUInt8(-1)),
                        (pow(2, 32) - 2, fixedint.MutableUInt8(7)),
                        (pow(2, 32) - 1, fixedint.MutableUInt8(8)),
                        (2047, fixedint.MutableUInt8(5)),
                    ]
                )
            ),
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
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LH(imm=10239, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [5, 1, -1, pow(2, 32) - 1])

        # imm=6, rs1=0 load negative value
        state.register_file.registers = [0, 2, -2, pow(2, 32) - 1]
        instr = LH(imm=6, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers,
            [fixedint.MutableUInt32(-1), 2, -2, pow(2, 32) - 1],
        )

        # try memory acces to non existant address
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=8, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [0, 1, -1, pow(2, 32) - 1])

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
                        (12, fixedint.MutableUInt8(-1)),
                        (13, fixedint.MutableUInt8(-1)),
                        (14, fixedint.MutableUInt8(-1)),
                        (15, fixedint.MutableUInt8(-1)),
                        (pow(2, 32) - 4, fixedint.MutableUInt8(4)),
                        (pow(2, 32) - 3, fixedint.MutableUInt8(4)),
                        (pow(2, 32) - 2, fixedint.MutableUInt8(4)),
                        (pow(2, 32) - 1, fixedint.MutableUInt8(4)),
                        (2047, fixedint.MutableUInt8(5)),
                    ]
                )
            ),
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
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LW(imm=10239, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [5, 1, -1, pow(2, 32) - 1])

        # imm=12, rs1=0 load negative value
        state.register_file.registers = [0, 4, -4, pow(2, 32) - 1]
        instr = LW(imm=12, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(
            state.register_file.registers,
            [fixedint.MutableUInt32(-1), 4, -4, pow(2, 32) - 1],
        )

        # try memory acces to non existant address
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LB(imm=16, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [0, 1, -1, pow(2, 32) - 1])

    def test_lbu(self):
        state = ArchitecturalState(
            register_file=RegisterFile(registers=[0, 1, -1, pow(2, 32) - 1]),
            memory=Memory(
                memory_file=dict(
                    [
                        (0, fixedint.MutableUInt8(1)),
                        (1, fixedint.MutableUInt8(2)),
                        (2, fixedint.MutableUInt8(3)),
                        (3, fixedint.MutableUInt8(-1)),
                        (pow(2, 32) - 1, fixedint.MutableUInt8(4)),
                        (2047, fixedint.MutableUInt8(5)),
                    ]
                )
            ),
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
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LBU(imm=10239, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [5, 1, -1, pow(2, 32) - 1])

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
                        (6, fixedint.MutableUInt8(-1)),
                        (7, fixedint.MutableUInt8(-1)),
                        (pow(2, 32) - 2, fixedint.MutableUInt8(7)),
                        (pow(2, 32) - 1, fixedint.MutableUInt8(8)),
                        (2047, fixedint.MutableUInt8(5)),
                    ]
                )
            ),
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
        state.register_file.registers = [0, 1, -1, pow(2, 32) - 1]
        instr = LHU(imm=10239, rs1=0, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [5, 1, -1, pow(2, 32) - 1])

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

    def test_srai(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 1, -128]))
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
        self.assertEqual(
            state.register_file.registers, [fixedint.MutableUInt32(-64), 1, -128]
        )

        # imm=95, rs1= 2^30 immediate is max 32
        state.register_file.registers = [0, 1, -128, pow(2, 30)]
        instr = SRAI(imm=95, rs1=3, rd=0)
        state = instr.behavior(state)
        self.assertEqual(state.register_file.registers, [0, 1, -128, pow(2, 30)])

    def test_jalr(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 8]))
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
        state = ArchitecturalState(register_file=RegisterFile(registers=()))
        # Raise ECALL Exception
        with self.assertRaises(ECALLException):
            instr = ECALL(imm=0, rs1=0, rd=0)
            state = instr.behavior(state)

    def test_ebreak(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=()))
        # Raise ECALL Exception
        with self.assertRaises(EBREAKException):
            instr = EBREAK(imm=0, rs1=0, rd=0)
            state = instr.behavior(state)

    def test_stype(self):
        try:
            SB(rs1=0, rs2=4, imm=-2048)
            SW(rs1=4, rs2=2, imm=2047)
        except Exception:
            print(Exception)
            self.fail("STypeInstruction raised an exception upon instantiation")

        with self.assertRaises(ValueError):
            SH(rs1=3, rs2=8, imm=-2049)
        with self.assertRaises(ValueError):
            SB(rs1=11, rs2=9, imm=2048)

    def test_sb(self):
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(261),
                    fixedint.MutableUInt32(257),
                    fixedint.MutableUInt32(256),
                    fixedint.MutableUInt32(128),
                    fixedint.MutableUInt32(1024),
                ]
            )
        )

        sb_0 = SB(rs1=0, rs2=0, imm=0)
        state = sb_0.behavior(state)
        self.assertEqual(state.memory.load_byte(0), 0)

        sb_1 = SB(rs1=0, rs2=2, imm=1)
        state = sb_1.behavior(state)
        self.assertEqual(state.memory.load_byte(1), 1)

        sb_2 = SB(rs1=0, rs2=1, imm=1)
        state = sb_2.behavior(state)
        self.assertEqual(state.memory.load_byte(1), 5)

        sb_3 = SB(rs1=0, rs2=3, imm=0)
        state = sb_3.behavior(state)
        self.assertEqual(state.memory.load_byte(0), 0)

        sb_4 = SB(rs1=0, rs2=3, imm=1)
        state = sb_4.behavior(state)
        self.assertEqual(state.memory.load_byte(1), 0)

        sb_5 = SB(rs1=0, rs2=4, imm=2)
        state = sb_5.behavior(state)
        self.assertEqual(state.memory.load_byte(2), 128)

        sb_6 = SB(rs1=0, rs2=5, imm=2)
        state = sb_6.behavior(state)
        self.assertEqual(state.memory.load_byte(2), 0)

    def test_sh(self):
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(65536),
                    fixedint.MutableUInt32(65537),
                    fixedint.MutableUInt32(65538),
                    fixedint.MutableUInt32(3),
                    fixedint.MutableUInt32(2),
                    fixedint.MutableUInt32(255),
                    fixedint.MutableUInt32(256),
                    fixedint.MutableUInt32(65535),
                ]
            )
        )

        sh_0 = SH(rs1=0, rs2=0, imm=0)
        state = sh_0.behavior(state)
        self.assertEqual(int(state.memory.load_halfword(0)), 0)

        sh_1 = SH(rs1=0, rs2=1, imm=0)
        state = sh_1.behavior(state)
        self.assertEqual(int(state.memory.load_halfword(0)), 0)

        sh_2 = SH(rs1=0, rs2=2, imm=1)
        state = sh_2.behavior(state)
        self.assertEqual(int(state.memory.load_halfword(1)), 1)

        sh_3 = SH(rs1=0, rs2=3, imm=2)
        state = sh_3.behavior(state)
        self.assertEqual(int(state.memory.load_halfword(2)), 2)

        sh_4 = SH(rs1=0, rs2=4, imm=3)
        state = sh_4.behavior(state)
        self.assertEqual(int(state.memory.load_halfword(3)), 3)

        sh_5 = SH(rs1=0, rs2=6, imm=3)
        state = sh_5.behavior(state)
        self.assertEqual(int(state.memory.load_halfword(3)), 255)

        sh_6 = SH(rs1=0, rs2=7, imm=3)
        state = sh_6.behavior(state)
        self.assertEqual(int(state.memory.load_halfword(3)), 256)

        sh_7 = SH(rs1=0, rs2=8, imm=6)
        state = sh_7.behavior(state)
        self.assertEqual(int(state.memory.load_halfword(6)), 65535)

    def test_sw(self):
        state = ArchitecturalState(
            register_file=RegisterFile(
                registers=[
                    fixedint.MutableUInt32(0),
                    fixedint.MutableUInt32(1),
                    fixedint.MutableUInt32(2),
                    fixedint.MutableUInt32(100),
                    fixedint.MutableUInt32(10),
                    fixedint.MutableUInt32(255),
                    fixedint.MutableUInt32(256),
                    fixedint.MutableUInt32(4294967295),
                ]
            )
        )

        sw_0 = SW(rs1=0, rs2=0, imm=0)
        state = sw_0.behavior(state)
        self.assertEqual(int(state.memory.load_word(0)), 0)

        sw_1 = SW(rs1=0, rs2=1, imm=1)
        state = sw_1.behavior(state)
        self.assertEqual(int(state.memory.load_word(1)), 1)

        sw_2 = SW(rs1=0, rs2=2, imm=2)
        state = sw_2.behavior(state)
        self.assertEqual(int(state.memory.load_word(2)), 2)

        sw_3 = SW(rs1=0, rs2=3, imm=3)
        state = sw_3.behavior(state)
        self.assertEqual(int(state.memory.load_word(3)), 100)

        sw_4 = SW(rs1=0, rs2=4, imm=0)
        state = sw_4.behavior(state)
        self.assertEqual(int(state.memory.load_word(0)), 10)

        sw_5 = SW(rs1=0, rs2=5, imm=0)
        state = sw_5.behavior(state)
        self.assertEqual(int(state.memory.load_word(0)), 255)

        sw_6 = SW(rs1=0, rs2=6, imm=0)
        state = sw_6.behavior(state)
        self.assertEqual(int(state.memory.load_word(0)), 256)

        sw_7 = SW(rs1=0, rs2=7, imm=8)
        state = sw_7.behavior(state)
        self.assertEqual(int(state.memory.load_word(8)), 4294967295)

    def test_utype(self):
        try:
            LUI(rd=0, imm=524287)
            AUIPC(rd=1, imm=-524288)
        except Exception:
            print(Exception)
            self.fail("UTypeInstruction raised an exception upon instantiation")

        with self.assertRaises(ValueError):
            LUI(rd=10, imm=524288)
            AUIPC(rd=9, imm=-524289)

    def test_lui(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 1, 2, 3]))

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

    def test_auipc(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 1, 2, 3]))

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

    def test_jtype(self):
        try:
            JAL(rd=3, imm=524287)
            JAL(rd=3, imm=-524288)
        except Exception:
            print(Exception)
            self.fail("JTypeInstruction raised an exception upon instantiation")

        with self.assertRaises(ValueError):
            JAL(rd=11, imm=524288)
        with self.assertRaises(ValueError):
            JAL(rd=1, imm=-524289)

    def test_jal(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[1, 1, 1]))
        state.program_counter = 0
        jal_1 = JAL(rd=0, imm=2)
        state = jal_1.behavior(state)
        self.assertEqual(state.program_counter, 0)
        self.assertEqual(int(state.register_file.registers[0]), 4)

        state.program_counter = 1
        jal_2 = JAL(rd=0, imm=3)
        state = jal_2.behavior(state)
        self.assertEqual(state.program_counter, 3)
        self.assertEqual(int(state.register_file.registers[0]), 5)

        state.program_counter = 2
        jal_3 = JAL(rd=0, imm=4)
        state = jal_3.behavior(state)
        self.assertEqual(state.program_counter, 6)
        self.assertEqual(int(state.register_file.registers[0]), 6)

        state.program_counter = 3
        jal_4 = JAL(rd=1, imm=4)
        state = jal_4.behavior(state)
        self.assertEqual(state.program_counter, 7)
        self.assertEqual(int(state.register_file.registers[1]), 7)

        state.program_counter = 7
        jal_5 = JAL(rd=1, imm=5)
        state = jal_5.behavior(state)
        self.assertEqual(state.program_counter, 13)
        self.assertEqual(int(state.register_file.registers[1]), 11)

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
