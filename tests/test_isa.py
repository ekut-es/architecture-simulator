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

import fixedint


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
