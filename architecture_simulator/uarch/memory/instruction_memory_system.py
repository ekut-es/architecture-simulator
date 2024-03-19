from __future__ import annotations
from typing import TypeVar, Generic, Optional, TYPE_CHECKING, Any
from abc import ABC, abstractmethod

from architecture_simulator.isa.instruction import Instruction

if TYPE_CHECKING:
    from architecture_simulator.uarch.memory.cache import CacheRepr


T = TypeVar("T", bound=Instruction)


class InstructionMemorySystem(ABC, Generic[T]):
    @abstractmethod
    def has_instructions(self) -> bool:
        """Abstract method checking if any instructions are stored.

        Returns:
            bool: whether there are instructions stored in the memory.
        """

    @abstractmethod
    def get_address_range(self) -> range:
        """Abstract method for returning valid address range.

        Returns:
            range: range of valid addresses
        """

    @abstractmethod
    def reset(self):
        """Abstract method for clearing the memory system."""

    @abstractmethod
    def get_representation(self) -> list[tuple[int, str]]:
        """Abstract method for returning a list of string representations for all instructions and their address. Sorted by address.

        Returns:
            list[tuple[int, str]]: Each element is a tuple of the address and the string representaiton of the instruction.
        """

    @abstractmethod
    def read_instruction(self, address: int) -> T:
        """Abstract method for reading an instruction.

        Args:
            address (int): Address to load the instruction from.

        Raises:
            InstructionMemoryKeyError: An error if there is no instruction at the provided address.

        Returns:
            T: The instruction saved at the given address.
        """

    @abstractmethod
    def write_instruction(self, address: int, instr: T):
        """Abstract method for storing a single instruction at a given address.

        Args:
            address (int): Address at which to store the instruction.
            instr (T): The instruction to be stored.
        """

    @abstractmethod
    def write_instructions(self, instructions: list[T]):
        """Abstract method for clearing the memory and store given instructions, starting at the first valid address.

        Args:
            instructions (list[Instruction]): Instructions to be stored.
        """

    @abstractmethod
    def instruction_at_address(self, address: int) -> bool:
        """Abstract method to return whether there is an instruction at the given address.

        Args:
            address (int): address to check

        Returns:
            bool: Whether there is an instruction at the given address.
        """

    def get_cache_stats(self) -> Optional[dict[str, Any]]:
        """
        Subclasses implementing a cache can override this method to provide statistics,
        such as hits and accesses, as a dictionary.

        Returns:
            Optional[dict[str, Any]]: A dictionary containing cache statistics, or None if not overridden.
        """
        return None

    def cache_repr(self) -> Optional[CacheRepr]:
        """
        Subclasses implementing a cache can override this method to provide cache representation.

        Returns:
            Optional[CacheRepr]: An object used to visualize the cache content, or None if not overridden.
        """
        return None
