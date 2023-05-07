import unittest
import fixedint

from architecture_simulator.uarch.architectural_state import RegisterFile, Memory
from architecture_simulator.isa.rv32i_instructions import (
    ADD,
    SUB,
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
