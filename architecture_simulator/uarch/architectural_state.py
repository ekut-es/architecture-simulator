from dataclasses import dataclass
import fixedint


@dataclass
class RegisterFile:
    registers: list[fixedint.MutableUInt32]


@dataclass
class Memory:
    memory_file: dict[int, fixedint.MutableUInt8]

    def load_byte(self, address: int) -> fixedint.MutableUInt8:
        return self.memory_file[address % pow(2, 32)]

    def store_byte(self, address: int, value: fixedint.MutableUInt8):
        self.memory_file[address % pow(2, 32)] = value

    def load_halfword(self, address: int) -> fixedint.MutableUInt16:
        return (
            fixedint.MutableUInt16(
                int(self.memory_file[(address + 1) % pow(2, 32)]) << 8
            )
            | self.memory_file[address % pow(2, 32)]
        )

    def store_halfword(self, address: int, value: fixedint.MutableUInt16):
        self.memory_file[address % pow(2, 32)] = fixedint.MutableUInt8(int(value[0:8]))
        self.memory_file[(address + 1) % pow(2, 32)] = fixedint.MutableUInt8(
            int(value[8:16])
        )

    def load_word(self, address: int) -> fixedint.MutableUInt32:
        return (
            fixedint.MutableUInt32(
                int(self.memory_file[(address + 3) % pow(2, 32)]) << 24
            )
            | fixedint.MutableUInt32(
                int(self.memory_file[(address + 2) % pow(2, 32)]) << 16
            )
            | fixedint.MutableUInt32(
                int(self.memory_file[(address + 1) % pow(2, 32)]) << 8
            )
            | fixedint.MutableUInt32(int(self.memory_file[address % pow(2, 32)]))
        )

    def store_word(self, address: int, value: fixedint.MutableUInt32):
        self.memory_file[address % pow(2, 32)] = fixedint.MutableUInt8(int(value[0:8]))
        self.memory_file[(address + 1) % pow(2, 32)] = fixedint.MutableUInt8(
            int(value[8:16])
        )
        self.memory_file[(address + 2) % pow(2, 32)] = fixedint.MutableUInt8(
            int(value[16:24])
        )
        self.memory_file[(address + 3) % pow(2, 32)] = fixedint.MutableUInt8(
            int(value[24:32])
        )


@dataclass
class ArchitecturalState:
    register_file: RegisterFile
    memory: Memory
    program_counter: int = 0
