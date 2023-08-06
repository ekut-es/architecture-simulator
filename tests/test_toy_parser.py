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
)
from architecture_simulator.uarch.toy.toy_architectural_state import (
    ToyArchitecturalState,
)


class TestToyParser(unittest.TestCase):
    def test_sanitize(self):
        parser = ToyParser()
        program = """ADD $030
        INC

        SUB    $200
        NOP#lol
        #Zwetschgenkuchen
        DEC # Ameisenkuchen
        """
        parser.parse(program, state=ToyArchitecturalState())
        expected = [
            (1, "ADD $030"),
            (2, "INC"),
            (4, "SUB    $200"),
            (5, "NOP"),
            (7, "DEC"),
        ]
        self.assertEqual(parser.sanitized_program, expected)

    def test_parse(self):
        parser = ToyParser()
        state = ToyArchitecturalState()
        program = """ADD $030
        INC

        SUB    $200
        NOP#lol
        #Zwetschgenkuchen
        DEC # Ameisenkuchen
        """
        expected = [ADD(0x030), INC(), SUB(0x200), NOP(), DEC()]
        parser.parse(program=program, state=state)
        parsed = state.instruction_memory.instructions
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
        self.assertEqual(state.instruction_memory.instructions, expected)

    def test_write_data(self):
        parser = ToyParser()
        state = ToyArchitecturalState()
        program = """ADD $400
        SUB 1025
        :1025:30
        :$1400:$1000F # test for overflow
        ADD 1025
        #:13141:11111"""
        parser.parse(program=program, state=state)
        self.assertEqual(state.data_memory.read_halfword(1025), 30)
        self.assertEqual(state.data_memory.read_halfword(1024), 15)
        self.assertEqual(state.instruction_memory.read_instruction(0), ADD(1024))
        self.assertEqual(state.instruction_memory.read_instruction(1), SUB(1025))
        self.assertEqual(state.instruction_memory.read_instruction(2), ADD(1025))

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
