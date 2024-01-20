from dataclasses import dataclass
from typing import Generic, Optional, Type, TypeVar
from enum import Enum
from fixedint import MutableUInt8, MutableUInt16, MutableUInt32, MutableUInt64
from architecture_simulator.util.integer_representations import (
    get_n_bit_representations,
)


@dataclass
class MemoryAddressError(ValueError):
    address: int
    min_address_incl: int
    max_address_incl: int
    memory_type: str

    def __repr__(self):
        return f"MemoryAddressError: Cannot access {self.memory_type} at address {self.address}: Addresses go from {self.min_address_incl} to {self.max_address_incl}"


@dataclass
class UnsupportedFunctionError(RuntimeError):
    required_addressing_type: str
    used_addressing_type: str

    def __repr__(self) -> str:
        return f"This function requires {self.required_addressing_type}, but this memory uses {self.used_addressing_type}-wise addressing."


class AddressingType(Enum):
    """
    Enum that stores addressing types (byte, half_word, word, double_word) and the corresponding MutableUInt.
    """

    BYTE: Type[MutableUInt8] = MutableUInt8
    HALF_WORD: Type[MutableUInt16] = MutableUInt16
    WORD: Type[MutableUInt32] = MutableUInt32
    DOUBLE_WORD: Type[MutableUInt64] = MutableUInt64


T = TypeVar("T", MutableUInt8, MutableUInt16, MutableUInt32, MutableUInt64)


class Memory(Generic[T]):
    """
    A class representing data memory (using Little-Endian byte-ordering).

    Parameters:
        - addressing_type (AddressingType): The addressing type for memory access (byte, half-word, word, double-word).
        - address_length (int): The length of memory addresses.
        - address_overflow (bool, optional): Flag indicating whether address overflow will be applied before access. Defaults to False.
        - address_range (range, optional): Optional range specifying valid memory addresses. If not specified, defaults to range(2**address_length).
    """

    def __init__(
        self,
        addressing_type: AddressingType,
        address_length: int,
        address_overflow: bool = False,
        address_range: Optional[range] = None,
    ) -> None:
        self.addressing_type = addressing_type
        self.class_of_memory_file_values: Type[T] = addressing_type.value
        self.memory_file_values_width = addressing_type.value.width
        self.address_length: int = address_length
        self.address_overflow = address_overflow
        self.address_range = (
            range(2**self.address_length) if address_range is None else address_range
        )
        self.memory_file: dict[int, T] = dict()

    def reset(self):
        """Clears the memory."""
        self.memory_file = {}

    def assert_address_in_range(self, address: int):
        """
        Asserts that the given address is within the valid memory address range. Raises MemoryAddressError if the address is outside the allowed range.
        """
        if not address in self.address_range:
            raise MemoryAddressError(
                address=address,
                min_address_incl=self.address_range.start,
                max_address_incl=self.address_range.stop - 1,
                memory_type="data memory",
            )

    def _read_value(self, address: int) -> T:
        """
        Reads the value at the specified memory address.

        Parameters:
            address (int): The memory address from which to read.

        Returns:
            T: The value at the given address, where the type (T) depends on the addressing type.
        """
        if self.address_overflow:
            address = address % (2**self.address_length)
        self.assert_address_in_range(address)
        try:
            value = self.class_of_memory_file_values(
                int(self.memory_file[address])
            )  # deep copy
        except KeyError:
            value = self.class_of_memory_file_values(0)
        return value

    def _write_value(self, address: int, value: T) -> None:
        """
        Writes the value at the specified memory address.

        Parameters:
            address (int): The memory address where the value will be written.
            value (T): The value to be written at the given address, where the type (T) depends on the addressing type.
        """
        if self.address_overflow:
            address = address % (2**self.address_length)
        self.assert_address_in_range(address)
        self.memory_file[address] = self.class_of_memory_file_values(
            int(value)
        )  # deep copy

    def _read_multiple(self, address: int, n: int) -> int:
        """
        Reads n consecutive values starting at the specified memory address and combines them into an integer.

        Parameters:
            address (int): The memory address from which to start reading.
            n (int): The number of values to read.

        Returns:
            int: The concatenated read values (Little Endian).
        """
        res = 0
        for i in range(n):
            res = res | (
                int(self._read_value(address + i))
                << (i * self.memory_file_values_width)
            )
        return res

    def _write_multiple(self, address: int, n: int, value: int) -> None:
        """
        Stores the integer value in consecutive memory addresses starting at the specified address (Little Endian).

        Parameters:
            address (int): The memory address from which to start writing.
            n (int): The number of consecutive addresses to write to.
            value (int): The value to be stored.
        """
        for i in range(n):
            self._write_value(
                address + i,
                self.class_of_memory_file_values(
                    value & (2**self.memory_file_values_width - 1)
                ),
            )
            value = value >> self.memory_file_values_width

    def read_byte(self, address: int) -> MutableUInt8:
        """
        Reads the byte at the specified memory address.

        Requires byte-wise addressing; otherwise, raises a UnsupportedFunctionError.

        Parameters:
            address (int): The memory address from which to read.

        Raises:
            UnsupportedFunctionError: If no byte-wise addressing is used.
            MemoryAddressError: If the address is outside the valid memory range.

        Returns:
            MutableUInt8: The value at the given address.
        """
        if self.memory_file_values_width > 8:
            raise UnsupportedFunctionError(
                "byte-wise addressing", self.addressing_type.name
            )
        return MutableUInt8(self._read_multiple(address, 1))

    def read_halfword(self, address: int) -> MutableUInt16:
        """
        Reads the halfword at the specified memory address.

        Requires halfword-wise addressing or smaller; otherwise, raises a UnsupportedFunctionError.

        Parameters:
            address (int): The memory address from which to read.

        Raises:
            UnsupportedFunctionError: If no halfword-wise addressing or smaller is used.
            MemoryAddressError: If the address is outside the valid memory range.

        Returns:
            MutableUInt16: The value at the given address.
        """
        if self.memory_file_values_width > 16:
            raise UnsupportedFunctionError(
                "halfword-wise addressing or smaller", self.addressing_type.name
            )
        return MutableUInt16(
            self._read_multiple(address, 16 // self.memory_file_values_width)
        )

    def read_word(self, address: int) -> MutableUInt32:
        """
        Reads the word at the specified memory address.

        Requires word-wise addressing or smaller; otherwise, raises a UnsupportedFunctionError.

        Parameters:
            address (int): The memory address from which to read.

        Raises:
            UnsupportedFunctionError: If no word-wise addressing or smaller is used.
            MemoryAddressError: If the address is outside the valid memory range.

        Returns:
            MutableUInt32: The value at the given address.
        """
        if self.memory_file_values_width > 32:
            raise UnsupportedFunctionError(
                "word-wise addressing or smaller", self.addressing_type.name
            )
        return MutableUInt32(
            self._read_multiple(address, 32 // self.memory_file_values_width)
        )

    def read_doubleword(self, address: int) -> MutableUInt64:
        """
        Reads the doubleword at the specified memory address.

        Requires doubleword-wise addressing or smaller; otherwise, raises a UnsupportedFunctionError.

        Parameters:
            address (int): The memory address from which to read.

        Raises:
            UnsupportedFunctionError: If no doubleword-wise addressing or smaller is used.
            MemoryAddressError: If the address is outside the valid memory range.

        Returns:
            MutableUInt64: The value at the given address.
        """
        if self.memory_file_values_width > 64:
            raise UnsupportedFunctionError(
                "doubleword-wise addressing or smaller", self.addressing_type.name
            )
        return MutableUInt64(
            self._read_multiple(address, 64 // self.memory_file_values_width)
        )

    def write_byte(self, address: int, value: MutableUInt8) -> None:
        """
        Writes the byte to the specified memory address.

        Requires byte-wise addressing; otherwise, raises a UnsupportedFunctionError.

        Parameters:
            address (int): The memory address to write to.
            value (MutableUInt8): The value to write.

        Raises:
            UnsupportedFunctionError: If no byte-wise addressing is used.
            MemoryAddressError: If the address is outside the valid memory range.
        """
        if self.memory_file_values_width > 8:
            raise UnsupportedFunctionError(
                "byte-wise addressing", self.addressing_type.name
            )
        self._write_multiple(address, 1, int(value))

    def write_halfword(self, address: int, value: MutableUInt16) -> None:
        """
        Writes the halfword to the specified memory address.

        Requires halfword-wise addressing or smaller; otherwise, raises a UnsupportedFunctionError.

        Parameters:
            address (int): The memory address to write to.
            value (MutableUInt16): The value to write.

        Raises:
            UnsupportedFunctionError: If no halfword-wise addressing or smaller is used.
            MemoryAddressError: If the address is outside the valid memory range.
        """
        if self.memory_file_values_width > 16:
            raise UnsupportedFunctionError(
                "halfword-wise addressing or smaller", self.addressing_type.name
            )
        self._write_multiple(address, 16 // self.memory_file_values_width, int(value))

    def write_word(self, address: int, value: MutableUInt32) -> None:
        """
        Writes the word to the specified memory address.

        Requires word-wise addressing or smaller; otherwise, raises a UnsupportedFunctionError.

        Parameters:
            address (int): The memory address to write to.
            value (MutableUInt32): The value to write.

        Raises:
            UnsupportedFunctionError: If no word-wise addressing or smaller is used.
            MemoryAddressError: If the address is outside the valid memory range.
        """
        if self.memory_file_values_width > 32:
            raise UnsupportedFunctionError(
                "word-wise addressing or smaller", self.addressing_type.name
            )
        self._write_multiple(address, 32 // self.memory_file_values_width, int(value))

    def write_doubleword(self, address: int, value: MutableUInt64) -> None:
        """
        Writes the doubleword to the specified memory address.

        Requires doubleword-wise addressing or smaller; otherwise, raises a UnsupportedFunctionError.

        Parameters:
            address (int): The memory address to write to.
            value (MutableUInt64): The value to write.

        Raises:
            UnsupportedFunctionError: If no doubleword-wise addressing or smaller is used.
            MemoryAddressError: If the address is outside the valid memory range.
        """
        if self.memory_file_values_width > 64:
            raise UnsupportedFunctionError(
                "doubleword-wise addressing or smaller", self.addressing_type.name
            )
        self._write_multiple(address, 64 // self.memory_file_values_width, int(value))

    def _memory_repr(
        self, bits_of_one_block: int
    ) -> dict[int, tuple[str, str, str, str]]:
        """
        Returns the contents of the memory as binary, unsigned decimal, hexadecimal, and signed decimal values, all nicely formatted.

        Parameters:
            bits_of_one_block (int): Specifies how many bits long the value at an address should be considered.

         Returns:
            dict[int, tuple[str, str, str, str]]:
                Keys: Memory addresses.
                Values: Tuples of (binary, unsigned decimal, hexadecimal, signed decimal) strings.
        """
        repr_map: dict[int, tuple[str, str, str, str]] = dict()
        num_keys_of_one_block = bits_of_one_block // self.memory_file_values_width
        read_fkt = (
            self.read_byte
            if bits_of_one_block == 8
            else self.read_halfword
            if bits_of_one_block == 16
            else self.read_word
            if bits_of_one_block == 32
            else self.read_doubleword
        )

        for address in self.memory_file.keys():
            aligned_address = address - (address % num_keys_of_one_block)
            if aligned_address in repr_map:
                continue
            word = read_fkt(aligned_address)
            repr_map[aligned_address] = get_n_bit_representations(
                int(word), bits_of_one_block
            )
        return repr_map

    def bytewise_repr(self) -> dict[int, tuple[str, str, str, str]]:
        """
        Returns the contents of the memory (grouped by bytes) as binary, unsigned decimal, hexadecimal, and signed decimal values, all nicely formatted.

        Raises:
            UnsupportedFunctionError: If no byte-wise addressing is used.

         Returns:
            dict[int, tuple[str, str, str, str]]:
                Keys: Memory addresses.
                Values: Tuples of (binary, unsigned decimal, hexadecimal, signed decimal) strings.
        """
        if self.memory_file_values_width > 8:
            raise UnsupportedFunctionError(
                "byte-wise addressing", self.addressing_type.name
            )
        return self._memory_repr(8)

    def half_wordwise_repr(self) -> dict[int, tuple[str, str, str, str]]:
        """
        Returns the contents of the memory (grouped by halfwords) as binary, unsigned decimal, hexadecimal, and signed decimal values, all nicely formatted.

        Raises:
            UnsupportedFunctionError: If no halfword-wise addressing or smaller is used.

         Returns:
            dict[int, tuple[str, str, str, str]]:
                Keys: Memory addresses.
                Values: Tuples of (binary, unsigned decimal, hexadecimal, signed decimal) strings.
        """
        if self.memory_file_values_width > 16:
            raise UnsupportedFunctionError(
                "halfword-wise addressing or smaller", self.addressing_type.name
            )
        return self._memory_repr(16)

    def wordwise_repr(self) -> dict[int, tuple[str, str, str, str]]:
        """
        Returns the contents of the memory (grouped by words) as binary, unsigned decimal, hexadecimal, and signed decimal values, all nicely formatted.

        Raises:
            UnsupportedFunctionError: If no word-wise addressing or smaller is used.

         Returns:
            dict[int, tuple[str, str, str, str]]:
                Keys: Memory addresses.
                Values: Tuples of (binary, unsigned decimal, hexadecimal, signed decimal) strings.
        """
        if self.memory_file_values_width > 32:
            raise UnsupportedFunctionError(
                "word-wise addressing or smaller", self.addressing_type.name
            )
        return self._memory_repr(32)

    def double_wordwise_repr(self) -> dict[int, tuple[str, str, str, str]]:
        """
        Returns the contents of the memory (grouped by doublewords) as binary, unsigned decimal, hexadecimal, and signed decimal values, all nicely formatted.

        Raises:
            UnsupportedFunctionError: If no doubleword-wise addressing or smaller is used.

         Returns:
            dict[int, tuple[str, str, str, str]]:
                Keys: Memory addresses.
                Values: Tuples of (binary, unsigned decimal, hexadecimal, signed decimal) strings.
        """
        if self.memory_file_values_width > 64:
            raise UnsupportedFunctionError(
                "doubleword-wise addressing or smaller", self.addressing_type.name
            )
        return self._memory_repr(64)
