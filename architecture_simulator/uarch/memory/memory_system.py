from __future__ import annotations
from abc import ABC, abstractmethod

from fixedint import UInt32, UInt16, UInt8


class MemorySystem(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def read_byte(self, address: int, update_statistics: bool = True) -> UInt8:
        raise NotImplementedError

    @abstractmethod
    def read_halfword(self, address: int, update_statistics: bool = True) -> UInt16:
        raise NotImplementedError

    @abstractmethod
    def read_word(self, address: int, update_statistics: bool = True) -> UInt32:
        raise NotImplementedError

    @abstractmethod
    def write_byte(self, address: int, value: UInt8) -> None:
        raise NotImplementedError

    @abstractmethod
    def write_halfword(self, address: int, value: UInt16) -> None:
        raise NotImplementedError

    @abstractmethod
    def write_word(self, address: int, value: UInt32) -> None:
        raise NotImplementedError

    # @abstractmethod
    # def get_stats_repr(self)-> dict[str, str]:
    #     raise NotImplementedError
