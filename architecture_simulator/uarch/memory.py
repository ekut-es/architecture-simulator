from dataclasses import dataclass, field
import fixedint


@dataclass
class MemoryAddressError(ValueError):
    address: int
    min_address_incl: int
    max_address_incl: int
    memory_type: str

    def __repr__(self):
        return f"MemoryAddressError: Cannot access {self.memory_type} at address {self.address}: Addresses go from {self.min_address_incl} to {self.max_address_incl}"


@dataclass
class Memory:
    """A byte addressed memory which is designed to store words.
    You can also store bytes and halfwords and you could easily adapt it to work with double words as well.
    There is however only a function for representing the contents as halfwords.
    """

    # Address length in bits. Can be used to limit memory size.
    address_length: int = 32
    # min address (inclusive)
    min_bytes: int = 2**14  # 2**14
    memory_file: dict[int, fixedint.MutableUInt8] = field(default_factory=dict)

    def memory_wordwise_repr(self) -> dict[int, tuple[str, str, str]]:
        """Returns the contents of the memory as binary, decimal and hexadecimal values, all nicely formatted.

        Returns:
            dict[int, tuple[str, str, str]]: keys: addresses. Values: Tuples of (binary, decimal, hexadecimal) strings.
        """
        wordwise_mem: dict[int, tuple[str, str, str]] = dict()
        for address in self.memory_file.keys():
            aligned_address = address - (address % 4)
            if aligned_address in wordwise_mem:
                continue
            word = self.read_word(address=aligned_address)
            bin_word = "{:032b}".format(int(word))
            hex_word = "{:08X}".format(int(word))
            bin_word_with_spaces = (
                bin_word[0:8]
                + " "
                + bin_word[8:16]
                + " "
                + bin_word[16:24]
                + " "
                + bin_word[24:32]
            )
            hex_word_with_spaces = (
                hex_word[0:2]
                + " "
                + hex_word[2:4]
                + " "
                + hex_word[4:6]
                + " "
                + hex_word[6:8]
            )
            wordwise_mem[aligned_address] = (
                bin_word_with_spaces,
                str(word),
                hex_word_with_spaces,
            )
        return wordwise_mem

    def read_byte(self, address: int) -> fixedint.MutableUInt8:
        address_with_overflow = address % pow(2, self.address_length)
        if address_with_overflow < self.min_bytes:
            raise MemoryAddressError(
                address=address_with_overflow,
                min_address_incl=self.min_bytes,
                max_address_incl=(2**self.address_length) - 1,
                memory_type="data memory",
            )
        try:
            addr1 = fixedint.MutableUInt8(int(self.memory_file[address_with_overflow]))
        except KeyError:
            addr1 = fixedint.MutableUInt8(0)
        return addr1

    def write_byte(self, address: int, value: fixedint.MutableUInt8):
        address_with_overflow = address % pow(2, self.address_length)
        if address_with_overflow < self.min_bytes:
            raise MemoryAddressError(
                address=address_with_overflow,
                min_address_incl=self.min_bytes,
                max_address_incl=(2**self.address_length) - 1,
                memory_type="data memory",
            )
        safe_value = fixedint.MutableUInt8(int(value))
        self.memory_file[address_with_overflow] = safe_value

    def read_halfword(self, address: int) -> fixedint.MutableUInt16:
        addr1 = int(self.read_byte(address))
        addr2 = int(self.read_byte(address + 1)) << 8

        return fixedint.MutableUInt16(addr1 | addr2)

    def write_halfword(self, address: int, value: fixedint.MutableUInt16):
        safe_value = fixedint.MutableUInt16(int(value))
        self.write_byte(
            address=address, value=fixedint.MutableUInt8(int(safe_value[0:8]))
        )
        self.write_byte(
            address=address + 1, value=fixedint.MutableUInt8(int(safe_value[8:16]))
        )

    def read_word(self, address: int) -> fixedint.MutableUInt32:
        addr1 = int(self.read_byte(address))
        addr2 = int(self.read_byte(address + 1)) << 8
        addr3 = int(self.read_byte(address + 2)) << 16
        addr4 = int(self.read_byte(address + 3)) << 24
        return fixedint.MutableUInt32(addr4 | addr3 | addr2 | addr1)

    def write_word(self, address: int, value: fixedint.MutableUInt32):
        safe_value = fixedint.MutableUInt32(int(value))
        self.write_byte(
            address=address, value=fixedint.MutableUInt8(int(safe_value[0:8]))
        )
        self.write_byte(
            address=address + 1, value=fixedint.MutableUInt8(int(safe_value[8:16]))
        )
        self.write_byte(
            address=address + 2, value=fixedint.MutableUInt8(int(safe_value[16:24]))
        )
        self.write_byte(
            address=address + 3, value=fixedint.MutableUInt8(int(safe_value[24:32]))
        )
