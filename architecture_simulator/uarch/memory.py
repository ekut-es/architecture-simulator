from dataclasses import dataclass, field
import fixedint
from architecture_simulator.isa.parser import RiscvParser


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
    # Address length in bits. Can be used to limit memory size.
    address_length: int = 32
    # min address (inclusive)
    min_bytes: int = 2**14  # 2**14
    memory_file: dict[int, fixedint.MutableUInt8] = field(default_factory=dict)

    def memory_wordwise_repr(self) -> dict[int, tuple]:
        wordwise_mem: dict[int, tuple] = dict()
        number_of_bytes = self.address_length / 8
        for address in self.memory_file.keys():
            if address % number_of_bytes == 0:
                word = self.load_word(address=address)
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
                wordwise_mem[address] = (
                    bin_word_with_spaces,
                    int(word),
                    hex_word_with_spaces,
                )
            elif address % number_of_bytes == 1:
                word = self.load_word(address=address - 1)
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
                wordwise_mem[address - 1] = (
                    bin_word_with_spaces,
                    int(word),
                    hex_word_with_spaces,
                )
            elif address % number_of_bytes == 2:
                word = self.load_word(address=address - 2)
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
                wordwise_mem[address - 2] = (
                    bin_word_with_spaces,
                    int(word),
                    hex_word_with_spaces,
                )
            elif address % number_of_bytes == 3:
                word = self.load_word(address=address - 3)
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
                wordwise_mem[address - 3] = (
                    bin_word_with_spaces,
                    int(word),
                    hex_word_with_spaces,
                )
        return wordwise_mem

    def load_byte(self, address: int) -> fixedint.MutableUInt8:
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

    def store_byte(self, address: int, value: fixedint.MutableUInt8):
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

    def load_halfword(self, address: int) -> fixedint.MutableUInt16:
        addr1 = int(self.load_byte(address))
        addr2 = int(self.load_byte(address + 1)) << 8

        return fixedint.MutableUInt16(addr1 | addr2)

    def store_halfword(self, address: int, value: fixedint.MutableUInt16):
        safe_value = fixedint.MutableUInt16(int(value))
        self.store_byte(
            address=address, value=fixedint.MutableUInt8(int(safe_value[0:8]))
        )
        self.store_byte(
            address=address + 1, value=fixedint.MutableUInt8(int(safe_value[8:16]))
        )

    def load_word(self, address: int) -> fixedint.MutableUInt32:
        addr1 = int(self.load_byte(address))
        addr2 = int(self.load_byte(address + 1)) << 8
        addr3 = int(self.load_byte(address + 2)) << 16
        addr4 = int(self.load_byte(address + 3)) << 24
        return fixedint.MutableUInt32(addr4 | addr3 | addr2 | addr1)

    def store_word(self, address: int, value: fixedint.MutableUInt32):
        safe_value = fixedint.MutableUInt32(int(value))
        self.store_byte(
            address=address, value=fixedint.MutableUInt8(int(safe_value[0:8]))
        )
        self.store_byte(
            address=address + 1, value=fixedint.MutableUInt8(int(safe_value[8:16]))
        )
        self.store_byte(
            address=address + 2, value=fixedint.MutableUInt8(int(safe_value[16:24]))
        )
        self.store_byte(
            address=address + 3, value=fixedint.MutableUInt8(int(safe_value[24:32]))
        )


class CsrRegisterFile(Memory):
    def __init__(self, privilege_level: int = 0, min_bytes: int = 0):
        super().__init__()
        self.privilege_level = privilege_level
        self.min_bytes = min_bytes

    def load_byte(self, address: int) -> fixedint.MutableUInt8:
        self.check_for_legal_address(address)
        self.check_privilege_level(address)
        return super().load_byte(address)

    def store_byte(self, address: int, value: fixedint.MutableUInt8):
        self.check_for_legal_address(address)
        self.check_privilege_level(address)
        self.check_read_only(address)
        return super().store_byte(address, value)

    def load_halfword(self, address: int) -> fixedint.MutableUInt16:
        self.check_for_legal_address(address)
        self.check_privilege_level(address)
        return super().load_halfword(address)

    def store_halfword(self, address: int, value: fixedint.MutableUInt16):
        self.check_for_legal_address(address)
        self.check_privilege_level(address)
        self.check_read_only(address)
        return super().store_halfword(address, value)

    def load_word(self, address: int) -> fixedint.MutableUInt32:
        self.check_for_legal_address(address)
        self.check_privilege_level(address)
        return super().load_word(address)

    def store_word(self, address: int, value: fixedint.MutableUInt32):
        self.check_for_legal_address(address)
        self.check_privilege_level(address)
        self.check_read_only(address)
        return super().store_word(address, value)

    def check_privilege_level(self, address: int):
        if (address & 0b001100000000) > self.privilege_level:
            raise CSRError(
                "illegal action: privilege level too low to access this csr register"
            )

    def check_for_legal_address(self, address: int):
        if address < 0 or address > 4095:
            raise CSRError("illegal action: csr register does not exist")

    def check_read_only(self, address: int):
        if address & 0b100000000000 and address & 0b010000000000:
            raise CSRError(
                "illegal action: attempting to write into read-only csr register"
            )


@dataclass
class CSRError(ValueError):
    message: str

    def __repr__(self):
        return self.message


@dataclass
class InstructionMemory:
    instructions: dict = field(default_factory=dict)

    # max address (exclusive)
    max_bytes: int = 2**14

    def save_instruction(self, address: int, instr):
        if address < 0:
            raise MemoryAddressError(
                address=address,
                min_address_incl=0,
                max_address_incl=self.max_bytes - 1,
                memory_type="instruction memory",
            )
        elif (address + instr.length - 1) >= self.max_bytes:
            raise MemoryAddressError(
                address=(address + instr.length - 1),
                min_address_incl=0,
                max_address_incl=self.max_bytes - 1,
                memory_type="instruction memory",
            )
        else:
            self.instructions[address] = instr

    def load_instruction(self, address):
        return self.instructions[address]

    def append_instructions(self, program: str):
        if self.instructions:
            last_address = max(self.instructions.keys())
            next_address = last_address + self.instructions[last_address].length
        else:
            next_address = 0
        parser: RiscvParser = RiscvParser()
        for instr in parser.parse(program, start_address=0):
            self.save_instruction(next_address, instr=instr)
            next_address += instr.length
