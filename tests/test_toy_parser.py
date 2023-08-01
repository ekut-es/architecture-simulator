import unittest

from architecture_simulator.isa.toy.toy_parser import ToyParser


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
