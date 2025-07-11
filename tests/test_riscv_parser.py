import unittest
import fixedint
from architecture_simulator.isa.riscv.rv32i_instructions import (
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
    LW,
)
from architecture_simulator.uarch.riscv.riscv_architectural_state import (
    RiscvArchitecturalState,
)
from architecture_simulator.simulation.riscv_simulation import RiscvSimulation
from architecture_simulator.uarch.memory.memory import Memory, AddressingType
from architecture_simulator.isa.riscv.riscv_parser import RiscvParser
from architecture_simulator.isa.parser_exceptions import (
    ParserLabelException,
    ParserOddImmediateException,
    ParserSyntaxException,
    ParserDirectiveException,
    ParserDataSyntaxException,
    ParserDataDuplicateException,
    ParserVariableException,
)


class TestRiscvParser(unittest.TestCase):
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
        ["beq", ["x", "4"], ["x", "5"], "42"],
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
        state = RiscvArchitecturalState()
        parser.state = state
        parser.start_address = 0
        parser.program = self.program
        parser._sanitize()
        parser._tokenize()
        instr = [
            instr
            for line_num, line, instr in [
                (n, l, p[0]) for (n, l, p) in parser.token_list
            ]
        ]
        self.assertEqual(
            [result if type(result) == str else result.as_list() for result in instr],
            self.expected,
        )
        self.assertNotEqual(instr[1].mnemonic, "")
        # self.assertEqual(instr[1].mnemonic, "")

        with self.assertRaises(ParserSyntaxException):
            parser.parse(self.program_2, state)

        with self.assertRaises(ParserSyntaxException):
            parser.parse(self.program_3, state)

        with self.assertRaises(ParserSyntaxException):
            parser.parse(self.program_4, state)

    def test_process_labels(self):
        expected_labels = {
            "Ananas": 0,
            "Banane": 8,
            "_Banune24_de": 8,
            "Chinakohl": 24,
            "Ban0n3": 60,
        }
        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(self.program, state)

        self.assertEqual(parser.labels, expected_labels)

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
        self.assertEqual(instr[4].imm, 42)

        # lui x12, 8000
        self.assertIsInstance(instr[5], LUI)
        self.assertEqual(instr[5].rd, 12)
        self.assertEqual(instr[5].imm, 8000)

        # jal x20, 220
        self.assertIsInstance(instr[6], JAL)
        self.assertEqual(instr[6].rd, 20)
        self.assertEqual(instr[6].imm, 220)
        # self.assertEqual(instr[6].abs_addr, 220)

        # bne x3, x10, Banane
        self.assertIsInstance(instr[7], BNE)
        self.assertEqual(instr[7].rs1, 3)
        self.assertEqual(instr[7].rs2, 10)
        self.assertEqual(instr[7].imm, -20)

        # jal x10, Ananas
        self.assertIsInstance(instr[8], JAL)
        self.assertEqual(instr[8].rd, 10)
        self.assertEqual(instr[8].imm, 4)

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
        self.assertEqual(instr[14].imm, 4)

        # beq x0, x1, Ban0n3
        self.assertIsInstance(instr[15], BEQ)
        self.assertEqual(instr[15].rs1, 0)
        self.assertEqual(instr[15].rs2, 1)
        self.assertEqual(instr[15].imm, 0)

    def test_parser(self):
        parser = RiscvParser()
        state = RiscvArchitecturalState()

        parser.parse(self.program, state)
        instr = list(state.instruction_memory.instructions.values())

        self.assert_inst_values(instr)

        parser = RiscvParser()
        with self.assertRaises(ParserSyntaxException):
            parser.parse(self.program_4, state)

        parser = RiscvParser()
        parser.parse(self.program_5_abi, state)

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
        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(memory=Memory(AddressingType.BYTE, 32))
        )
        simulation.load_program(self.fibonacci)
        # print(simulation.instructions)
        while simulation.state.program_counter < 104:
            simulation.step()
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
        simulation = RiscvSimulation()
        simulation.load_program(self.fibonacci_c)
        # print(simulation.instructions)
        while simulation.state.program_counter != 24:
            simulation.step()
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
        simulation = RiscvSimulation()
        simulation.load_program(self.add_c)
        # print(simulation.instructions)
        while simulation.state.program_counter < 60:
            simulation.step()
            simulation.state.register_file.registers[0] = 0
        self.assertEqual(int(simulation.state.memory.read_word(4294967268)), 65)

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
        simulation = RiscvSimulation()
        simulation.load_program(self.fibonacci_c_abi)
        # print(simulation.instructions)
        while simulation.state.program_counter != 24:
            simulation.step()
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
        state = RiscvArchitecturalState()
        parser.parse(text, state)
        instr = list(state.instruction_memory.instructions.values())

        self.assertEqual(instr[0].imm, -4)
        self.assertEqual(instr[1].imm, -4)
        self.assertEqual(instr[2].imm, 8)
        self.assertEqual(instr[3].imm, -12)
        self.assertEqual(instr[4].imm, 8)
        self.assertEqual(instr[5].imm, -20)

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
        csrrwi sp, 0x448, 0x1F"""
        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(text, state)
        instr = list(state.instruction_memory.instructions.values())

        self.assertEqual(instr[0].imm, 0xFF)
        self.assertEqual(instr[1].imm, -15)
        self.assertEqual(instr[2].imm, 0xA)
        self.assertEqual(instr[3].imm, 0x11)
        self.assertEqual(instr[4].imm, -0xAC)
        self.assertEqual(instr[5].imm, -0xAF)
        self.assertEqual(instr[6].imm, 0x3A)
        self.assertEqual(instr[7].csr, 0x448)
        self.assertEqual(instr[8].csr, 0x448)
        self.assertEqual(instr[8].uimm, 0x1F)

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
        csrrwi sp, 0b010001001000, 0b11111"""
        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(text, state)
        instr = list(state.instruction_memory.instructions.values())

        self.assertEqual(instr[0].imm, 0xFF)
        self.assertEqual(instr[1].imm, -15)
        self.assertEqual(instr[2].imm, 0xA)
        self.assertEqual(instr[3].imm, 0x11)
        self.assertEqual(instr[4].imm, -0xAC)
        self.assertEqual(instr[5].imm, -0xAF)
        self.assertEqual(instr[6].imm, 0b0000111010)
        self.assertEqual(instr[7].csr, 0x448)
        self.assertEqual(instr[8].csr, 0x448)
        self.assertEqual(instr[8].uimm, 0x1F)

    def test_reg_label_names(self):
        parser = RiscvParser()
        state = RiscvArchitecturalState()
        program = """t0Test:
        sp3:
        zero_187_jo_do:
        _test01:
        _sp_:
        sp_0x_0xF:
        beq x0, x1, t0Test
        beq x0, x1, sp3
        beq x0, x1, zero_187_jo_do
        beq x0, x1, _test01
        beq x0, x1, _sp
        beq x0, x1, sp_0x_0xF
        add x0, x1, x2
        jal x2, sp3
        """
        parser.program = program
        parser.state = state
        parser._sanitize()
        parser._tokenize()

        parsed = [
            result[2] for result in [(n, l, p[0]) for (n, l, p) in parser.token_list]
        ]
        self.assertEqual(
            [result if type(result) == str else result.as_list() for result in parsed],
            [
                "t0Test",
                "sp3",
                "zero_187_jo_do",
                "_test01",
                "_sp_",
                "sp_0x_0xF",
                ["beq", ["x", "0"], ["x", "1"], "t0Test"],
                ["beq", ["x", "0"], ["x", "1"], "sp3"],
                ["beq", ["x", "0"], ["x", "1"], "zero_187_jo_do"],
                ["beq", ["x", "0"], ["x", "1"], "_test01"],
                ["beq", ["x", "0"], ["x", "1"], "_sp"],
                ["beq", ["x", "0"], ["x", "1"], "sp_0x_0xF"],
                ["add", ["x", "0"], ["x", "1"], ["x", "2"]],
                ["jal", ["x", "2"], "sp3"],
            ],
        )

    def test_custom_exceptions(self):
        false_code_1 = """addi x1, x0, 15
        subi x1, x0, 15
        """
        parser = RiscvParser()
        state = RiscvArchitecturalState()
        with self.assertRaises(ParserSyntaxException) as cm:
            parser.parse(false_code_1, state)
        self.assertEqual(
            cm.exception, ParserSyntaxException(line_number=2, line="subi x1, x0, 15")
        )

        false_code_2 = """add x0, x0, x0
        t:
        beq x0, x0, tt"""
        with self.assertRaises(ParserLabelException) as cm:
            parser.parse(false_code_2, state)
        self.assertEqual(
            cm.exception,
            ParserLabelException(line_number=3, line="beq x0, x0, tt", label="tt"),
        )

        false_code_3 = """# a comment
        add x0, x0, x0
        # something
        beq x0, x0, -1
        """
        with self.assertRaises(ParserOddImmediateException) as cm:
            parser.parse(false_code_3, state)
        self.assertEqual(
            cm.exception,
            ParserOddImmediateException(
                line_number=4,
                line="beq x0, x0, -1",
            ),
        )

        false_code_4 = """addi x1, x0, 5
        and x2, x1, x1
        jal x0, t1, -24
        beq x0, x0, 4
        """
        with self.assertRaises(ParserSyntaxException) as cm:
            parser.parse(false_code_4, state)
        self.assertEqual(
            cm.exception, ParserSyntaxException(line_number=3, line="jal x0, t1, -24")
        )

        false_code_5 = """addi x1, x0, 0x-5 # Käse
        add x0, x0, x0
        addi x0, x0, x0
        """
        with self.assertRaises(ParserSyntaxException) as cm:
            parser.parse(false_code_5, state)
        self.assertEqual(
            cm.exception, ParserSyntaxException(line_number=1, line="addi x1, x0, 0x-5")
        )

        false_code_6 = """# ablhsdldfs
        # bliblablub
        addi x1, x0, 0b5555 #asdad
        #ffff"""
        with self.assertRaises(ParserSyntaxException) as cm:
            parser.parse(false_code_6, state)
        self.assertEqual(
            cm.exception,
            ParserSyntaxException(line_number=3, line="addi x1, x0, 0b5555"),
        )

        false_code_7 = """add x0, x5
        x1:
        # not a comment
        """
        with self.assertRaises(ParserSyntaxException) as cm:
            parser.parse(false_code_7, state)
        self.assertEqual(
            cm.exception, ParserSyntaxException(line_number=1, line="add x0, x5")
        )

    def test_multiple_notations(self):
        program = """toast:
        beq x0, x0, toast
        beq x0, x0, 8
        beq x0, x0, toast+0x4"""

        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(program, state)
        instr = list(state.instruction_memory.instructions.values())
        self.assertIsInstance(instr[0], BEQ)
        self.assertEqual(instr[0].rs1, 0)
        self.assertEqual(instr[0].rs2, 0)
        self.assertEqual(instr[0].imm, 0)

        self.assertIsInstance(instr[1], BEQ)
        self.assertEqual(instr[1].rs1, 0)
        self.assertEqual(instr[1].rs2, 0)
        self.assertEqual(instr[1].imm, 8)

        self.assertIsInstance(instr[2], BEQ)
        self.assertEqual(instr[2].rs1, 0)
        self.assertEqual(instr[2].rs2, 0)
        self.assertEqual(instr[2].imm, -4)

        program_2 = """lw x0, x1, 8
        lw x0, 8(x1)"""
        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(program_2, state)
        instr_2 = list(state.instruction_memory.instructions.values())
        self.assertIsInstance(instr_2[0], LW)
        self.assertEqual(instr_2[0].rd, 0)
        self.assertEqual(instr_2[0].rs1, 1)
        self.assertEqual(instr_2[0].imm, 8)

        self.assertIsInstance(instr_2[1], LW)
        self.assertEqual(instr_2[1].rd, 0)
        self.assertEqual(instr_2[1].rs1, 1)
        self.assertEqual(instr_2[1].imm, 8)

    def test_segmentation(self):
        program = """.data
        test: .byte 0
        .text
        addi x0, x0, 0
        """

        program2 = """.text
        addi x0, x0, 0
        .data
        test: .byte 0
        """

        program3 = """addi x0, x0, 0
        .data
        test: .byte 0
        """

        program4 = """test: .byte 0
        .text
        addi x0, x0, 0
        """

        program5 = """.data
        test: .byte 0
        .data
        test2: .byte 0
        """

        program6 = """.data
        test: .byte 0
        """

        program7 = """.data
        test: .byte 0
        .text
        """

        program8 = """.text
        addi x1, x1, 1
        addi x2, x2, 2
        """

        program9 = """.text
        addi x1, x1, 1
        addi x2, x2, 2
        .data
        """

        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(program, state)

        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(program2, state)

        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(program3, state)

        parser = RiscvParser()
        with self.assertRaises(ParserDirectiveException) as cm:
            parser.parse(program4, state)

        parser = RiscvParser()
        with self.assertRaises(ParserDirectiveException) as cm:
            parser.parse(program5, state)

        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(program6, state)

        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(program7, state)

        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(program8, state)

        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(program9, state)

    def test_data_segment(self):
        parser = RiscvParser()
        state = RiscvArchitecturalState()
        program = """.data
        test1: .byte 42
        test2: .half 0x5
        test3: .word 0x2, 0b1011, -99
        .text
        addi x0, x0, 0
        ori x0, x0, 0"""

        parser.parse(program, state)
        instr = list(state.instruction_memory.instructions.values())
        self.assertEqual(instr.__len__(), 2)
        self.assertEqual(instr[0].mnemonic, "addi")
        self.assertEqual(instr[1].mnemonic, "ori")

        program2 = """.data
        test1: .byte 42
        test2: .half 0x5
        test3: .word 0x2, 0b1011, -99
        addi x0, x0, 0
        .text
        ori x0, x0, 0"""

        parser = RiscvParser()
        with self.assertRaises(ParserDataSyntaxException) as cm:
            parser.parse(program2, state)
        self.assertEqual(
            cm.exception,
            ParserDataSyntaxException(line_number=5, line="addi x0, x0, 0"),
        )

        program3 = """.data
        test1: .byte 42
        test2: .half 0x5
        .data
        test3: .word 0x2, 0b1011, -99
        .text
        addi x0, x0, 0
        ori x0, x0, 0"""

        parser = RiscvParser()
        with self.assertRaises(ParserDirectiveException) as cm:
            parser.parse(program3, state)
        self.assertEqual(
            cm.exception,
            ParserDirectiveException(line_number=4, line=".data"),
        )

        program4 = """.data
        test1: .byte 42
        test2: .half 0x5
        test3: .word 0x2, 0b1011, -99
        .text
        addi x0, x0, 0
        ori x0, x0, 0
        .data"""

        parser = RiscvParser()
        with self.assertRaises(ParserDirectiveException) as cm:
            parser.parse(program4, state)

        program5 = """.data
        test1: .byte 42
        test2: .half 0x5
        test3: .word 0x2, 0b1011, -99
        .text
        addi x0, x0, 0
        ori x0, x0, 0
        .text"""

        parser = RiscvParser()
        with self.assertRaises(ParserDirectiveException) as cm:
            parser.parse(program5, state)

        program6 = """.data
        test1: .byte 42
        test2: .half 0x5
        .text
        test3: .word 0x2, 0b1011, -99
        addi x0, x0, 0
        ori x0, x0, 0"""

        parser = RiscvParser()
        with self.assertRaises(ParserSyntaxException) as cm:
            parser.parse(program6, state)

    def test_string(self):
        program = """.data
        dummy: .word 0
        test1: .string "Hello, World!"
        test2: .string "a"
        .text
        lb x1, test1     # = H
        lb x2, test1[1]  # = e
        lb x3, test1[12] # = !
        lb x4, test1[13] # = 0x0 (null terminator)
        lb x5, test2
        """

        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(program, state)
        simulation = RiscvSimulation(state=state)
        simulation.run()

        self.assertEqual(
            state.register_file.registers[1],
            fixedint.UInt32(ord("H")),
        )
        self.assertEqual(
            state.register_file.registers[2],
            fixedint.UInt32(ord("e")),
        )
        self.assertEqual(
            state.register_file.registers[3],
            fixedint.UInt32(ord("!")),
        )
        self.assertEqual(
            state.register_file.registers[4],
            fixedint.UInt32(0),
        )
        self.assertEqual(
            state.register_file.registers[5],
            fixedint.UInt32(ord("a")),
        )

    def test_zero(self):
        program = """.data
        d1: .zero 16
        a1: .word 1, 2
        a3: .byte 11, 12
        d2: .zero 2
        a2: .word 3
        .text
        nop
        """

        sim = RiscvSimulation()
        sim.load_program(program)
        sim.run()
        base_addr = sim.state.memory.address_range.start
        self.assertEqual(sim.state.memory.read_word(base_addr + 0), 0)
        self.assertEqual(sim.state.memory.read_word(base_addr + 60), 0)
        self.assertEqual(sim.state.memory.read_word(base_addr + 64), 1)
        self.assertEqual(sim.state.memory.read_word(base_addr + 68), 2)
        self.assertEqual(sim.state.memory.read_word(base_addr + 76), 0)
        self.assertEqual(sim.state.memory.read_word(base_addr + 80), 0)
        self.assertEqual(sim.state.memory.read_word(base_addr + 84), 3)

    def test_pseudo_instructions_variables(self):
        parser = RiscvParser()
        state = RiscvArchitecturalState()
        program = """.data
        test1: .byte 42, 43, 44
        test2: .half 0x5
        test3: .word 0x2, 0b1011, -99
        .text
        lb x5, test1
        lh x6, test2
        lw x7, test3
        lw x8, test3[2]"""

        parser.parse(program, state)

        self.assertEqual(
            state.memory.read_byte(state.memory.address_range.start),
            fixedint.UInt8(42),
        )
        self.assertEqual(
            state.memory.read_halfword(state.memory.address_range.start + 4),
            fixedint.UInt16(5),
        )
        self.assertEqual(
            state.memory.read_word(state.memory.address_range.start + 8),
            fixedint.UInt32(0x2),
        )
        self.assertEqual(
            state.memory.read_word(state.memory.address_range.start + 4 * 4),
            fixedint.UInt32(-99),
        )
        # out of bounds
        self.assertEqual(
            state.memory.read_word(state.memory.address_range.start + 5 * 4),
            fixedint.UInt32(0),
        )

        program2 = """.data
        test1: .byte 42
        test2: .half 0xA
        test3: .word 0x2, 0b1011, 0, -555, -1
        .text
        la x5, test1
        la x6, test2
        la x7, test3
        la x8, test3[0] # == test3
        la x9, test3[1]
        la x10, test3[2]
        la x11, test3[3]
        la x12, test3[4]
        la x13, test3[5] # out of bounds"""

        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(program2, state)
        simulation = RiscvSimulation(state)
        simulation.run()

        self.assertEqual(
            state.memory.read_byte(state.memory.address_range.start),
            fixedint.UInt32(42),
        )
        self.assertEqual(
            state.memory.read_halfword(state.memory.address_range.start + 4),
            fixedint.UInt32(10),
        )
        self.assertEqual(
            state.memory.read_word(state.memory.address_range.start + 8),
            fixedint.UInt32(2),
        )
        self.assertEqual(
            state.memory.read_word(state.memory.address_range.start + 12),
            fixedint.UInt32(11),
        )
        self.assertEqual(
            state.memory.read_word(state.memory.address_range.start + 16),
            fixedint.UInt32(0),
        )
        self.assertEqual(
            state.memory.read_word(state.memory.address_range.start + 20),
            fixedint.UInt32(-555),
        )
        self.assertEqual(
            state.memory.read_word(state.memory.address_range.start + 24),
            fixedint.UInt32(-1),
        )

        self.assertEqual(state.instruction_memory.read_instruction(0).mnemonic, "lui")
        self.assertEqual(
            state.instruction_memory.read_instruction(0).imm,
            state.memory.address_range.start >> 12,
        )
        self.assertEqual(state.instruction_memory.read_instruction(0).rd, 5)
        self.assertEqual(state.instruction_memory.read_instruction(4).mnemonic, "addi")
        self.assertEqual(
            state.instruction_memory.read_instruction(4).imm,
            state.memory.address_range.start & 0xFFF,
        )
        self.assertEqual(state.instruction_memory.read_instruction(4).rs1, 5)

        self.assertEqual(state.instruction_memory.read_instruction(48).mnemonic, "lui")
        self.assertEqual(
            state.instruction_memory.read_instruction(48).imm,
            (state.memory.address_range.start + 20) >> 12,
        )
        self.assertEqual(state.instruction_memory.read_instruction(48).rd, 11)
        self.assertEqual(state.instruction_memory.read_instruction(52).mnemonic, "addi")
        self.assertEqual(
            state.instruction_memory.read_instruction(52).imm,
            (state.memory.address_range.start + 20) & 0xFFF,
        )
        self.assertEqual(state.instruction_memory.read_instruction(52).rs1, 11)

        self.assertEqual(
            state.register_file.registers[5],
            state.memory.address_range.start,
        )
        self.assertEqual(
            state.register_file.registers[6],
            state.memory.address_range.start + 4,
        )
        self.assertEqual(
            state.register_file.registers[7],
            state.memory.address_range.start + 8,
        )
        self.assertEqual(
            state.register_file.registers[8],
            state.memory.address_range.start + 8,
        )
        self.assertEqual(
            state.register_file.registers[9],
            state.memory.address_range.start + 12,
        )
        self.assertEqual(
            state.register_file.registers[10],
            state.memory.address_range.start + 16,
        )
        self.assertEqual(
            state.register_file.registers[12],
            state.memory.address_range.start + 24,
        )
        self.assertEqual(
            state.register_file.registers[13],
            state.memory.address_range.start + 28,
        )

        program3 = """.data
        test1: .byte 42
        test2: .half 0xA
        test3: .word 0x2, 0b1011, 0, -555, -1
        .text
        la x5, test2
        lh x6, 0(x5)
        la x7, test3
        lw x8, 0(x7)
        lw x9, 12(x7)
        la x10, test3[3]
        lw x11, 0(x10)"""

        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(program3, state)
        simulation = RiscvSimulation(state)
        simulation.run()

        self.assertEqual(state.register_file.registers[6], 10)
        self.assertEqual(state.register_file.registers[8], 2)
        self.assertEqual(state.register_file.registers[9], fixedint.UInt32(-555))
        self.assertEqual(state.register_file.registers[11], fixedint.UInt32(-555))

        program4 = """.data
        test1: .byte 42
        test2: .half 0xA
        .text
        la x5, test1
        la x6, test2
        la x7, xxxxx"""

        with self.assertRaises(ParserVariableException) as cm:
            parser.parse(program4, state)
        self.assertEqual(
            cm.exception,
            ParserVariableException(
                line_number=7,
                line="la x7, xxxxx",
                name="xxxxx",
            ),
        )

    def test_mem_immediate_pseudos(self):
        program = """.data
        test1: .byte 42
        test2: .half 0xA
        test3: .word 0x2, 0b1011, 0, -555, -1
        .text
        lb x5, test1
        lh x6, test2
        lw x7, test3
        lw x8, test3[0]
        lw x9, test3[1]
        lw x10, test3[2]
        lw x11, test3[3]
        lw x12, test3[4]"""

        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(program, state)
        simulation = RiscvSimulation(state)
        simulation.run()

        length = 4
        self.assertEqual(
            state.instruction_memory.read_instruction(0 * length).mnemonic, "lui"
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(0 * length).imm,
            state.memory.address_range.start >> 12,
        )
        self.assertEqual(state.instruction_memory.read_instruction(0 * length).rd, 5)
        self.assertEqual(
            state.instruction_memory.read_instruction(1 * length).mnemonic, "addi"
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(1 * length).imm,
            state.memory.address_range.start & 0xFFF,
        )
        self.assertEqual(state.instruction_memory.read_instruction(1 * length).rs1, 5)
        self.assertEqual(state.instruction_memory.read_instruction(1 * length).rd, 5)
        self.assertEqual(
            state.instruction_memory.read_instruction(2 * length).mnemonic, "lb"
        )
        self.assertEqual(state.instruction_memory.read_instruction(2 * length).imm, 0)
        self.assertEqual(state.instruction_memory.read_instruction(2 * length).rs1, 5)
        self.assertEqual(state.instruction_memory.read_instruction(2 * length).rd, 5)

        self.assertEqual(
            state.instruction_memory.read_instruction(3 * length).mnemonic, "lui"
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(3 * length).imm,
            (state.memory.address_range.start + 4) >> 12,
        )
        self.assertEqual(state.instruction_memory.read_instruction(3 * length).rd, 6)
        self.assertEqual(
            state.instruction_memory.read_instruction(4 * length).mnemonic, "addi"
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(4 * length).imm,
            (state.memory.address_range.start + 4) & 0xFFF,
        )
        self.assertEqual(state.instruction_memory.read_instruction(4 * length).rs1, 6)
        self.assertEqual(state.instruction_memory.read_instruction(4 * length).rd, 6)
        self.assertEqual(
            state.instruction_memory.read_instruction(5 * length).mnemonic, "lh"
        )
        self.assertEqual(state.instruction_memory.read_instruction(5 * length).imm, 0)
        self.assertEqual(state.instruction_memory.read_instruction(5 * length).rs1, 6)
        self.assertEqual(state.instruction_memory.read_instruction(5 * length).rd, 6)

        self.assertEqual(
            state.instruction_memory.read_instruction(6 * length).mnemonic, "lui"
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(6 * length).imm,
            (state.memory.address_range.start + 8) >> 12,
        )
        self.assertEqual(state.instruction_memory.read_instruction(6 * length).rd, 7)
        self.assertEqual(
            state.instruction_memory.read_instruction(7 * length).mnemonic, "addi"
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(7 * length).imm,
            (state.memory.address_range.start + 8) & 0xFFF,
        )
        self.assertEqual(state.instruction_memory.read_instruction(7 * length).rs1, 7)
        self.assertEqual(state.instruction_memory.read_instruction(7 * length).rd, 7)

        self.assertEqual(
            state.instruction_memory.read_instruction(8 * length).mnemonic, "lw"
        )
        self.assertEqual(state.instruction_memory.read_instruction(8 * length).imm, 0)
        self.assertEqual(state.instruction_memory.read_instruction(8 * length).rs1, 7)
        self.assertEqual(state.instruction_memory.read_instruction(8 * length).rd, 7)

        self.assertEqual(
            state.instruction_memory.read_instruction(9 * length).mnemonic, "lui"
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(9 * length).imm,
            (state.memory.address_range.start + 8) >> 12,
        )
        self.assertEqual(state.instruction_memory.read_instruction(9 * length).rd, 8)
        self.assertEqual(
            state.instruction_memory.read_instruction(10 * length).mnemonic, "addi"
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(10 * length).imm,
            (state.memory.address_range.start + 8) & 0xFFF,
        )
        self.assertEqual(state.instruction_memory.read_instruction(10 * length).rs1, 8)
        self.assertEqual(state.instruction_memory.read_instruction(10 * length).rd, 8)
        self.assertEqual(
            state.instruction_memory.read_instruction(11 * length).mnemonic, "lw"
        )
        self.assertEqual(state.instruction_memory.read_instruction(11 * length).imm, 0)
        self.assertEqual(state.instruction_memory.read_instruction(11 * length).rs1, 8)
        self.assertEqual(state.instruction_memory.read_instruction(11 * length).rd, 8)

        self.assertEqual(state.register_file.registers[5], fixedint.UInt32(42))
        self.assertEqual(state.register_file.registers[6], fixedint.UInt32(10))
        self.assertEqual(state.register_file.registers[7], fixedint.UInt32(2))
        self.assertEqual(state.register_file.registers[8], fixedint.UInt32(2))
        self.assertEqual(state.register_file.registers[9], fixedint.UInt32(11))
        self.assertEqual(state.register_file.registers[10], fixedint.UInt32(0))
        self.assertEqual(state.register_file.registers[11], fixedint.UInt32(-555))
        self.assertEqual(state.register_file.registers[12], fixedint.UInt32(-1))

    def test_s_type_pseudos(self):
        program = """.data
        test1: .byte 42
        test2: .half 0xA
        test3: .word 0x2, 0b1011, 0, -555, -1
        .text
        addi x1, x1, 47
        addi x2, x2, 0xBB
        addi x3, x3, 0x7FF
        sb x1, test1, x5
        sh x2, test2, x5
        sw x3, test3[2], x5
        """

        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(program, state)

        length = 4
        self.assertEqual(
            state.instruction_memory.read_instruction(3 * length).mnemonic, "lui"
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(3 * length).imm,
            state.memory.address_range.start >> 12,
        )
        self.assertEqual(state.instruction_memory.read_instruction(3 * length).rd, 5)
        self.assertEqual(
            state.instruction_memory.read_instruction(4 * length).mnemonic, "addi"
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(4 * length).imm,
            state.memory.address_range.start & 0xFFF,
        )
        self.assertEqual(state.instruction_memory.read_instruction(4 * length).rs1, 5)
        self.assertEqual(state.instruction_memory.read_instruction(4 * length).rd, 5)
        self.assertEqual(
            state.instruction_memory.read_instruction(5 * length).mnemonic, "sb"
        )
        self.assertEqual(state.instruction_memory.read_instruction(5 * length).imm, 0)
        self.assertEqual(state.instruction_memory.read_instruction(5 * length).rs1, 5)
        self.assertEqual(state.instruction_memory.read_instruction(5 * length).rs2, 1)

        self.assertEqual(
            state.instruction_memory.read_instruction(6 * length).mnemonic, "lui"
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(6 * length).imm,
            state.memory.address_range.start + 4 >> 12,
        )
        self.assertEqual(state.instruction_memory.read_instruction(6 * length).rd, 5)
        self.assertEqual(
            state.instruction_memory.read_instruction(7 * length).mnemonic, "addi"
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(7 * length).imm,
            state.memory.address_range.start + 4 & 0xFFF,
        )
        self.assertEqual(state.instruction_memory.read_instruction(7 * length).rs1, 5)
        self.assertEqual(state.instruction_memory.read_instruction(7 * length).rd, 5)
        self.assertEqual(
            state.instruction_memory.read_instruction(8 * length).mnemonic, "sh"
        )
        self.assertEqual(state.instruction_memory.read_instruction(8 * length).imm, 0)
        self.assertEqual(state.instruction_memory.read_instruction(8 * length).rs1, 5)
        self.assertEqual(state.instruction_memory.read_instruction(8 * length).rs2, 2)

        self.assertEqual(
            state.instruction_memory.read_instruction(9 * length).mnemonic, "lui"
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(9 * length).imm,
            state.memory.address_range.start + 16 >> 12,
        )
        self.assertEqual(state.instruction_memory.read_instruction(9 * length).rd, 5)
        self.assertEqual(
            state.instruction_memory.read_instruction(10 * length).mnemonic, "addi"
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(10 * length).imm,
            state.memory.address_range.start + 16 & 0xFFF,
        )
        self.assertEqual(state.instruction_memory.read_instruction(10 * length).rs1, 5)
        self.assertEqual(state.instruction_memory.read_instruction(10 * length).rd, 5)
        self.assertEqual(
            state.instruction_memory.read_instruction(11 * length).mnemonic, "sw"
        )
        self.assertEqual(state.instruction_memory.read_instruction(11 * length).imm, 0)
        self.assertEqual(state.instruction_memory.read_instruction(11 * length).rs1, 5)
        self.assertEqual(state.instruction_memory.read_instruction(11 * length).rs2, 3)

        self.assertEqual(
            state.memory.read_byte(state.memory.address_range.start),
            fixedint.UInt32(42),
        )
        self.assertEqual(
            state.memory.read_halfword(state.memory.address_range.start + 4),
            fixedint.UInt32(10),
        )
        self.assertEqual(
            state.memory.read_word(state.memory.address_range.start + 16),
            fixedint.UInt32(0),
        )

        simulation = RiscvSimulation(state=state)
        simulation.run()

        self.assertEqual(
            state.memory.read_byte(state.memory.address_range.start),
            fixedint.UInt32(47),
        )
        self.assertEqual(
            state.memory.read_halfword(state.memory.address_range.start + 4),
            fixedint.UInt32(0xBB),
        )
        self.assertEqual(
            state.memory.read_word(state.memory.address_range.start + 16),
            fixedint.UInt32(0x7FF),
        )

    def test_li(self):
        program = """li x1, 0x0
        li x2, 1
        li x3, -1
        li x4, 0xABCDEF
        li x5, 0xFFFFFFFF
        li x6, -1234567"""

        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(program, state)
        simulation = RiscvSimulation(state)
        simulation.run()

        length = 4
        self.assertEqual(
            state.instruction_memory.read_instruction(0 * length).mnemonic, "addi"
        )
        self.assertEqual(state.instruction_memory.read_instruction(0 * length).imm, 0)
        self.assertEqual(state.instruction_memory.read_instruction(0 * length).rd, 1)
        self.assertEqual(
            state.instruction_memory.read_instruction(1 * length).mnemonic, "addi"
        )
        self.assertEqual(state.instruction_memory.read_instruction(1 * length).imm, 1)
        self.assertEqual(state.instruction_memory.read_instruction(1 * length).rs1, 0)
        self.assertEqual(state.instruction_memory.read_instruction(1 * length).rd, 2)
        self.assertEqual(
            state.instruction_memory.read_instruction(2 * length).mnemonic, "addi"
        )
        self.assertEqual(state.instruction_memory.read_instruction(2 * length).imm, -1)

        self.assertEqual(
            state.instruction_memory.read_instruction(3 * length).mnemonic, "lui"
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(3 * length).imm, 0xABC + 1
        )
        self.assertEqual(state.instruction_memory.read_instruction(3 * length).rd, 4)
        self.assertEqual(
            state.instruction_memory.read_instruction(4 * length).mnemonic, "addi"
        )
        self.assertEqual(
            state.instruction_memory.read_instruction(4 * length).imm, 0xDEF - 4096
        )
        self.assertEqual(state.instruction_memory.read_instruction(4 * length).rs1, 4)
        self.assertEqual(state.instruction_memory.read_instruction(4 * length).rd, 4)

        self.assertEqual(state.register_file.registers[1], fixedint.UInt32(0))
        self.assertEqual(state.register_file.registers[2], fixedint.UInt32(1))
        self.assertEqual(state.register_file.registers[3], fixedint.UInt32(-1))
        self.assertEqual(
            state.register_file.registers[4],
            fixedint.UInt32(0xABCDEF),
        )
        self.assertEqual(
            state.register_file.registers[5],
            fixedint.UInt32(0xFFFFFFFF),
        )
        self.assertEqual(state.register_file.registers[5], fixedint.UInt32(-1))
        self.assertEqual(
            state.register_file.registers[6],
            fixedint.UInt32(-1234567),
        )

    def test_in_line_labels(self):
        program = """
        Banane:
        Birne: ADD x0, x0, x0
        Label: JAL x0, Birne
        _Apf_el: ADDI x0, x0, 0xFF
        Kirsche: SB x0, x0, 0xFF
        Hambeere:
        Himbeere: BEQ x0, x0, Kirsche
        Blaubeere: LUI x0, 0xFF
        CSR: csrrw x0, 0xa, x0
        NOP: NOP
        e_c_all: ecall # Comment
        # ...
        """

        parser = RiscvParser()
        state = RiscvArchitecturalState()
        parser.parse(program, state)
        self.assertEqual(parser.labels["Banane"], parser.labels["Birne"])
        self.assertEqual(parser.labels["Hambeere"], parser.labels["Himbeere"])
        self.assertEqual(parser.labels["Hambeere"], 16)
        self.assertEqual(parser.labels["NOP"], 28)

        program = """
        .text
        addi x1, x0, 10
        start: add x2, x2, x1 # comment
        label:
        addi x1, x1, -1
        bne x0, x1, start
        end: # comment
        """
        sim = RiscvSimulation()
        sim.load_program(program)
        for _ in range(100):
            sim.step()
        self.assertEqual(sim.state.register_file.registers[2], 55)

    def test_m_extension_instructions(self):
        program = """
        addi x1, x0, -10
        addi x2, x0, 22
        addi x3, x0, -1
        addi x4, x0, 1
        addi x5, x0, -1
        addi x6, x0, 1
        addi x7, x0, -1
        addi x8, x0, 1
        addi x9, x0, -100
        addi x10, x0, -9
        addi x11, x0, 101
        addi x12, x0, -1
        addi x13, x0, 12
        addi x14, x0, -5
        addi x15, x0, -1
        addi x16, x0, 2
        #
        mul x20, x1, x2
        mulh x21, x3, x4
        mulhu x22, x5, x6
        mulhsu x23, x7, x8
        div x24, x9, x10
        divu x25, x11, x12
        rem x26, x13, x14
        remu x27, x15, x16
        """
        sim = RiscvSimulation()
        sim.load_program(program)
        sim.run()

        self.assertEqual(sim.state.register_file.registers[20], fixedint.UInt32(-220))
        self.assertEqual(sim.state.register_file.registers[21], fixedint.UInt32(-1))
        self.assertEqual(sim.state.register_file.registers[22], fixedint.UInt32(0))
        self.assertEqual(sim.state.register_file.registers[23], fixedint.UInt32(-1))
        self.assertEqual(sim.state.register_file.registers[24], fixedint.UInt32(11))
        self.assertEqual(sim.state.register_file.registers[25], fixedint.UInt32(0))
        self.assertEqual(sim.state.register_file.registers[26], fixedint.UInt32(2))
        self.assertEqual(sim.state.register_file.registers[27], fixedint.UInt32(1))

        sim = RiscvSimulation(mode="five_stage_pipeline")
        sim.load_program(program)
        sim.run()

        self.assertEqual(sim.state.register_file.registers[20], fixedint.UInt32(-220))
        self.assertEqual(sim.state.register_file.registers[21], fixedint.UInt32(-1))
        self.assertEqual(sim.state.register_file.registers[22], fixedint.UInt32(0))
        self.assertEqual(sim.state.register_file.registers[23], fixedint.UInt32(-1))
        self.assertEqual(sim.state.register_file.registers[24], fixedint.UInt32(11))
        self.assertEqual(sim.state.register_file.registers[25], fixedint.UInt32(0))
        self.assertEqual(sim.state.register_file.registers[26], fixedint.UInt32(2))
        self.assertEqual(sim.state.register_file.registers[27], fixedint.UInt32(1))

    def test_data_segment_padding(self):
        program = """
        .data
        t1: .byte 1, 2, 3, 4
        t2: .byte 1, 2, 3
        t3: .byte 1, 2
        t4: .byte 1
        t5: .half 1, 2
        t6: .half 1
        t7: .word 0xFFFFFFFF
        .text
        nop
        """

        sim = RiscvSimulation()
        sim.load_program(program)
        sim.run()

        for addr, val in enumerate([1, 2, 3, 4, 1, 2, 3, 0, 1, 2, 0, 0, 1, 0, 0, 0]):
            self.assertEqual(
                sim.state.memory.read_byte(sim.state.memory.address_range.start + addr),
                val,
            )

        for addr, val in enumerate([1, 2, 1, 0]):
            self.assertEqual(
                sim.state.memory.read_halfword(
                    sim.state.memory.address_range.start + addr * 2 + 16
                ),
                val,
            )

        self.assertEqual(
            sim.state.memory.read_word(sim.state.memory.address_range.start + 24),
            0xFFFFFFFF,
        )

        self.assertEqual(
            sim.state.memory.read_byte(sim.state.memory.address_range.start + 27), 0xFF
        )
        self.assertEqual(
            sim.state.memory.read_byte(sim.state.memory.address_range.start + 28), 0
        )

    def test_mv(self):
        program = """
        addi x1, x0, 1
        addi x2, x0, 2
        addi gp, zero, 3
        addi t0, zero, 4
        addi a0, zero, 5
        ###
        mv x31, x1
        mv t5, x2
        mv x22, t0
        mv s11, a0
        mv zero, gp
        """
        simulation = RiscvSimulation()
        simulation.load_program(program)
        simulation.run()

        self.assertEqual(simulation.state.register_file.registers[31], 1)
        self.assertEqual(simulation.state.register_file.registers[30], 2)
        self.assertEqual(simulation.state.register_file.registers[22], 4)
        self.assertEqual(simulation.state.register_file.registers[27], 5)
        self.assertEqual(simulation.state.register_file.registers[0], 0)
