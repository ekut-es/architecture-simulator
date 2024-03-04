from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from fixedint import UInt32, UInt16, UInt8

if TYPE_CHECKING:
    from architecture_simulator.uarch.memory.cache import CacheRepr


class MemorySystem(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_address_range(self) -> range:
        raise NotImplementedError

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

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def wordwise_repr(self) -> dict[int, tuple[str, str, str, str]]:
        raise NotImplementedError

    def get_cache_stats(self) -> Optional[dict[str, str]]:
        return None

    def cache_repr(self) -> Optional[CacheRepr]:
        return None
