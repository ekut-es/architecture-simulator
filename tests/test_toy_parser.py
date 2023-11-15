import unittest

from architecture_simulator.isa.toy.toy_parser import ToyParser
from architecture_simulator.isa.toy.toy_instructions import (
    ADD,
    SUB,
    INC,
    NOP,
    DEC,
    STO,
    BRZ,
    ToyInstruction,
)
from architecture_simulator.uarch.toy.toy_architectural_state import (
    ToyArchitecturalState,
)

from architecture_simulator.simulation.toy_simulation import ToySimulation

from architecture_simulator.isa.parser_exceptions import (
    ParserDirectiveException,
    ParserDataSyntaxException,
    ParserSyntaxException,
    DuplicateLabelException,
)


class TestToyParser(unittest.TestCase):
    def test_sanitize(self):
        parser = ToyParser()
        program = """ADD 0x030
        INC

        SUB    0x200
        NOP#lol
        #Zwetschgenkuchen
        DEC # Ameisenkuchen
        """
        parser.parse(program, state=ToyArchitecturalState())
        expected = [
            (1, "ADD 0x030"),
            (2, "INC"),
            (4, "SUB    0x200"),
            (5, "NOP"),
            (7, "DEC"),
        ]
        self.assertEqual(parser.sanitized_program, expected)

    def test_parse(self):
        parser = ToyParser()
        state = ToyArchitecturalState()
        program = """ADD 0x030
        INC

        SUB    0x200
        NOP#lol
        #Zwetschgenkuchen
        DEC # Ameisenkuchen
        """
        expected = [ADD(0x030), INC(), SUB(0x200), NOP(), DEC()]
        parser.parse(program=program, state=state)
        parsed = [
            ToyInstruction.from_integer(int(state.memory.read_halfword(i)))
            for i in range(len(expected))
        ]
        self.assertEqual(len(parsed), 5)
        self.assertEqual(parsed[0], expected[0])
        self.assertEqual(parsed[1], expected[1])
        self.assertEqual(parsed[2], expected[2])
        self.assertEqual(parsed[3], expected[3])
        self.assertEqual(parsed[4], expected[4])

    def test_decimal_addresses(self):
        parser = ToyParser()
        state = ToyArchitecturalState()
        program = """INC
        STO 1024
        ADD 1025
        STO 1026
        ADD 2000
        STO 4095
        SUB 1024"""

        parser.parse(program=program, state=state)
        expected = {
            0: INC(),
            1: STO(1024),
            2: ADD(1025),
            3: STO(1026),
            4: ADD(2000),
            5: STO(4095),
            6: SUB(1024),
        }
        parsed = {
            i: ToyInstruction.from_integer(int(state.memory.read_halfword(i)))
            for i in range(len(expected))
        }
        self.assertEqual(parsed, expected)

    def test_write_data(self):
        parser = ToyParser()
        state = ToyArchitecturalState()
        program = """
        .data
        num1: .word 30
        num2: .word 0x1000F # test for overflow
        .text
        ADD 0x400
        SUB num1
        ADD num1
        #:13141:11111"""
        parser.parse(program=program, state=state)
        self.assertEqual(state.memory.read_halfword(4095), 30)
        self.assertEqual(state.memory.read_halfword(4094), 15)
        self.assertEqual(
            ToyInstruction.from_integer(int(state.memory.read_halfword(0))), ADD(1024)
        )
        self.assertEqual(
            ToyInstruction.from_integer(int(state.memory.read_halfword(1))), SUB(4095)
        )
        self.assertEqual(
            ToyInstruction.from_integer(int(state.memory.read_halfword(2))), ADD(4095)
        )

    def test_labels(self):
        parser = ToyParser()
        state = ToyArchitecturalState()
        program = """Ameisenkuchen:
        _Apfeltarte:
        ADD Ameisenkuchen
        INC
        Banan3nkuch3n3:
        BRZ _Apfeltarte
        STO Banan3nkuch3n3"""
        parser.parse(program=program, state=state)
        expected = {0: ADD(0), 1: INC(), 2: BRZ(0), 3: STO(2)}

    def test_load_instructions(self):
        parser = ToyParser()
        state = ToyArchitecturalState()
        program = """INC
        DEC"""
        parser.parse(program, state)
        self.assertEqual(state.max_pc, 1)
        self.assertEqual(state.loaded_instruction, INC())

    def test_data_section(self):
        sim = ToySimulation()
        program = """
        .data
        arr_ptr: .word 1, 0x002, 3, 0x004, 5
        arr_len: .word 5
        sum: .word 0
        .text
        loop:
        LDA sum # add array element to sum
        add_instr:
        ADD arr_ptr
        STO sum
        LDA add_instr # inc array element address
        INC
        STO add_instr
        LDA arr_len # check if done?
        DEC
        STO arr_len
        BRZ end
        ZRO
        BRZ loop
        end:
        NOP
        """
        sim.load_program(program)
        state = sim.state
        self.assertEqual(state.memory.read_halfword(4090), 5)
        sim.run()
        self.assertEqual(state.memory.read_halfword(4091), 1)
        self.assertEqual(state.memory.read_halfword(4092), 2)
        self.assertEqual(state.memory.read_halfword(4093), 3)
        self.assertEqual(state.memory.read_halfword(4094), 4)
        self.assertEqual(state.memory.read_halfword(4095), 5)
        self.assertEqual(state.memory.read_halfword(4090), 0)
        self.assertEqual(state.memory.read_halfword(4089), 15)

        program = """
        #comment
        .data
        p_1: .word 11 #comment
        p_2: .word 12, 13, 0x00E, 0x00F
        p_3: .word 16
        #comment
        """
        sim.load_program(program)
        state = sim.state
        self.assertEqual(state.memory.read_halfword(4095), 11)
        self.assertEqual(state.memory.read_halfword(4094), 15)
        self.assertEqual(state.memory.read_halfword(4093), 14)
        self.assertEqual(state.memory.read_halfword(4092), 13)
        self.assertEqual(state.memory.read_halfword(4091), 12)
        self.assertEqual(state.memory.read_halfword(4090), 16)

        with self.assertRaises(ParserDataSyntaxException):
            sim.load_program(".data \n INC")

        with self.assertRaises(ParserDirectiveException):
            sim.load_program(".data \n .text \n .text \n")

        with self.assertRaises(ParserSyntaxException):
            sim.load_program(".ljksadflkj \n")

        with self.assertRaises(ParserSyntaxException):
            sim.load_program(".data label: .word")

        with self.assertRaises(ParserSyntaxException):
            sim.load_program(".ljksadflkj \n")

        with self.assertRaises(DuplicateLabelException):
            sim.load_program("label:\n .data\n label: .word 0")

        with self.assertRaises(DuplicateLabelException):
            sim.load_program(".data\n label: .word 0\n label: .word 0")

        # Does not raise a exception:
        sim.load_program("INC\nINC\n.data\n addr: .word 0")
