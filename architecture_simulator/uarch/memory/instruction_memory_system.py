from __future__ import annotations
from typing import TypeVar, Generic, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod

from architecture_simulator.isa.instruction import Instruction

if TYPE_CHECKING:
    from architecture_simulator.uarch.memory.cache import CacheRepr


T = TypeVar("T", bound=Instruction)


class InstructionMemorySystem(ABC, Generic[T]):
    @abstractmethod
    def has_instructions(self) -> bool:
        pass

    @abstractmethod
    def get_address_range(self) -> range:
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def get_representation(self) -> list[tuple[int, str]]:
        pass

    @abstractmethod
    def read_instruction(self, address: int) -> T:
        pass

    @abstractmethod
    def write_instruction(self, address: int, instr: T):
        pass

    @abstractmethod
    def write_instructions(self, instructions: list[T]):
        pass

    @abstractmethod
    def instruction_at_address(self, address: int) -> bool:
        pass

    def get_cache_stats(self) -> Optional[dict[str, str]]:
        return None

    def cache_repr(self) -> Optional[CacheRepr]:
        return None
