import unittest
from architecture_simulator.util.integer_representations import (
    get_12_bit_representations,
    get_16_bit_representations,
)


class TestUtil(unittest.TestCase):
    def test_12_bit_representation(self):
        self.assertEqual(
            get_12_bit_representations(0), ("0000 00000000", "0", "0 00", "0")
        )
        self.assertEqual(
            get_12_bit_representations(1), ("0000 00000001", "1", "0 01", "1")
        )
        self.assertEqual(
            get_12_bit_representations(255), ("0000 11111111", "255", "0 FF", "255")
        )
        self.assertEqual(
            get_12_bit_representations(2047), ("0111 11111111", "2047", "7 FF", "2047")
        )
        self.assertEqual(
            get_12_bit_representations(2048), ("1000 00000000", "2048", "8 00", "-2048")
        )
        self.assertEqual(
            get_12_bit_representations(2049), ("1000 00000001", "2049", "8 01", "-2047")
        )
        self.assertEqual(
            get_12_bit_representations(3072), ("1100 00000000", "3072", "C 00", "-1024")
        )
        self.assertEqual(
            get_12_bit_representations(4095), ("1111 11111111", "4095", "F FF", "-1")
        )
        self.assertEqual(
            get_12_bit_representations(4096), ("0000 00000000", "0", "0 00", "0")
        )
        self.assertEqual(
            get_12_bit_representations(4097), ("0000 00000001", "1", "0 01", "1")
        )
        self.assertEqual(
            get_12_bit_representations(-1), ("1111 11111111", "4095", "F FF", "-1")
        )
        self.assertEqual(
            get_12_bit_representations(-2048),
            ("1000 00000000", "2048", "8 00", "-2048"),
        )

    def test_16_bit_representation(self):
        self.assertEqual(
            get_16_bit_representations(1), ("00000000 00000001", "1", "00 01", "1")
        )
        self.assertEqual(
            get_16_bit_representations(0), ("00000000 00000000", "0", "00 00", "0")
        )
        self.assertEqual(
            get_16_bit_representations(255),
            ("00000000 11111111", "255", "00 FF", "255"),
        )
        self.assertEqual(
            get_16_bit_representations(32767),
            ("01111111 11111111", "32767", "7F FF", "32767"),
        )
        self.assertEqual(
            get_16_bit_representations(32768),
            ("10000000 00000000", "32768", "80 00", "-32768"),
        )
        self.assertEqual(
            get_16_bit_representations(32769),
            ("10000000 00000001", "32769", "80 01", "-32767"),
        )
        self.assertEqual(
            get_16_bit_representations(49152),
            ("11000000 00000000", "49152", "C0 00", "-16384"),
        )
        self.assertEqual(
            get_16_bit_representations(65535),
            ("11111111 11111111", "65535", "FF FF", "-1"),
        )
        self.assertEqual(
            get_16_bit_representations(65536), ("00000000 00000000", "0", "00 00", "0")
        )
        self.assertEqual(
            get_16_bit_representations(65537), ("00000000 00000001", "1", "00 01", "1")
        )
        self.assertEqual(
            get_16_bit_representations(-1),
            ("11111111 11111111", "65535", "FF FF", "-1"),
        )
        self.assertEqual(
            get_16_bit_representations(-32767),
            ("10000000 00000001", "32769", "80 01", "-32767"),
        )
