import unittest
from fixedint import MutableUInt16

from architecture_simulator.uarch.toy.toy_architectural_state import (
    ToyArchitecturalState,
)
from architecture_simulator.isa.toy.toy_instructions import (
    STO,
    LDA,
    BRZ,
    ADD,
    SUB,
    OR,
    AND,
    XOR,
    NOT,
    INC,
    DEC,
    ZRO,
    NOP,
)


class TestToyInstructions(unittest.TestCase):
    def test_sto(self):
        state = ToyArchitecturalState()
        self.assertEqual(state.data_memory.read_halfword(1024), 0)
        STO(1024).behavior(state)
        self.assertEqual(state.data_memory.read_halfword(1024), 0)
        state.accu = MutableUInt16(1)
        STO(1024).behavior(state)
        self.assertEqual(state.data_memory.read_halfword(1024), 1)
        self.assertEqual(state.accu, 1)
        state.accu = MutableUInt16(2**16 - 1)
        STO(4095).behavior(state)
        self.assertEqual(state.data_memory.read_halfword(4095), 2**16 - 1)
        self.assertEqual(state.program_counter, 3)

    def test_lda(self):
        state = ToyArchitecturalState()
        state.data_memory.write_halfword(1025, MutableUInt16(1))
        state.data_memory.write_halfword(1026, MutableUInt16(25))
        state.data_memory.write_halfword(4095, MutableUInt16(2**16 - 1))
        LDA(1024).behavior(state)
        self.assertEqual(state.accu, 0)
        LDA(1025).behavior(state)
        self.assertEqual(state.accu, 1)
        LDA(1026).behavior(state)
        self.assertEqual(state.accu, 25)
        LDA(4095).behavior(state)
        self.assertEqual(state.accu, 2**16 - 1)
        self.assertEqual(state.program_counter, 4)

    def test_brz(self):
        state = ToyArchitecturalState()
        self.assertEqual(state.program_counter, 0)
        BRZ(9).behavior(state)
        self.assertEqual(state.program_counter, 9)
        state.accu = MutableUInt16(1)
        BRZ(200).behavior(state)
        self.assertEqual(state.program_counter, 10)
        state.accu = MutableUInt16(0)
        BRZ(2).behavior(state)
        self.assertEqual(state.program_counter, 2)

    def test_add(self):
        state = ToyArchitecturalState()
        state.data_memory.write_halfword(1024, MutableUInt16(1))
        state.data_memory.write_halfword(1025, MutableUInt16(2))
        state.data_memory.write_halfword(1026, MutableUInt16(10))
        state.data_memory.write_halfword(1027, MutableUInt16(2**16 - 1))
        ADD(1024).behavior(state=state)
        self.assertEqual(state.accu, 1)
        ADD(1024).behavior(state=state)
        self.assertEqual(state.accu, 2)
        ADD(1025).behavior(state=state)
        self.assertEqual(state.accu, 4)
        ADD(1026).behavior(state=state)
        self.assertEqual(state.accu, 14)
        ADD(1027).behavior(state=state)
        self.assertEqual(state.accu, 13)
        self.assertEqual(state.program_counter, 5)

    def test_sub(self):
        state = ToyArchitecturalState()
        state.data_memory.write_halfword(1024, MutableUInt16(1))
        state.data_memory.write_halfword(1025, MutableUInt16(2))
        state.data_memory.write_halfword(1026, MutableUInt16(10))
        state.data_memory.write_halfword(1027, MutableUInt16(2**16 - 1))
        SUB(1024).behavior(state)
        self.assertEqual(state.accu, 2**16 - 1)
        SUB(1027).behavior(state)
        self.assertEqual(state.accu, 0)
        SUB(1026).behavior(state)
        self.assertEqual(state.accu, 2**16 - 10)
        SUB(1025).behavior(state)
        self.assertEqual(state.accu, 2**16 - 12)
        self.assertEqual(state.program_counter, 4)

    def test_or(self):
        state = ToyArchitecturalState()
        state.data_memory.write_halfword(1024, MutableUInt16(0x000F))
        state.data_memory.write_halfword(1025, MutableUInt16(0x0EF0))
        state.data_memory.write_halfword(1026, MutableUInt16(0x0100))
        state.data_memory.write_halfword(1027, MutableUInt16(0xFFFF))
        OR(1024).behavior(state)
        self.assertEqual(state.accu, 0x000F)
        OR(1025).behavior(state)
        self.assertEqual(state.accu, 0x0EFF)
        OR(1026).behavior(state)
        self.assertEqual(state.accu, 0x0FFF)
        OR(1027).behavior(state)
        self.assertEqual(state.accu, 0xFFFF)
        self.assertEqual(state.program_counter, 4)

    def test_and(self):
        state = ToyArchitecturalState()
        state.data_memory.write_halfword(1024, MutableUInt16(0x000F))
        state.data_memory.write_halfword(1025, MutableUInt16(0x0EF0))
        state.data_memory.write_halfword(1026, MutableUInt16(0x0100))
        state.data_memory.write_halfword(1027, MutableUInt16(0xFFFF))
        AND(1024).behavior(state)
        self.assertEqual(state.accu, 0x0000)
        state.accu = MutableUInt16(0x00FA)
        AND(1024).behavior(state)
        self.assertEqual(state.accu, 0x000A)
        AND(1025).behavior(state)
        self.assertEqual(state.accu, 0x0000)
        state.accu = MutableUInt16(0x0100)
        AND(1026).behavior(state)
        self.assertEqual(state.accu, 0x0100)
        AND(1027).behavior(state)
        self.assertEqual(state.accu, 0x0100)
        self.assertEqual(state.program_counter, 5)

    def test_xor(self):
        state = ToyArchitecturalState()
        state.data_memory.write_halfword(1024, MutableUInt16(0b1101))
        state.data_memory.write_halfword(1025, MutableUInt16(0b1111))
        state.data_memory.write_halfword(1026, MutableUInt16(0xFFFF))
        state.data_memory.write_halfword(1027, MutableUInt16(0x0F0F))
        XOR(1024).behavior(state)
        self.assertEqual(state.accu, 0b1101)
        XOR(1024).behavior(state)
        self.assertEqual(state.accu, 0)
        XOR(1025).behavior(state)
        self.assertEqual(state.accu, 0b1111)
        XOR(1026).behavior(state)
        self.assertEqual(state.accu, 0xFFF0)
        XOR(1027).behavior(state)
        self.assertEqual(state.accu, 0xF0FF)
        self.assertEqual(state.program_counter, 5)

    def test_not(self):
        state = ToyArchitecturalState()
        self.assertEqual(state.accu, 0)
        NOT().behavior(state)
        self.assertEqual(state.accu, 2**16 - 1)
        NOT().behavior(state)
        self.assertEqual(state.accu, 0)
        state.accu = MutableUInt16(0xF0F0)
        NOT().behavior(state)
        self.assertEqual(state.accu, 0x0F0F)
        self.assertEqual(state.program_counter, 3)

    def test_inc(self):
        state = ToyArchitecturalState()
        self.assertEqual(state.accu, 0)
        INC().behavior(state)
        self.assertEqual(state.accu, 1)
        INC().behavior(state)
        self.assertEqual(state.accu, 2)
        INC().behavior(state)
        self.assertEqual(state.accu, 3)
        INC().behavior(state)
        self.assertEqual(state.accu, 4)
        state.accu = MutableUInt16(2**16 - 1)
        INC().behavior(state)
        self.assertEqual(state.accu, 0)
        self.assertEqual(state.program_counter, 5)

    def test_dec(self):
        state = ToyArchitecturalState()
        state.accu = MutableUInt16(3)
        DEC().behavior(state)
        self.assertEqual(state.accu, 2)
        DEC().behavior(state)
        self.assertEqual(state.accu, 1)
        DEC().behavior(state)
        self.assertEqual(state.accu, 0)
        DEC().behavior(state)
        self.assertEqual(state.accu, 2**16 - 1)
        self.assertEqual(state.program_counter, 4)

    def test_zro(self):
        state = ToyArchitecturalState()
        state.accu = MutableUInt16(12415)
        ZRO().behavior(state)
        self.assertEqual(state.accu, 0)
        ZRO().behavior(state)
        ZRO().behavior(state)
        ZRO().behavior(state)
        self.assertEqual(state.accu, 0)
        self.assertEqual(state.program_counter, 4)

    def test_nop(self):
        state = ToyArchitecturalState()
        state.accu = MutableUInt16(111)
        NOP().behavior(state)
        NOP().behavior(state)
        NOP().behavior(state)
        self.assertEqual(state.accu, 111)
        self.assertEqual(state.program_counter, 3)

    def test_repr(self):
        self.assertEqual(str(STO(0xDEA)), "STO $DEA")
        self.assertEqual(str(LDA(0xDBE)), "LDA $DBE")
        self.assertEqual(str(BRZ(0xEF0)), "BRZ $EF0")
        self.assertEqual(str(ADD(0x0)), "ADD $000")
        self.assertEqual(str(SUB(0x3)), "SUB $003")
        self.assertEqual(str(OR(0x333)), "OR $333")
        self.assertEqual(str(AND(0xFAF)), "AND $FAF")
        self.assertEqual(str(XOR(0xF8C)), "XOR $F8C")
        self.assertEqual(str(NOT()), "NOT")
        self.assertEqual(str(INC()), "INC")
        self.assertEqual(str(DEC()), "DEC")
        self.assertEqual(str(ZRO()), "ZRO")
        self.assertEqual(str(NOP()), "NOP")

    def test_to_integer(self):
        self.assertEqual(int(STO(125)), 125)
        self.assertEqual(int(LDA(223)), 4319)
        self.assertEqual(int(BRZ(3)), 8195)
        self.assertEqual(int(ADD(5)), 12293)
        self.assertEqual(int(SUB(4095)), 20479)
        self.assertEqual(int(OR(256)), 20736)
        self.assertEqual(int(AND(4000)), 28576)
        self.assertEqual(int(XOR(999)), 29671)
        self.assertEqual(int(NOT()), 32768)
        self.assertEqual(int(INC()), 36864)
        self.assertEqual(int(DEC()), 40960)
        self.assertEqual(int(ZRO()), 45056)
        self.assertEqual(int(NOP()), 49152)

    def test_to_binary(self):
        self.assertEqual(STO(125).to_binary(), "0000000001111101")
        self.assertEqual(LDA(223).to_binary(), "0001000011011111")
        self.assertEqual(BRZ(3).to_binary(), "0010000000000011")
        self.assertEqual(ADD(5).to_binary(), "0011000000000101")
        self.assertEqual(SUB(4095).to_binary(), "0100111111111111")
        self.assertEqual(OR(256).to_binary(), "0101000100000000")
        self.assertEqual(AND(4000).to_binary(), "0110111110100000")
        self.assertEqual(XOR(999).to_binary(), "0111001111100111")
        self.assertEqual(NOT().to_binary(), "1000000000000000")
        self.assertEqual(INC().to_binary(), "1001000000000000")
        self.assertEqual(DEC().to_binary(), "1010000000000000")
        self.assertEqual(ZRO().to_binary(), "1011000000000000")
        self.assertEqual(NOP().to_binary(), "1100000000000000")

    def test_to_hex(self):
        self.assertEqual(STO(125).to_hex(), "007D")
        self.assertEqual(LDA(223).to_hex(), "10DF")
        self.assertEqual(BRZ(3).to_hex(), "2003")
        self.assertEqual(ADD(5).to_hex(), "3005")
        self.assertEqual(SUB(4095).to_hex(), "4FFF")
        self.assertEqual(OR(256).to_hex(), "5100")
        self.assertEqual(AND(4000).to_hex(), "6FA0")
        self.assertEqual(XOR(999).to_hex(), "73E7")
        self.assertEqual(NOT().to_hex(), "8000")
        self.assertEqual(INC().to_hex(), "9000")
        self.assertEqual(DEC().to_hex(), "A000")
        self.assertEqual(ZRO().to_hex(), "B000")
        self.assertEqual(NOP().to_hex(), "C000")
