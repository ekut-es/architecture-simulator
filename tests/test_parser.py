import unittest
import pyparsing as pp
from architecture_simulator.simulation.simulation import Simulation
from architecture_simulator.uarch.architectural_state import RegisterFile, Memory
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
    ]

    def test_bnf(self):
        parser = RiscvParser()
        instr = parser.parse_assembly(self.program)
        self.assertEqual(instr.as_list(), self.expected)
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
        expected_labels = {"Ananas": 0, "Banane": 8, "_Banune24_de": 8, "Chinakohl": 24}
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
        simulation = Simulation(
            state=ArchitecturalState(
                register_file=RegisterFile(registers=[0] * 32),
                memory=Memory(memory_file={}),
            ),
            instructions={},
        )
        simulation.append_instructions(self.fibonacci)
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

    def test_compiled_c_programm(self):
        simulation = Simulation(
            state=ArchitecturalState(
                register_file=RegisterFile(registers=[0] * 32),
                memory=Memory(memory_file={}),
            ),
            instructions={},
        )
        simulation.append_instructions(self.fibonacci_c)
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
        simulation = Simulation(
            state=ArchitecturalState(
                register_file=RegisterFile(registers=[0] * 32),
                memory=Memory(memory_file={}),
            ),
            instructions={},
        )
        simulation.append_instructions(self.add_c)
        # print(simulation.instructions)
        while simulation.state.program_counter < 60:
            simulation.step_simulation()
            simulation.state.register_file.registers[0] = 0
        self.assertEqual(int(simulation.state.memory.load_word(4294967268)), 65)
