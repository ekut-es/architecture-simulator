import unittest

from architecture_simulator.isa.toy.toy_parser import ToyParser
from architecture_simulator.isa.toy.toy_instructions import ADD, SUB, INC, NOP, DEC, STO


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
        expected = [
            (1, "ADD $030"),
            (2, "INC"),
            (4, "SUB    $200"),
            (5, "NOP"),
            (7, "DEC"),
        ]
        self.assertEqual(parser._sanitize(program), expected)

    def test_parse(self):
        parser = ToyParser()
        program = """ADD $030
        INC

        SUB    $200
        NOP#lol
        #Zwetschgenkuchen
        DEC # Ameisenkuchen
        """
        expected = [ADD(0x030), INC(), SUB(0x200), NOP(), DEC()]
        parsed = parser.parse(program)
        self.assertEqual(len(parsed), 5)
        self.assertEqual(parsed[0], expected[0])
        self.assertEqual(parsed[1], expected[1])
        self.assertEqual(parsed[2], expected[2])
        self.assertEqual(parsed[3], expected[3])
        self.assertEqual(parsed[4], expected[4])

    def test_dec_addresses(self):
        parser = ToyParser()
        program = """INC
        STO 1024
        ADD 1025
        STO 1026
        ADD 2000
        STO 4095
        SUB 1024"""

        parsed = parser.parse(program)
        expected = [
            INC(),
            STO(1024),
            ADD(1025),
            STO(1026),
            ADD(2000),
            STO(4095),
            SUB(1024),
        ]
        self.assertEqual(parsed, expected)
