from dataclasses import dataclass, field
from fixedint import MutableUInt16

from ..memory import MemoryAddressError


@dataclass
class ToyMemory:
    """A halfword addressed memory designed only for reading and writing halfwords.
    You may rename this if you find any other architecture which uses a 16bit Memory.
    """

    memory_file: dict[int, MutableUInt16] = field(default_factory=dict)
    address_range: range = field(default_factory=lambda: range(1024, 4096))

    def write_halfword(self, address: int, value: MutableUInt16):
        """Store given value at given address.

        Args:
            address (int): Address at which to store the value.
            value (MutableUInt16): The value (a halfword) to be stored.
        """
        self.assert_address_in_range(address)
        # casting is there to create a copy
        self.memory_file[address] = MutableUInt16(int(value))

    def read_halfword(self, address: int) -> MutableUInt16:
        """Load value from given address. Default is 0 if the address hasn't been written to yet.

        Args:
            address (int): Address from which to load the value.

        Returns:
            MutableUInt16: Value stored at given address.
        """
        self.assert_address_in_range(address)
        try:
            return self.memory_file[address]
        except KeyError:
            return MutableUInt16(0)

    def assert_address_in_range(self, address: int):
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
                memory_type="data memory",
            )

    def get_entries(self) -> dict[int, tuple]:
        """Returns the contents of the memory as binary, decimal and hexadecimal numbers.

        Returns:
            dict[int, tuple]: keys: Addresses. Values: tuples of (binary, decimal, hexadecimal) strings.
        """
        entries: dict[int, tuple] = {}
        for address, value in self.memory_file.items():
            bin_value = "{:019_b}".format(int(value)).replace("_", " ")
            dec_value = str(int(value))
            hex_value = "{:04X}".format(int(value))
            entries[address] = bin_value, dec_value, hex_value
        return entries
