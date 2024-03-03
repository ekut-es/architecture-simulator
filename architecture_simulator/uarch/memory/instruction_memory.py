from __future__ import annotations
from typing import TypeVar, Generic
from dataclasses import dataclass, field

from architecture_simulator.settings.settings import Settings
from architecture_simulator.isa.instruction import Instruction
from architecture_simulator.uarch.memory.memory import MemoryAddressError
from architecture_simulator.uarch.memory.instruction_memory_system import (
    InstructionMemorySystem,
)


T = TypeVar("T", bound=Instruction)


@dataclass
class InstructionMemory(InstructionMemorySystem, Generic[T]):
    """A Generic instruction memory class. Can store instructions from different ISAs,
    as long as their instructions are based on the 'Instruction' class.

    Args:
        Generic (Instruction): The base class for the instructions from some specific ISA.
    """

    instructions: dict[int, T] = field(default_factory=dict)
    address_range: range = field(
        default_factory=lambda: range(
            Settings().get()["instruction_memory_min_bytes"],
            Settings().get()["instruction_memory_max_bytes"],
        )
    )

    def reset(self):
        """Clears the instruction memory."""
        self.instructions = {}

    def get_representation(self) -> list[tuple[int, str]]:
        """Returns a list of string representations for all instructions and their address. Sorted by address.

        Returns:
            list[tuple[int, str]]: Each element is a tuple of the address and the string representaiton of the instruction.
        """
        return [
            (address, str(instr))
            for address, instr in sorted(
                self.instructions.items(), key=lambda el: el[0]
            )
        ]

    def read_instruction(self, address: int) -> T:
        """Load instruction from given address.

        Args:
            address (int): Address to load the instruction from.

        Raises:
            InstructionMemoryKeyError: An error if there is no instruction at the provided address.

        Returns:
            T: The instruction saved at the given address.
        """
        self._assert_address_in_range(address)
        try:
            return self.instructions[address]
        except KeyError:
            raise InstructionMemoryKeyError(address)

    def write_instruction(self, address: int, instr: T):
        """Store a single instruction at given address.

        Args:
            address (int): Address at which to store the instruction.
            instr (T): The instruction to be stored.
        """
        self._assert_address_in_range(address)
        self._assert_address_in_range(address + instr.length - 1)
        self.instructions[address] = instr

    def write_instructions(self, instructions: list[T]):
        """Clear the instruction memory and store given instructions, starting at the first valid address.

        Args:
            instructions (list[Instruction]): Instructions to be stored.
        """
        self.instructions = {}
        next_address = self.address_range.start
        for instr in instructions:
            self.write_instruction(next_address, instr=instr)
            next_address += instr.length

    def _assert_address_in_range(self, address: int):
        """Raises an error if the address is not inside the valid range.

        Args:
            address (int): address to be checked

        Raises:
            MemoryAddressError: An error to indicate that the address was invalid.
        """
        if not address in self.address_range:
            raise MemoryAddressError(
                address=address,
                min_address_incl=self.address_range.start,
                max_address_incl=self.address_range.stop - 1,
                memory_type="instruction memory",
            )

    def instruction_at_address(self, address: int) -> bool:
        """Return whether there is an instruction at the given address.

        Args:
            address (int): address to check

        Returns:
            bool: Whether there is an instruction at the given address.
        """
        return address in self.instructions


@dataclass
class InstructionMemoryKeyError(KeyError):
    address: int

    def __repr__(self):
        return f"Error: No instruction at address {self.address}"
