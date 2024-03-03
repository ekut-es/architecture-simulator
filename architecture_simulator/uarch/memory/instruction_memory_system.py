from __future__ import annotations
from typing import TypeVar, Generic
from abc import ABC, abstractmethod

from architecture_simulator.settings.settings import Settings
from architecture_simulator.uarch.memory.memory import MemoryAddressError
from architecture_simulator.isa.instruction import Instruction


T = TypeVar("T", bound=Instruction)


class InstructionMemorySystem(ABC, Generic[T]):
    def __init__(self) -> None:
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
