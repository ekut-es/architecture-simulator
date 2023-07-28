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
        self.assertEqual(state.load(1024), 0)
        STO(1024).behavior(state)
        self.assertEqual(state.load(1024), 0)
        state.accu = MutableUInt16(1)
        STO(1024).behavior(state)
        self.assertEqual(state.load(1024), 1)
        self.assertEqual(state.accu, 1)
        state.accu = MutableUInt16(2**16 - 1)
        STO(4095).behavior(state)
        self.assertEqual(state.load(4095), 2**16 - 1)
        self.assertEqual(state.program_counter, 3)

    def test_lda(self):
        state = ToyArchitecturalState()
        state.store(1025, MutableUInt16(1))
        state.store(1026, MutableUInt16(25))
        state.store(4095, MutableUInt16(2**16 - 1))
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
        state.store(1024, MutableUInt16(1))
        state.store(1025, MutableUInt16(2))
        state.store(1026, MutableUInt16(10))
        state.store(1027, MutableUInt16(2**16 - 1))
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
        state.store(1024, MutableUInt16(1))
        state.store(1025, MutableUInt16(2))
        state.store(1026, MutableUInt16(10))
        state.store(1027, MutableUInt16(2**16 - 1))
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
        state.store(1024, MutableUInt16(0x000F))
        state.store(1025, MutableUInt16(0x0EF0))
        state.store(1026, MutableUInt16(0x0100))
        state.store(1027, MutableUInt16(0xFFFF))
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
        state.store(1024, MutableUInt16(0x000F))
        state.store(1025, MutableUInt16(0x0EF0))
        state.store(1026, MutableUInt16(0x0100))
        state.store(1027, MutableUInt16(0xFFFF))
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
        state.store(1024, MutableUInt16(0b1101))
        state.store(1025, MutableUInt16(0b1111))
        state.store(1026, MutableUInt16(0xFFFF))
        state.store(1027, MutableUInt16(0x0F0F))
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
