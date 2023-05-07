import unittest

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
    CSRRW,
    CSRRS,
    CSRRC,
    CSRRWI,
    CSRRSI,
    CSRRCI,
    SLL,
    SLT,
    SLTU,
    XOR,
    SRL,
    SRA,
    OR,
    AND
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

        num_a = fixedint.MutableUInt32(4294902015)  # FF FF 00 FF
        num_b = fixedint.MutableUInt32(4294905615)  # FF FF 0F 0F
        num_c = fixedint.MutableUInt32(4080)  # 00 00 0F F0

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
        # Number defintions
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

    def test_csrrw_privilege_level_too_low(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 2]))
        state.csr_registers.privilege_level = 0
        with self.assertRaises(Exception) as context:
            state.csr_registers.store_word(3000, fixedint.MutableUInt32(3))
        self.assertTrue("illegal action: privilege level too low to access this csr register" in str(context.exception))

    def test_csrrw_attempting_to_write_to_read_only(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 2]))
        with self.assertRaises(Exception) as context:
            state.csr_registers.store_word(3072, fixedint.MutableUInt32(3))
        self.assertTrue("illegal action: attempting to write into read-only csr register" in str(context.exception))

    def test_csrrw_invalid_adress(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 2]))
        state.csr_registers.privilege_level = 4
        with self.assertRaises(Exception) as context:
            state.csr_registers.store_word(7000, fixedint.MutableUInt32(3))
        self.assertTrue("illegal action: csr register does not exist" in str(context.exception))

    def test_csrrw(self):
        register_value_1 = fixedint.MutableUInt32(0)
        register_value_2 = fixedint.MutableUInt32(1)
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 2]))
        cssrw_1 = CSRRW(csr = 0, rs1 = 1, rd = 0)
        state.csr_registers.store_word(0, fixedint.MutableUInt32(3))
        state.csr_registers.privilege_level = 4
        state = cssrw_1.behavior(state)
        self.assertEqual(state.register_file.registers, [3, 2])
        self.assertEqual(state.csr_registers.load_word(cssrw_1.csr), 2)

    def test_csrrs(self):
        max_number = fixedint.MutableUInt32(4294967295) #FF FF FF FF
        test_number_1 = fixedint.MutableUInt32(4294967294) #FF FF FF FE
        test_mask_1 = fixedint.MutableUInt32(1) # 00 00 00 01
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, test_mask_1]))
        state.csr_registers.store_word(0, test_number_1)
        cssrs_1 = CSRRS(csr = 0, rs1 = 1, rd = 0)
        state = cssrs_1.behavior(state)
        self.assertEqual(state.register_file.registers, [test_number_1, test_mask_1])
        self.assertEqual(state.csr_registers.load_word(cssrs_1.csr), max_number)

    def test_csrrc(self):
        max_number = fixedint.MutableUInt32(4294967295) #FF FF FF FF
        test_result_1 = fixedint.MutableUInt32(1) # 00 00 00 01
        test_mask_1 = fixedint.MutableUInt32(4294967294) #FF FF FF FE
        state = ArchitecturalState(register_file=RegisterFile(registers=[0, test_mask_1]))
        state.csr_registers.store_word(0, max_number)
        cssrc_1 = CSRRC(csr = 0, rs1 = 1, rd = 0)
        state = cssrc_1.behavior(state)
        self.assertEqual(state.register_file.registers, [max_number, test_mask_1])
        self.assertEqual(state.csr_registers.load_word(cssrc_1.csr), test_result_1)

    def test_csrrwi(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=[0]))
        state.csr_registers.store_word(0, 3)
        cssrwi_1 = CSRRWI(csr = 0, uimm = 4, rd = 0)
        state = cssrwi_1.behavior(state)
        self.assertEqual(state.register_file.registers, [3])
        self.assertEqual(state.csr_registers.load_word(cssrwi_1.csr), 4)

    def test_csrrsi(self):
        max_number = fixedint.MutableUInt32(4294967295) #FF FF FF FF
        test_number_1 = fixedint.MutableUInt32(4294967294) #FF FF FF FE
        test_mask_1 = fixedint.MutableUInt32(1) # 00 00 00 01
        state = ArchitecturalState(register_file=RegisterFile(registers=[0]))
        cssrsi_1 = CSRRSI(csr = 0, uimm = test_mask_1, rd = 0)
        state.csr_registers.store_word(0, test_number_1)
        state = cssrsi_1.behavior(state)
        self.assertEqual(state.register_file.registers, [test_number_1])
        self.assertEqual(state.csr_registers.load_word(cssrsi_1.csr), max_number)

    def test_csrrci(self):
        max_number = fixedint.MutableUInt32(4294967295) #FF FF FF FF
        test_result_1 = fixedint.MutableUInt32(1) # 00 00 00 01
        test_mask_1 = fixedint.MutableUInt32(4294967294) #FF FF FF FE
        state = ArchitecturalState(register_file=RegisterFile(registers=[0]))
        state.csr_registers.store_word(0, max_number)
        cssrci_1 = CSRRCI(csr = 0, uimm = test_mask_1, rd = 0)
        state = cssrci_1.behavior(state)
        self.assertEqual(state.register_file.registers, [max_number])
        self.assertEqual(state.csr_registers.load_word(cssrci_1.csr), test_result_1)

    def test_mem(self):
        state = ArchitecturalState(register_file=RegisterFile(registers=()))
        # store_byte test
        state.memory.store_byte(0, fixedint.MutableUInt8(1))
        self.assertEqual(state.memory.load_byte(0), fixedint.MutableUInt8(1))

        # store_byte type test
        state.memory.store_byte(0, fixedint.MutableUInt8(1))
        self.assertIsInstance(state.memory.load_byte(0), fixedint.MutableUInt8)

        # store_halfword test
        state.memory.store_halfword(0, fixedint.MutableUInt16(1))
        self.assertEqual(state.memory.load_halfword(0), fixedint.MutableUInt16(1))

        # store_halfword type test
        state.memory.store_halfword(0, fixedint.MutableUInt16(1))
        self.assertIsInstance(state.memory.load_halfword(0), fixedint.MutableUInt16)

        # store_word test
        state.memory.store_word(0, fixedint.MutableUInt32(1))
        self.assertEqual(state.memory.load_word(0), fixedint.MutableUInt32(1))

        # store_word type test
        state.memory.store_word(0, fixedint.MutableUInt32(1))
        self.assertIsInstance(state.memory.load_word(0), fixedint.MutableUInt32)

        # store_byte negative value test
        state.memory.store_byte(0, fixedint.MutableUInt8(-1))
        self.assertEqual(state.memory.load_byte(0), fixedint.MutableUInt8(-1))

        # store_halfword negative value test
        state.memory.store_halfword(0, fixedint.MutableUInt16(-1))
        self.assertEqual(state.memory.load_halfword(0), fixedint.MutableUInt16(-1))

        # store_word test
        state.memory.store_word(0, fixedint.MutableUInt32(-1))
        self.assertEqual(state.memory.load_word(0), fixedint.MutableUInt32(-1))



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
