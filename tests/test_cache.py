from unittest import TestCase
from architecture_simulator.uarch.cache import select_bits
from fixedint import MutableUInt8, MutableUInt16, MutableUInt32, MutableUInt64


class TestCache(TestCase):
    def test_select_bits(self) -> None:
        self.assertEqual(select_bits(0xFF0, 4, 8), 0xF)
        self.assertEqual(select_bits(0xFFFF, 0, 0), 0)
        self.assertEqual(select_bits(0xE, 0, 1), 0)
        self.assertEqual(select_bits(0xABCDABCD, 0, 32), 0xABCDABCD)
        self.assertEqual(select_bits(0xDCBAABCD, 12, 20), 0xAA)
