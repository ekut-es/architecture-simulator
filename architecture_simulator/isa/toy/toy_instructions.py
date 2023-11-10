from __future__ import annotations
from typing import TYPE_CHECKING, Type
from fixedint import MutableUInt16
from ..instruction import Instruction
from architecture_simulator.uarch.toy.SvgVisValues import SvgVisValues

if TYPE_CHECKING:
    from architecture_simulator.uarch.toy.toy_architectural_state import (
        ToyArchitecturalState,
    )


class ToyInstruction(Instruction):
    """Base class for all Toy instructions.
    Instructions which do not need an address are directly based on this class.
    """

    length: int = 1

    def __init__(self, **kwargs):
        """"""
        """NOTE: I use **kwargs here because otherwise, the parser has to create objects from the 'class objects'.
        Since it only knows if the instruction it is currently looking at is an AddressTypeInstruction or a
        normal ToyInstruction and since it doesnt know which exact subclass it is, it can not know which
        constructor the current instruction has. So to fix this, we use **kwargs for the arguments which we do
        need to fill in in the parser. If you have a better solution (that does not involve creating a separate
        if-case for each instruction), go ahead and change this."""
        self.mnemonic = kwargs["mnemonic"].upper()
        self.opcode = int(kwargs["opcode"]) % 16

    def __repr__(self):
        return self.mnemonic.upper()

    def behavior(self, state: ToyArchitecturalState):
        """Make the instruction perform all of its actions on the given state."""

    def __eq__(self, other):
        """Useful for testing, since you can directly compare instructions."""
        if isinstance(other, ToyInstruction):
            return self.opcode == other.opcode
        return False

    def to_integer(self) -> int:
        """Get the machine code of the instruction as integer value.

        Returns:
            int: machine code
        """
        return self.opcode << 12

    def __int__(self) -> int:
        return self.to_integer()

    def to_binary(self) -> str:
        """Get the machine code of the instrution as 16 digit binary string.

        Returns:
            str: A 16 digit long binary string.
        """
        return "{:016b}".format(int(self))

    def to_hex(self) -> str:
        """Get the machine code of the instruction as 4 digit hexadecimal string.

        Returns:
            str: A 4 digit long hexadecimal string.
        """
        return "{:04X}".format(int(self))

    def op_code_value(self) -> int:
        """
        Return the op code of the instruction as a int.
        """
        return (int(self) >> 12) & 0xF

    def address_section_value(self) -> int:
        """
        Return the address section of a instruction, even if the instruction is no AddressTypeInstruction.
        """
        return int(self) & 0xFFF

    @classmethod
    def from_integer(cls, integer_instruction: int) -> ToyInstruction:
        """Turn a machine code integer into the corresponding instruction object.

        Args:
            integer_instruction (int): machine code of the instruction.

        Returns:
            ToyInstruction: The corresponding instruction object.
        """
        opcode = opcode = (integer_instruction >> 12) & 0xF
        address = integer_instruction & 0xFFF
        if opcode == 0:
            return STO(address)
        elif opcode == 1:
            return LDA(address)
        elif opcode == 2:
            return BRZ(address)
        elif opcode == 3:
            return ADD(address)
        elif opcode == 4:
            return SUB(address)
        elif opcode == 5:
            return OR(address)
        elif opcode == 6:
            return AND(address)
        elif opcode == 7:
            return XOR(address)
        elif opcode == 8:
            return NOT()
        elif opcode == 9:
            return INC()
        elif opcode == 10:
            return DEC()
        elif opcode == 11:
            return ZRO()
        else:
            return NOP()


class AddressTypeInstruction(ToyInstruction):
    """Base class for all instructions which do use an address."""

    def __init__(self, address: int, **kwargs):
        super().__init__(**kwargs)
        self.address = address % 4096

    def __repr__(self):
        return f"{self.mnemonic.upper()} 0x{self.address:03X}"

    def __eq__(self, other):
        if isinstance(other, AddressTypeInstruction):
            return super().__eq__(other) and self.address == other.address
        return False

    def to_integer(self):
        return (self.opcode << 12) + self.address


class STO(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="STO", opcode=0, address=address)

    def behavior(self, state: ToyArchitecturalState):
        """MEM[address] = ACCU"""
        state.visualisation_values = SvgVisValues(alu_out=state.accu)
        state.memory.write_halfword(address=self.address, value=state.accu)


class LDA(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="LDA", opcode=1, address=address)

    def behavior(self, state: ToyArchitecturalState):
        """ACCU = MEM[address]"""
        read_value = state.memory.read_halfword(address=self.address)
        state.visualisation_values = SvgVisValues(
            ram_out=read_value, alu_out=read_value
        )
        state.accu = read_value


class BRZ(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="BRZ", opcode=2, address=address)

    def behavior(self, state: ToyArchitecturalState):
        """PC = ADDRESS if (ACCU == 0)"""
        state.visualisation_values = SvgVisValues(jump=not state.accu)
        if not state.accu:
            state.set_current_pc(MutableUInt16(self.address))
            state.performance_metrics.branch_count += 1


class ADD(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="ADD", opcode=3, address=address)

    def behavior(self, state: ToyArchitecturalState):
        """ACCU += MEM[address]"""
        read_value = state.memory.read_halfword(address=self.address)
        state.visualisation_values = SvgVisValues(
            accu_old=MutableUInt16(int(state.accu)),
            ram_out=read_value,
            alu_out=state.accu + read_value,
        )
        state.accu = state.accu + read_value


class SUB(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="SUB", opcode=4, address=address)

    def behavior(self, state: ToyArchitecturalState):
        """ACCU -= MEM[address]"""
        read_value = state.memory.read_halfword(address=self.address)
        state.visualisation_values = SvgVisValues(
            accu_old=MutableUInt16(int(state.accu)),
            ram_out=read_value,
            alu_out=state.accu - read_value,
        )
        state.accu = state.accu - read_value


class OR(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="OR", opcode=5, address=address)

    def behavior(self, state: ToyArchitecturalState):
        """ACCU |= MEM[address]"""
        read_value = state.memory.read_halfword(address=self.address)
        state.visualisation_values = SvgVisValues(
            accu_old=MutableUInt16(int(state.accu)),
            ram_out=read_value,
            alu_out=state.accu | read_value,
        )
        state.accu = state.accu | read_value


class AND(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="AND", opcode=6, address=address)

    def behavior(self, state: ToyArchitecturalState):
        """ACCU &= MEM[address]"""
        read_value = state.memory.read_halfword(address=self.address)
        state.visualisation_values = SvgVisValues(
            accu_old=MutableUInt16(int(state.accu)),
            ram_out=read_value,
            alu_out=state.accu & read_value,
        )
        state.accu = state.accu & read_value


class XOR(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="XOR", opcode=7, address=address)

    def behavior(self, state: ToyArchitecturalState):
        """ACCU ^= MEM[address]"""
        read_value = state.memory.read_halfword(address=self.address)
        state.visualisation_values = SvgVisValues(
            accu_old=MutableUInt16(int(state.accu)),
            ram_out=read_value,
            alu_out=state.accu ^ read_value,
        )
        state.accu = state.accu ^ read_value


class NOT(ToyInstruction):
    def __init__(self):
        super().__init__(mnemonic="NOT", opcode=8)

    def behavior(self, state: ToyArchitecturalState):
        """ACCU = ~ACCU"""
        state.visualisation_values = SvgVisValues(
            accu_old=MutableUInt16(int(state.accu)), alu_out=~state.accu
        )
        state.accu = ~state.accu


class INC(ToyInstruction):
    def __init__(self):
        super().__init__(mnemonic="INC", opcode=9)

    def behavior(self, state: ToyArchitecturalState):
        """ACCU += 1"""
        state.visualisation_values = SvgVisValues(
            accu_old=MutableUInt16(int(state.accu)),
            alu_out=state.accu + MutableUInt16(1),
        )
        state.accu += MutableUInt16(1)


class DEC(ToyInstruction):
    def __init__(self):
        super().__init__(mnemonic="DEC", opcode=10)

    def behavior(self, state: ToyArchitecturalState):
        """ACCU -= 1"""
        state.visualisation_values = SvgVisValues(
            accu_old=MutableUInt16(int(state.accu)),
            alu_out=state.accu - MutableUInt16(1),
        )
        state.accu -= MutableUInt16(1)


class ZRO(ToyInstruction):
    def __init__(self) -> None:
        super().__init__(mnemonic="ZRO", opcode=11)

    def behavior(self, state: ToyArchitecturalState):
        """ACCU = 0"""
        state.visualisation_values = SvgVisValues(alu_out=MutableUInt16(0))
        state.accu = MutableUInt16(0)


class NOP(ToyInstruction):
    def __init__(self) -> None:
        super().__init__(mnemonic="NOP", opcode=12)

    def behavior(self, state: ToyArchitecturalState):
        """no operation"""
        state.visualisation_values = SvgVisValues()


instruction_map: dict[str, Type[ToyInstruction]] = {
    "STO": STO,
    "LDA": LDA,
    "BRZ": BRZ,
    "ADD": ADD,
    "SUB": SUB,
    "OR": OR,
    "AND": AND,
    "XOR": XOR,
    "NOT": NOT,
    "INC": INC,
    "DEC": DEC,
    "ZRO": ZRO,
    "NOP": NOP,
}
