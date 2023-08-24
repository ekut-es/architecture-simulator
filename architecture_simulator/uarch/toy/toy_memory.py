from dataclasses import dataclass, field
from fixedint import MutableUInt16

from architecture_simulator.settings.settings import Settings
from ..memory import MemoryAddressError


@dataclass
class ToyMemory:
    """A halfword addressed memory designed only for reading and writing halfwords.
    You may rename this if you find any other architecture which uses a 16bit Memory.
    """

    memory_file: dict[int, MutableUInt16] = field(default_factory=dict)
    address_range: range = field(
        default_factory=lambda: range(
            Settings().get()["toy_memory_min_bytes"],
            Settings().get()["toy_memory_max_bytes"],
        )
    )

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
            return MutableUInt16(int(self.memory_file[address]))
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

    def memory_repr(self) -> dict[int, tuple[str, str, str, str]]:
        """Returns the contents of the memory as binary, decimal and hexadecimal values, all nicely formatted.

        Returns:
            dict[int, tuple[str,str,str,str]]: keys: addresses. Values: Tuples of (binary, unsigned decimal, hexadecimal, signed decimal) strings.
        """
        res: dict[int, tuple[str, str, str, str]] = {}
        for key in self.memory_file.keys():
            word = self.memory_file[key]
            unsigned_decimal = int(word)
            signed_decimal = (
                unsigned_decimal - 2**16
                if unsigned_decimal >= 2**15
                else unsigned_decimal
            )
            bin = "{:016b}".format(int(word))
            hex = "{:04X}".format(int(word))
            res[key] = (
                bin[0:8] + " " + bin[8:16],
                str(unsigned_decimal),
                hex[0:2] + " " + hex[2:4],
                str(signed_decimal),
            )
        return res
