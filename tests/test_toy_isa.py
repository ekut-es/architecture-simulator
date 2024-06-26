import unittest
from fixedint import UInt16

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
    ToyInstruction,
)
from architecture_simulator.isa.toy.toy_micro_program import (
    MicroProgram,
    int_to_bool_list,
)


class TestToyInstructions(unittest.TestCase):
    def test_sto(self):
        state = ToyArchitecturalState()
        self.assertEqual(state.memory.read_halfword(1024), 0)
        STO(1024).behavior(state)
        self.assertEqual(state.memory.read_halfword(1024), 0)
        state.accu = UInt16(1)
        STO(1024).behavior(state)
        self.assertEqual(state.memory.read_halfword(1024), 1)
        self.assertEqual(state.visualisation_values.alu_out, state.accu)
        state.accu = UInt16(2**16 - 1)
        STO(4095).behavior(state)
        self.assertEqual(state.memory.read_halfword(4095), 2**16 - 1)

    def test_lda(self):
        state = ToyArchitecturalState()
        state.memory.write_halfword(1025, UInt16(1))
        state.memory.write_halfword(1026, UInt16(25))
        state.memory.write_halfword(4095, UInt16(2**16 - 1))
        LDA(1024).behavior(state)
        self.assertEqual(state.accu, 0)
        LDA(1025).behavior(state)
        self.assertEqual(state.accu, 1)
        LDA(1026).behavior(state)
        self.assertEqual(state.accu, 25)
        self.assertEqual(state.visualisation_values.ram_out, state.accu)
        LDA(4095).behavior(state)
        self.assertEqual(state.accu, 2**16 - 1)

    def test_brz(self):
        state = ToyArchitecturalState()
        self.assertEqual(state.program_counter, 1)
        state.accu = UInt16(1)
        BRZ(2).behavior(state)
        self.assertEqual(state.program_counter, UInt16(1))
        state.accu = UInt16(0)
        BRZ(2).behavior(state)
        self.assertTrue(state.visualisation_values.jump)
        self.assertEqual(state.program_counter, UInt16(2))

    def test_add(self):
        state = ToyArchitecturalState()
        state.memory.write_halfword(1024, UInt16(1))
        state.memory.write_halfword(1025, UInt16(2))
        state.memory.write_halfword(1026, UInt16(10))
        state.memory.write_halfword(1027, UInt16(2**16 - 1))
        ADD(1024).behavior(state=state)
        self.assertEqual(state.accu, 1)
        ADD(1024).behavior(state=state)
        self.assertEqual(state.accu, 2)
        ADD(1025).behavior(state=state)
        self.assertEqual(state.accu, 4)
        ADD(1026).behavior(state=state)
        self.assertEqual(state.accu, 14)
        self.assertEqual(state.accu, state.visualisation_values.alu_out)
        self.assertEqual(
            state.visualisation_values.ram_out, state.memory.read_halfword(1026)
        )
        ADD(1027).behavior(state=state)
        self.assertEqual(state.accu, 13)

    def test_sub(self):
        state = ToyArchitecturalState()
        state.memory.write_halfword(1024, UInt16(1))
        state.memory.write_halfword(1025, UInt16(2))
        state.memory.write_halfword(1026, UInt16(10))
        state.memory.write_halfword(1027, UInt16(2**16 - 1))
        SUB(1024).behavior(state)
        self.assertEqual(state.accu, 2**16 - 1)
        SUB(1027).behavior(state)
        self.assertEqual(state.accu, 0)
        SUB(1026).behavior(state)
        self.assertEqual(state.accu, 2**16 - 10)
        self.assertEqual(state.accu, state.visualisation_values.alu_out)
        self.assertEqual(
            state.visualisation_values.ram_out, state.memory.read_halfword(1026)
        )
        SUB(1025).behavior(state)
        self.assertEqual(state.accu, 2**16 - 12)

    def test_or(self):
        state = ToyArchitecturalState()
        state.memory.write_halfword(1024, UInt16(0x000F))
        state.memory.write_halfword(1025, UInt16(0x0EF0))
        state.memory.write_halfword(1026, UInt16(0x0100))
        state.memory.write_halfword(1027, UInt16(0xFFFF))
        OR(1024).behavior(state)
        self.assertEqual(state.accu, 0x000F)
        OR(1025).behavior(state)
        self.assertEqual(state.accu, 0x0EFF)
        OR(1026).behavior(state)
        self.assertEqual(state.accu, 0x0FFF)
        self.assertEqual(state.accu, state.visualisation_values.alu_out)
        self.assertEqual(
            state.visualisation_values.ram_out, state.memory.read_halfword(1026)
        )
        OR(1027).behavior(state)
        self.assertEqual(state.accu, 0xFFFF)

    def test_and(self):
        state = ToyArchitecturalState()
        state.memory.write_halfword(1024, UInt16(0x000F))
        state.memory.write_halfword(1025, UInt16(0x0EF0))
        state.memory.write_halfword(1026, UInt16(0x0100))
        state.memory.write_halfword(1027, UInt16(0xFFFF))
        AND(1024).behavior(state)
        self.assertEqual(state.accu, 0x0000)
        state.accu = UInt16(0x00FA)
        AND(1024).behavior(state)
        self.assertEqual(state.accu, 0x000A)
        AND(1025).behavior(state)
        self.assertEqual(state.accu, 0x0000)
        state.accu = UInt16(0x0100)
        AND(1026).behavior(state)
        self.assertEqual(state.accu, 0x0100)
        self.assertEqual(state.accu, state.visualisation_values.alu_out)
        self.assertEqual(
            state.visualisation_values.ram_out, state.memory.read_halfword(1026)
        )
        AND(1027).behavior(state)
        self.assertEqual(state.accu, 0x0100)

    def test_xor(self):
        state = ToyArchitecturalState()
        state.memory.write_halfword(1024, UInt16(0b1101))
        state.memory.write_halfword(1025, UInt16(0b1111))
        state.memory.write_halfword(1026, UInt16(0xFFFF))
        state.memory.write_halfword(1027, UInt16(0x0F0F))
        XOR(1024).behavior(state)
        self.assertEqual(state.accu, 0b1101)
        XOR(1024).behavior(state)
        self.assertEqual(state.accu, 0)
        XOR(1025).behavior(state)
        self.assertEqual(state.accu, 0b1111)
        XOR(1026).behavior(state)
        self.assertEqual(state.accu, 0xFFF0)
        self.assertEqual(state.accu, state.visualisation_values.alu_out)
        self.assertEqual(
            state.visualisation_values.ram_out, state.memory.read_halfword(1026)
        )
        XOR(1027).behavior(state)
        self.assertEqual(state.accu, 0xF0FF)

    def test_not(self):
        state = ToyArchitecturalState()
        self.assertEqual(state.accu, 0)
        NOT().behavior(state)
        self.assertEqual(state.accu, 2**16 - 1)
        NOT().behavior(state)
        self.assertEqual(state.accu, 0)
        state.accu = UInt16(0xF0F0)
        NOT().behavior(state)
        self.assertEqual(state.accu, 0x0F0F)
        self.assertEqual(state.visualisation_values.alu_out, state.accu)

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
        self.assertEqual(state.visualisation_values.alu_out, state.accu)
        state.accu = UInt16(2**16 - 1)
        INC().behavior(state)
        self.assertEqual(state.accu, 0)

    def test_dec(self):
        state = ToyArchitecturalState()
        state.accu = UInt16(3)
        DEC().behavior(state)
        self.assertEqual(state.accu, 2)
        DEC().behavior(state)
        self.assertEqual(state.accu, 1)
        self.assertEqual(state.visualisation_values.alu_out, state.accu)
        DEC().behavior(state)
        self.assertEqual(state.accu, 0)
        DEC().behavior(state)
        self.assertEqual(state.accu, 2**16 - 1)

    def test_zro(self):
        state = ToyArchitecturalState()
        state.accu = UInt16(12415)
        self.assertEqual(state.visualisation_values.alu_out, None)
        ZRO().behavior(state)
        self.assertEqual(state.visualisation_values.alu_out, UInt16(0))
        self.assertEqual(state.accu, 0)
        ZRO().behavior(state)
        ZRO().behavior(state)
        ZRO().behavior(state)
        self.assertEqual(state.accu, 0)

    def test_nop(self):
        state = ToyArchitecturalState()
        state.accu = UInt16(111)
        NOP().behavior(state)
        NOP().behavior(state)
        NOP().behavior(state)
        self.assertEqual(state.accu, 111)

    def test_repr(self):
        self.assertEqual(str(STO(0xDEA)), "STO 0xDEA")
        self.assertEqual(str(LDA(0xDBE)), "LDA 0xDBE")
        self.assertEqual(str(BRZ(0xEF0)), "BRZ 0xEF0")
        self.assertEqual(str(ADD(0x0)), "ADD 0x000")
        self.assertEqual(str(SUB(0x3)), "SUB 0x003")
        self.assertEqual(str(OR(0x333)), "OR 0x333")
        self.assertEqual(str(AND(0xFAF)), "AND 0xFAF")
        self.assertEqual(str(XOR(0xF8C)), "XOR 0xF8C")
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

    def test_from_integer(self):
        self.assertEqual(ToyInstruction.from_integer(125), STO(125))
        self.assertEqual(ToyInstruction.from_integer(4319), LDA(223))
        self.assertEqual(ToyInstruction.from_integer(8195), BRZ(3))
        self.assertEqual(ToyInstruction.from_integer(12293), ADD(5))
        self.assertEqual(ToyInstruction.from_integer(20479), SUB(4095))
        self.assertEqual(ToyInstruction.from_integer(20736), OR(256))
        self.assertEqual(ToyInstruction.from_integer(28576), AND(4000))
        self.assertEqual(ToyInstruction.from_integer(29671), XOR(999))
        self.assertEqual(ToyInstruction.from_integer(32768), NOT())
        self.assertEqual(ToyInstruction.from_integer(36864), INC())
        self.assertEqual(ToyInstruction.from_integer(40960), DEC())
        self.assertEqual(ToyInstruction.from_integer(45056), ZRO())
        self.assertEqual(ToyInstruction.from_integer(49152), NOP())
        self.assertEqual(ToyInstruction.from_integer(53248), NOP())
        self.assertEqual(ToyInstruction.from_integer(57344), NOP())
        self.assertEqual(ToyInstruction.from_integer(61440), NOP())

    def test_micro_program(self):
        self.assertTrue(int_to_bool_list(0x800)[0])
        self.assertTrue(int_to_bool_list(0x001)[11])
        self.assertEqual(
            int_to_bool_list(0b110001011100),
            [bool(i) for i in [1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0]],
        )

        self.assertEqual(
            MicroProgram.get_mp_values(type(STO(12))),
            [bool(i) for i in [1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1]],
        )
        self.assertFalse(MicroProgram.get_mp_var_value(type(STO(12)), "set[accu]"))

    def test_address_on_non_address_instructions(self):
        test_number = 0xA00F  # INC
        self.assertEqual(int(ToyInstruction.from_integer(test_number)), test_number)

        test_number = 0x3ABC  # ADD 0xABC
        self.assertEqual(ToyInstruction.from_integer(test_number), ADD(0xABC))

        with self.assertRaises(TypeError):
            STO()
