from unittest import TestCase
from architecture_simulator.uarch.memory.memory import (
    Memory,
    AddressingType,
    UnsupportedFunctionError,
    MemoryAddressError,
)
from fixedint import UInt8, UInt16, UInt32, UInt64


class TestMemory(TestCase):
    def test_mixed(self) -> None:
        mem01 = Memory(AddressingType.BYTE, 32)

        mem01.write_word(0, UInt32(0xFABCFABC))
        self.assertEqual(mem01.read_word(0), 0xFABCFABC)

        mem01.write_doubleword(4, UInt64(0xAAAABBBBCCCCDDDD))
        self.assertEqual(mem01.read_doubleword(4), 0xAAAABBBBCCCCDDDD)
        self.assertEqual(mem01.read_byte(7), 0xCC)
        self.assertEqual(mem01.read_byte(8), 0xBB)
        self.assertEqual(mem01.read_byte(9), 0xBB)
        self.assertEqual(mem01.read_byte(10), 0xAA)

        mem02 = Memory(AddressingType.WORD, 8, True)

        with self.assertRaises(RuntimeError):
            mem02.write_halfword(0, UInt16(0xFFAA))

        mem02.write_word(7 + 2**8, UInt32(0x1234))
        self.assertEqual(mem02.read_word(7), 0x1234)

    def test_byte_addressing(self) -> None:
        mem = Memory(AddressingType.BYTE, 32, False)

        mem.write_byte(0, UInt8(0x01))
        mem.write_halfword(1, UInt16(0x2345))
        mem.write_word(3, UInt32(0x6789ABCD))
        mem.write_doubleword(7, UInt64(0xEF0123456789ABCF))

        self.assertEqual(mem.read_word(0), 0xCD234501)
        self.assertEqual(mem.read_word(4), 0xCF6789AB)
        self.assertEqual(mem.read_doubleword(7), 0xEF0123456789ABCF)
        self.assertEqual(mem.read_byte(2**32 - 1), 0)

        with self.assertRaises(MemoryAddressError):
            mem.read_byte(2**32)

        self.assertEqual(mem.double_wordwise_repr()[0][2], "CF 67 89 AB CD 23 45 01")

        self.assertEqual(mem.bytewise_repr()[14], ("11101111", "239", "EF", "-17"))

        mem = Memory(AddressingType.BYTE, 32, True, range(2**14, 2**32))
        with self.assertRaises(MemoryAddressError):
            mem.read_byte(2**10)

        mem.write_byte(2**15, UInt8(0xAB))
        mem.write_halfword(2**15 - 1, UInt16(0))

        self.assertEqual(mem.read_byte(2**15), 0)

        a = UInt8(0xFA)
        mem.write_byte(2**16, a)
        a += UInt8(1)

        self.assertEqual(mem.read_byte(2**16), 0xFA)

    def test_halfword_addressing(self):
        mem = Memory(AddressingType.HALF_WORD, 12)
        with self.assertRaises(UnsupportedFunctionError):
            mem.read_byte(0)

        with self.assertRaises(UnsupportedFunctionError):
            mem.write_byte(0, UInt8(1))

        with self.assertRaises(UnsupportedFunctionError):
            mem.bytewise_repr()

        try:
            mem.read_byte(0)
        except UnsupportedFunctionError as e:
            self.assertEqual(
                e.__repr__(),
                "This function requires byte-wise addressing, but this memory uses HALF_WORD-wise addressing.",
            )

        mem.write_halfword(0, UInt16(0x3210))
        mem.write_word(1, UInt32(0xBA987654))
        mem.write_doubleword(3, UInt32(0x000000000000FEDC))

        self.assertEqual(mem.read_halfword(1234), 0)
        self.assertEqual(mem.read_word(1), UInt32(0xBA987654))
        self.assertEqual(mem.read_doubleword(0), 0xFEDCBA9876543210)

    def test_word_addressing(self):
        mem = Memory(AddressingType.WORD, 16, True, range(2**8))
        with self.assertRaises(UnsupportedFunctionError):
            mem.read_byte(0)

        with self.assertRaises(UnsupportedFunctionError):
            mem.write_byte(0, UInt8(1))

        with self.assertRaises(UnsupportedFunctionError):
            mem.bytewise_repr()

        with self.assertRaises(UnsupportedFunctionError):
            mem.read_halfword(0)

        with self.assertRaises(UnsupportedFunctionError):
            mem.write_halfword(0, UInt16(1))

        with self.assertRaises(UnsupportedFunctionError):
            mem.half_wordwise_repr()

        mem.write_word(0, UInt32(1234))
        mem.write_word(2**8 - 1, UInt32(0xABCDABCD))

        with self.assertRaises(MemoryAddressError):
            mem.write_word(2**8, UInt32(0xABCDABCD))

        with self.assertRaises(MemoryAddressError):
            mem.read_doubleword(2**8 - 1)

        self.assertEqual(mem.read_word(2**8 - 1), 0xABCDABCD)
        self.assertEqual(mem.read_doubleword(2**8 - 2), 0xABCDABCD00000000)

        self.assertEqual(
            mem.wordwise_repr()[2**8 - 1],
            (
                "10101011 11001101 10101011 11001101",
                str(0xABCDABCD),
                "AB CD AB CD",
                str(-1412584499),
            ),
        )

    def test_doubleword_addressing(self):
        mem = Memory(AddressingType.DOUBLE_WORD, 8, True, range(2**8))
        with self.assertRaises(UnsupportedFunctionError):
            mem.read_byte(0)

        with self.assertRaises(UnsupportedFunctionError):
            mem.write_byte(0, UInt8(1))

        with self.assertRaises(UnsupportedFunctionError):
            mem.bytewise_repr()

        with self.assertRaises(UnsupportedFunctionError):
            mem.read_halfword(0)

        with self.assertRaises(UnsupportedFunctionError):
            mem.write_halfword(0, UInt16(1))

        with self.assertRaises(UnsupportedFunctionError):
            mem.half_wordwise_repr()

        with self.assertRaises(UnsupportedFunctionError):
            mem.read_word(0)

        with self.assertRaises(UnsupportedFunctionError):
            mem.write_word(0, UInt32(1))

        with self.assertRaises(UnsupportedFunctionError):
            mem.wordwise_repr()

        mem.write_doubleword(2**9 + 7, UInt64(122342354563))

        self.assertEqual(mem.read_doubleword(7), 122342354563)
