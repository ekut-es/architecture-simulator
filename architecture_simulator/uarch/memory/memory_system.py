from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Any
from fixedint import UInt32, UInt16, UInt8

if TYPE_CHECKING:
    from architecture_simulator.uarch.memory.cache import CacheRepr


class MemorySystem(ABC):
    """
    An abstract class that needs to be implemented if a class is to be used as a data memory in RiscvArchitecturalState.
    """

    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_address_range(self) -> range:
        """
        Abstract method that returns the valid address range of the memory.
        """
        raise NotImplementedError

    @abstractmethod
    def read_byte(self, address: int, update_statistics: bool = True) -> UInt8:
        """
        Abstract method for reading a byte from memory.

        Args:
            address (int): The memory address to read from.
            update_statistics (bool, optional): Whether to update memory statistics.
            Defaults to True.

        Returns:
            UInt8: The byte read from memory.
        """
        raise NotImplementedError

    @abstractmethod
    def read_halfword(self, address: int, update_statistics: bool = True) -> UInt16:
        """
        Abstract method for reading a halfword from memory.

        Args:
            address (int): The memory address to read from.
            update_statistics (bool, optional): Whether to update memory statistics.
            Defaults to True.

        Returns:
            UInt16: The halfword read from memory.
        """
        raise NotImplementedError

    @abstractmethod
    def read_word(self, address: int, update_statistics: bool = True) -> UInt32:
        """
        Abstract method for reading a word from memory.

        Args:
            address (int): The memory address to read from.
            update_statistics (bool, optional): Whether to update memory statistics.
            Defaults to True.

        Returns:
            UInt32: The word read from memory.
        """
        raise NotImplementedError

    @abstractmethod
    def write_byte(
        self, address: int, value: UInt8, directly_write_to_lower_memory: bool = False
    ) -> None:
        """
        Abstract method for writing a byte to memory.

        Args:
            address (int): The memory address to write to.
            value (UInt8): The byte value to write.
            directly_write_to_lower_memory (bool, optional): Whether to bypass caches and statistics
            and directly write to lower memory. Defaults to False.
        """
        raise NotImplementedError

    @abstractmethod
    def write_halfword(
        self, address: int, value: UInt16, directly_write_to_lower_memory: bool = False
    ) -> None:
        """
        Abstract method for writing a halfword to memory.

        Args:
            address (int): The memory address to write to.
            value (UInt8): The halfword value to write.
            directly_write_to_lower_memory (bool, optional): Whether to bypass caches and statistics
            and directly write to lower memory. Defaults to False.
        """
        raise NotImplementedError

    @abstractmethod
    def write_word(
        self, address: int, value: UInt32, directly_write_to_lower_memory: bool = False
    ) -> None:
        """
        Abstract method for writing a word to memory.

        Args:
            address (int): The memory address to write to.
            value (UInt8): The word value to write.
            directly_write_to_lower_memory (bool, optional): Whether to bypass caches and statistics
            and directly write to lower memory. Defaults to False.
        """
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """
        Abstract method for clearing data and statistics.
        """
        raise NotImplementedError

    @abstractmethod
    def wordwise_repr(self) -> dict[int, tuple[str, str, str, str]]:
        """
        Abstract method that returns the contents of the memory (grouped by words)
        as binary, unsigned decimal, hexadecimal, and signed decimal values, all nicely formatted.

         Returns:
            dict[int, tuple[str, str, str, str]]:
                Keys: Memory addresses.
                Values: Tuples of (binary, unsigned decimal, hexadecimal, signed decimal) strings.
        """
        raise NotImplementedError

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
