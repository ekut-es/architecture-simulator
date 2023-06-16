import unittest
import pyparsing as pp
from architecture_simulator.simulation.simulation import Simulation
from architecture_simulator.uarch.architectural_state import (
    RegisterFile,
    Memory,
    InstructionMemory,
)
from architecture_simulator.isa.rv32i_instructions import (
    ADD,
    BEQ,
    BNE,
    CSRRW,
    CSRRWI,
    SB,
    LUI,
    JAL,
    LB,
    ECALL,
    EBREAK,
    ADDI,
    FENCE,
)
from architecture_simulator.uarch.architectural_state import ArchitecturalState

from architecture_simulator.isa.parser import RiscvParser


class TestParser(unittest.TestCase):
    program = """

Ananas:#dfsdfsdf
add x0,x1,x2
addi x0, x1, -20
#aaaaa
Banane:
##asdsadad
_Banune24_de:
lb x0, 7(x1)
sb x1, 666(x2)
BEQ x4, x5, 42
lui x12, 8000
Chinakohl:
jal x20, 220
bne x3, x10, Banane
jal x10, Ananas+0x24
ecall
ebreak
fence x10, x12
csrrw x2, 0x448, x9
csrrwi x2, 0x448, 20
beq x0, x1, Ban0n3
Ban0n3:
beq x0, x1, Ban0n3


"""

    program_2 = "8asfsdfs:"
    program_3 = "add x5, x6, x6, x8"
    program_4 = "addidas x5, x6, 666"

    program_5_abi = """
Ananas:#dfsdfsdf
add zero, ra, sp
addi zero, ra, -20
#aaaaa
Banane:
##asdsadad
_Banune24_de:
lb zero, 7(ra)
sb ra, 666(sp)
BEQ tp, t0, 42
lui a2, 8000
Chinakohl:
jal s4, 220
bne gp, a0, Banane
jal a0, Ananas+0x24
ecall
ebreak
fence a0, a2
csrrw sp, 0x448, s1
csrrwi sp, 0x448, 20
beq zero, ra, Ban0n3
Ban0n3:
beq zero, ra, Ban0n3
"""

    expected = [
        "Ananas",
        ["add", ["x", "0"], ["x", "1"], ["x", "2"]],
        ["addi", ["x", "0"], ["x", "1"], "-20"],
        "Banane",
        "_Banune24_de",
        ["lb", ["x", "0"], "7", ["x", "1"]],
        ["sb", ["x", "1"], "666", ["x", "2"]],
        ["BEQ", ["x", "4"], ["x", "5"], "42"],
        ["lui", ["x", "12"], "8000"],
        "Chinakohl",
        ["jal", ["x", "20"], "220"],
        ["bne", ["x", "3"], ["x", "10"], "Banane"],
        ["jal", ["x", "10"], "Ananas", "0x24"],
        "ecall",
        "ebreak",
        ["fence", ["x", "10"], ["x", "12"]],
        ["csrrw", ["x", "2"], "0x448", ["x", "9"]],
        ["csrrwi", ["x", "2"], "0x448", "20"],
        ["beq", ["x", "0"], ["x", "1"], "Ban0n3"],
        "Ban0n3",
        ["beq", ["x", "0"], ["x", "1"], "Ban0n3"],
    ]

    def test_bnf(self):
        parser = RiscvParser()
        instr = parser.parse_assembly(self.program)
        self.assertEqual(
            [result if type(result) == str else result.as_list() for result in instr],
            self.expected,
        )
        self.assertNotEqual(instr[1].mnemonic, "")
        # self.assertEqual(instr[1].mnemonic, "")

        with self.assertRaises(pp.exceptions.ParseException):
            parser.parse_assembly(self.program_2)

        with self.assertRaises(pp.exceptions.ParseException):
            parser.parse_assembly(self.program_3)

        # just check that there is no parser exception
        parser.parse_assembly(self.program_4)

    def test_process_labels(self):
        parser = RiscvParser()
        expected_labels = {
            "Ananas": 0,
            "Banane": 8,
            "_Banune24_de": 8,
            "Chinakohl": 24,
            "Ban0n3": 60,
        }
        bnf_result = parser.parse_assembly(self.program)
        proc_labels = parser.compute_labels(bnf_result, 0)
        self.assertEqual(proc_labels, expected_labels)

    def assert_inst_values(self, instr):
        # add x0,x1,x2
        self.assertIsInstance(instr[0], ADD)
        self.assertEqual(instr[0].rd, 0)
        self.assertEqual(instr[0].rs1, 1)
        self.assertEqual(instr[0].rs2, 2)
        # addi x0, x1, -20
        self.assertIsInstance(instr[1], ADDI)
        self.assertEqual(instr[1].rd, 0)
        self.assertEqual(instr[1].rs1, 1)
        self.assertEqual(instr[1].imm, -20)
        # lb x0, 7(x1)
        self.assertIsInstance(instr[2], LB)
        self.assertEqual(instr[2].rd, 0)
        self.assertEqual(instr[2].rs1, 1)
        self.assertEqual(instr[2].imm, 7)

        # sb x1, 666(x2)
        self.assertIsInstance(instr[3], SB)
        self.assertEqual(instr[3].rs1, 2)
        self.assertEqual(instr[3].rs2, 1)
        self.assertEqual(instr[3].imm, 666)

        # BEQ x4, x5, 42
        self.assertIsInstance(instr[4], BEQ)
        self.assertEqual(instr[4].rs1, 4)
        self.assertEqual(instr[4].rs2, 5)
        self.assertEqual(instr[4].imm, 21)

        # lui x12, 8000
        self.assertIsInstance(instr[5], LUI)
        self.assertEqual(instr[5].rd, 12)
        self.assertEqual(instr[5].imm, 8000)

        # jal x20, 220
        self.assertIsInstance(instr[6], JAL)
        self.assertEqual(instr[6].rd, 20)
        self.assertEqual(instr[6].imm, 110)

        # bne x3, x10, Banane
        self.assertIsInstance(instr[7], BNE)
        self.assertEqual(instr[7].rs1, 3)
        self.assertEqual(instr[7].rs2, 10)
        self.assertEqual(instr[7].imm, -10)

        # jal x10, Ananas
        self.assertIsInstance(instr[8], JAL)
        self.assertEqual(instr[8].rd, 10)
        self.assertEqual(instr[8].imm, 2)

        # ecall
        self.assertIsInstance(instr[9], ECALL)

        # ebreak
        self.assertIsInstance(instr[10], EBREAK)

        # fence
        self.assertIsInstance(instr[11], FENCE)
        # TODO: currently not implemented
        # self.assertEqual(instr[11].rd, 10)
        # self.assertEqual(instr[11].rs1, 12)

        # csrrw x2, 0x448, x9
        self.assertIsInstance(instr[12], CSRRW)
        self.assertEqual(instr[12].rd, 2)
        self.assertEqual(instr[12].csr, 0x448)
        self.assertEqual(instr[12].rs1, 9)

        # csrrwi x2, 0x448, 20
        self.assertIsInstance(instr[13], CSRRWI)
        self.assertEqual(instr[13].rd, 2)
        self.assertEqual(instr[13].csr, 0x448)
        self.assertEqual(instr[13].uimm, 20)

        # beq x0, x1, Ban0n3
        self.assertIsInstance(instr[14], BEQ)
        self.assertEqual(instr[14].rs1, 0)
        self.assertEqual(instr[14].rs2, 1)
        self.assertEqual(instr[14].imm, 2)

        # beq x0, x1, Ban0n3
        self.assertIsInstance(instr[15], BEQ)
        self.assertEqual(instr[15].rs1, 0)
        self.assertEqual(instr[15].rs2, 1)
        self.assertEqual(instr[15].imm, 0)

    def test_parser(self):
        parser = RiscvParser()
        instr = parser.parse_res_to_instructions(
            parser.parse_assembly(self.program), start_address=0
        )
        self.assert_inst_values(instr)

        with self.assertRaises(KeyError):
            parser.parse_res_to_instructions(
                parser.parse_assembly(self.program_4), start_address=0
            )

        parser = RiscvParser()
        instr = parser.parse_res_to_instructions(
            parser.parse_assembly(self.program_5_abi), start_address=0
        )

        self.assert_inst_values(instr)

    fibonacci = """lui x10, 0
    addi x10, x10, 10
    addi x2, x0, 1024
    jal x1, Fib
    beq x0, x0, End
    Fib:
    bge x0, x10, BaseA
    addi x5, x0, 1
    beq x5, x10, BaseB
    addi x2, x2, -8
    sw x1, 4(x2)
    sw x10, 0(x2) # store n
    addi x10, x10, -1 # x10 = n - 1
    jal x1, Fib # goto 5 (beginning)
    lw x5, 0(x2) # restore argument
    sw x10, 0(x2) # store return value (fib(n-1))
    addi x10, x5, -2 # x10 = n - 2
    jal x1, Fib # goto 5 (beginning)
    lw x5, 0(x2) # x5 = fib(n-1)
    lw x1, 4(x2) # restore ra
    addi x2, x2, 8 # return sp to original size
    add x10, x10, x5 # x10 = fib(n-2) + fib(n-1)
    jalr x7, x1, 0
    BaseA:
    and x10, x10, x0 # <- n <= 0
    jalr x7, x1, 0
    BaseB:
    addi x10, x0, 1 # <- n == 1
    jalr x7, x1, 0
    End:
    and x0, x0, x0 # end
    """

    def test_fibonacci_parser(self):
        simulation = Simulation(state=ArchitecturalState(memory=Memory(min_bytes=0)))
        simulation.state.instruction_memory.append_instructions(self.fibonacci)
        # print(simulation.instructions)
        while simulation.state.program_counter < 104:
            simulation.step_simulation()
        self.assertEqual(int(simulation.state.register_file.registers[10]), 55)

    fibonacci_c = """main:
	addi	x2,x2,-16
	sw	x1,12(x2)
	sw	x8,8(x2)
	addi	x8,x2,16
	addi	x10,x0,10
	jal	x1,fibonacci
	addi	x15,x0,0
	addi	x10,x15,0
	lw	x1,12(x2)
	lw	x8,8(x2)
	addi	x2,x2,16
	jalr	x0,0(x1)
fibonacci:
	addi	x2,x2,-32
	sw	x1,28(x2)
	sw	x8,24(x2)
	sw	x9,20(x2)
	addi	x8,x2,32
	sw	x10,-20(x8)
	lw	x14,-20(x8)
	addi	x15,x0,1
	blt	x15,x14,fibonacci+0x2c
	lw	x15,-20(x8)
	jal	x0,fibonacci+0x58
	lw	x15,-20(x8)
	addi	x15,x15,-1
	addi	x10,x15,0
	jal	x1,fibonacci
	addi	x9,x10,0
	lw	x15,-20(x8)
	addi	x15,x15,-2
	addi	x10,x15,0
	jal	x1,fibonacci
	addi	x15,x10,0
	add	x15,x9,x15
	addi	x10,x15,0
	lw	x1,28(x2)
	lw	x8,24(x2)
	lw	x9,20(x2)
	addi	x2,x2,32
	jalr	x0,0(x1)

"""

    def test_c_fibonacci(self):
        simulation = Simulation()
        simulation.state.instruction_memory.append_instructions(self.fibonacci_c)
        # print(simulation.instructions)
        while simulation.state.program_counter != 24:
            simulation.step_simulation()
            simulation.state.register_file.registers[0] = 0
        self.assertEqual(int(simulation.state.register_file.registers[15]), 55)

    add_c = """main:
	addi	x2,x2,-32
	sw	x8,28(x2)
	addi	x8,x2,32
	addi	x15,x0,42
	sw	x15,-20(x8)
	addi	x15,x0,23
	sw	x15,-24(x8)
	lw	x14,-20(x8)
	lw	x15,-24(x8)
	add	x15,x14,x15
	sw	x15,-28(x8)
	addi	x15,x0,0
	addi	x10,x15,0
	lw	x8,28(x2)
	addi	x2,x2,32
	jalr	x0,0(x1)
    """

    def test_c_add(self):
        simulation = Simulation()
        simulation.state.instruction_memory.append_instructions(self.add_c)
        # print(simulation.instructions)
        while simulation.state.program_counter < 60:
            simulation.step_simulation()
            simulation.state.register_file.registers[0] = 0
        self.assertEqual(int(simulation.state.memory.load_word(4294967268)), 65)

    fibonacci_c_abi = """main:
	addi	sp,sp,-16
	sw	ra,12(sp)
	sw	s0,8(sp)
	addi	s0,sp,16
	addi	a0,zero,10
	jal	ra,fibonacci
	addi	a5,zero,0
	addi	a0,a5,0
	lw	ra,12(sp)
	lw	s0,8(sp)
	addi	sp,sp,16
	jalr	zero,0(ra)
fibonacci:
	addi	sp,sp,-32
	sw	ra,28(sp)
	sw	s0,24(sp)
	sw	s1,20(sp)
	addi	s0,sp,32
	sw	a0,-20(s0)
	lw	a4,-20(s0)
	addi	a5,zero,1
	blt	a5,a4,fibonacci+0x2c
	lw	a5,-20(s0)
	jal	zero,fibonacci+0x58
	lw	a5,-20(s0)
	addi	a5,a5,-1
	addi	a0,a5,0
	jal	ra,fibonacci
	addi	s1,a0,0
	lw	a5,-20(s0)
	addi	a5,a5,-2
	addi	a0,a5,0
	jal	ra,fibonacci
	addi	a5,a0,0
	add	a5,s1,a5
	addi	a0,a5,0
	lw	ra,28(sp)
	lw	s0,24(sp)
	lw	s1,20(sp)
	addi	sp,sp,32
	jalr	zero,0(ra)
"""

    def test_c_fibonacci_abi(self):
        simulation = Simulation()
        simulation.state.instruction_memory.append_instructions(self.fibonacci_c_abi)
        # print(simulation.instructions)
        while simulation.state.program_counter != 24:
            simulation.step_simulation()
            simulation.state.register_file.registers[0] = 0
        self.assertEqual(int(simulation.state.register_file.registers[15]), 55)

    def test_neg_imm_where_lables_are_accepted(self):
        # This test ensures, that the fix for negative imm values where labels can be used works
        text = """main:
        beq x0, x1, -4
        blt x1, x2, main
        bge x3, x4, 8
        jal x7, -12
        jal zero, 8
        jal zero, main
        """
        parser = RiscvParser()
        instr = parser.parse_res_to_instructions(
            parser.parse_assembly(text), start_address=0
        )
        self.assertEqual(instr[0].imm, -2)
        self.assertEqual(instr[1].imm, -2)
        self.assertEqual(instr[2].imm, 4)
        self.assertEqual(instr[3].imm, -6)
        self.assertEqual(instr[4].imm, 4)
        self.assertEqual(instr[5].imm, -10)

    def test_hex_imm(self):
        text = """
        addi x0, x0, 0x0FF
        andi x0, x1, -0x000F
        slli x3, t3, 0x0A
        sb x2, 0x00011(x3)
        beq x0, zero, -0x0AC
        lui x0, -0xAF
        jal x0, 0x3a
        csrrw sp, 0x448, s1
        csrrwi sp, 0x448, 0x20"""
        parser = RiscvParser()
        instr = parser.parse_res_to_instructions(
            parser.parse_assembly(text), start_address=0
        )

        self.assertEqual(instr[0].imm, 0xFF)
        self.assertEqual(instr[1].imm, -15)
        self.assertEqual(instr[2].imm, 0xA)
        self.assertEqual(instr[3].imm, 0x11)
        self.assertEqual(instr[4].imm, -0xAC // 2)
        self.assertEqual(instr[5].imm, -0xAF)
        self.assertEqual(instr[6].imm, 0x3A // 2)
        self.assertEqual(instr[7].csr, 0x448)
        self.assertEqual(instr[8].csr, 0x448)
        self.assertEqual(instr[8].uimm, 0x20)

    def test_bin_imm(self):
        text = """
        addi x0, x0, 0b0011111111
        andi x0, x1, -0b01111
        slli x3, t3, 0b0001010
        sb x2, 0b10001(x3)
        beq x0, zero, -0b10101100
        lui x0, -0b10101111
        jal x0, 0b0000111010
        csrrw sp, 0b010001001000, s1
        csrrwi sp, 0b010001001000, 0b100000"""
        parser = RiscvParser()
        instr = parser.parse_res_to_instructions(
            parser.parse_assembly(text), start_address=0
        )
        self.assertEqual(instr[0].imm, 0xFF)
        self.assertEqual(instr[1].imm, -15)
        self.assertEqual(instr[2].imm, 0xA)
        self.assertEqual(instr[3].imm, 0x11)
        self.assertEqual(instr[4].imm, -0xAC // 2)
        self.assertEqual(instr[5].imm, -0xAF)
        self.assertEqual(instr[6].imm, 0x3A // 2)
        self.assertEqual(instr[7].csr, 0x448)
        self.assertEqual(instr[8].csr, 0x448)
        self.assertEqual(instr[8].uimm, 0x20)

    def test_reg_label_names(self):
        parser = RiscvParser()
        program = """t0Test:
        sp3:
        beq x0, x1, t0Test
        add x0, x1, x2
        jal x2, sp3
        """

        parsed = parser.parse_assembly(program)
        self.assertEqual(
            [result if type(result) == str else result.as_list() for result in parsed],
            [
                "t0Test",
                "sp3",
                ["beq", ["x", "0"], ["x", "1"], "t0Test"],
                ["add", ["x", "0"], ["x", "1"], ["x", "2"]],
                ["jal", ["x", "2"], "sp3"],
            ],
        )
