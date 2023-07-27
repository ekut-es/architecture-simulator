from __future__ import annotations
from typing import TYPE_CHECKING
from fixedint import MutableUInt16

from architecture_simulator.uarch.toy.toy_architectural_state import (
    ToyArchitecturalState,
)

if TYPE_CHECKING:
    from architecture_simulator.uarch.toy.toy_architectural_state import (
        ToyArchitecturalState,
    )


class Instruction:
    def __init__(self, mnemonic: str, opcode: int):
        self.mnemonic = mnemonic.upper()
        self.opcode = opcode % 16

    def __repr__(self):
        return self.mnemonic

    def behavior(self, state: ToyArchitecturalState):
        pass


class AddressTypeInstruction(Instruction):
    def __init__(self, mnemonic: str, opcode: int, address: int):
        super().__init__(mnemonic, opcode)
        self.address = address % 4096

    def __repr__(self):
        return f"{self.mnemonic} ${self.address:03x}"


class STO(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="STO", opcode=0, address=address)

    def behavior(self, state: ToyArchitecturalState):
        # NOTE: The Memory class is byte addressed, but the toy architecture uses a halfword addressed memory.
        # Thus, we need to shift the address by one bit
        byte_aligned_address = self.address << 1
        state.data_memory.store_halfword(address=byte_aligned_address, value=state.accu)
        state.program_counter += 1


class LDA(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="LDA", opcode=1, address=address)

    def behavior(self, state: ToyArchitecturalState):
        # NOTE: The Memory class is byte addressed, but the toy architecture uses a halfword addressed memory.
        # Thus, we need to shift the address by one bit
        byte_aligned_address = self.address << 1
        state.accu = state.data_memory.load_halfword(address=byte_aligned_address)
        state.program_counter += 1


class BRZ(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="BRZ", opcode=2, address=address)

    def behavior(self, state: ToyArchitecturalState):
        if state.accu:
            state.program_counter += 1
        else:
            # NOTE: sets the pc to self.address without additionally increasing the program counter.
            # If instructions should ever get saved in a unified memory and are thus editable by other instructions,
            # this needs to change or you need to address this during parsing
            state.program_counter = self.address


class ADD(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="ADD", opcode=3, address=address)

    def behavior(self, state: ToyArchitecturalState):
        byte_aligned_address = self.address << 1
        memory = state.data_memory.load_halfword(address=byte_aligned_address)
        state.accu = state.accu + memory
        state.program_counter += 1


class SUB(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="SUB", opcode=4, address=address)

    def behavior(self, state: ToyArchitecturalState):
        byte_aligned_address = self.address << 1
        memory = state.data_memory.load_halfword(address=byte_aligned_address)
        state.accu = state.accu - memory
        state.program_counter += 1


class OR(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="OR", opcode=5, address=address)

    def behavior(self, state: ToyArchitecturalState):
        byte_aligned_address = self.address << 1
        memory = state.data_memory.load_halfword(address=byte_aligned_address)
        state.accu = state.accu | memory
        state.program_counter += 1


class AND(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="AND", opcode=6, address=address)

    def behavior(self, state: ToyArchitecturalState):
        byte_aligned_address = self.address << 1
        memory = state.data_memory.load_halfword(address=byte_aligned_address)
        state.accu = state.accu & memory
        state.program_counter += 1


class XOR(AddressTypeInstruction):
    def __init__(self, address: int):
        super().__init__(mnemonic="XOR", opcode=7, address=address)

    def behavior(self, state: ToyArchitecturalState):
        byte_aligned_address = self.address << 1
        memory = state.data_memory.load_halfword(address=byte_aligned_address)
        state.accu = state.accu ^ memory
        state.program_counter += 1


class NOT(Instruction):
    def __init__(self):
        super().__init__(mnemonic="NOT", opcode=8)

    def behavior(self, state: ToyArchitecturalState):
        state.accu = ~state.accu
        state.program_counter += 1


class INC(Instruction):
    def __init__(self):
        super().__init__(mnemonic="INC", opcode=9)

    def behavior(self, state: ToyArchitecturalState):
        state.accu += MutableUInt16(1)
        state.program_counter += 1


class DEC(Instruction):
    def __init__(self):
        super().__init__(mnemonic="DEC", opcode=10)


class ZRO(Instruction):
    def __init__(self) -> None:
        super().__init__(mnemonic="ZRO", opcode=11)

    def behavior(self, state: ToyArchitecturalState):
        state.accu = MutableUInt16(0)


class NOP(Instruction):
    def __init__(self) -> None:
        super().__init__(mnemonic="NOP", opcode=12)
