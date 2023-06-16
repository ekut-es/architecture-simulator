from dataclasses import dataclass, field
import fixedint
import time


@dataclass
class PerformanceMetrics:
    execution_time_s: float = -1
    instruction_count: int = 0
    instructions_per_second: float = -1
    branch_count: int = 0
    procedure_count: int = 0
    start: float = -1

    def start_timer(self):
        self.start = time.time()

    def stop_timer(self):
        self.execution_time_s = time.time() - self.start
        self.instructions_per_second = (
            (self.instruction_count / self.execution_time_s)
            if self.execution_time_s
            else 0
        )


class Registers(list):
    """
    Custom list, that overwrites [], so that register x0 gets hardwired to zero.
    """

    def __getitem__(self, index):
        # access of x0 will alway return zero, since x0 get´s initialized as zero and can not be changed
        # index out of bounds error will be thrown if trying to acces a register outside of x0 to x31
        return super().__getitem__(index)

    def __setitem__(self, index, value):
        # ensures, that register x0 stays 0 and that there are only 32 registers
        if index > 0 and index < 32:
            super().__setitem__(index, value)


@dataclass
class RegisterFile:
    """
    This class implements the register file.

    Args:
        registers:
            list[int / fixedint.MutableUInt32] => provided list will be used to init registers, x0 can have any value (test mode)

            no_arg => 32 registers with x0 is hard wired to zero
    """

    registers: list[fixedint.MutableUInt32] = field(
        default_factory=lambda: Registers([fixedint.MutableUInt32(0)] * 32)
    )


@dataclass
class Memory:
    # Address length in bits. Can be used to limit memory size.
    address_length: int = 32
    # min address (inclusive)
    min_bytes: int = 2**14
    memory_file: dict[int, fixedint.MutableUInt8] = field(default_factory=dict)

    def load_byte(self, address: int) -> fixedint.MutableUInt8:
        address_with_overflow = address % pow(2, self.address_length)
        if address_with_overflow < self.min_bytes:
            raise ValueError("You can not access the instruction memory this way.")
        try:
            addr1 = fixedint.MutableUInt8(int(self.memory_file[address_with_overflow]))
        except KeyError:
            addr1 = fixedint.MutableUInt8(0)
        return addr1

    def store_byte(self, address: int, value: fixedint.MutableUInt8):
        address_with_overflow = address % pow(2, self.address_length)
        if address_with_overflow < self.min_bytes:
            raise ValueError("You can not access the instruction memory this way.")
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
            raise Exception(
                "illegal action: privilege level too low to access this csr register"
            )

    def check_for_legal_address(self, address: int):
        if address < 0 or address > 4095:
            raise Exception("illegal action: csr register does not exist")

    def check_read_only(self, address: int):
        if address & 0b100000000000 and address & 0b010000000000:
            raise Exception(
                "illegal action: attempting to write into read-only csr register"
            )


@dataclass
class InstructionMemory:
    instructions: dict = field(default_factory=dict)

    # max address (exclusive)
    max_bytes: int = 2**14

    def save_instruction(self, address: int, instr):
        if address >= 0 and (address + instr.length - 1) < self.max_bytes:
            self.instructions[address] = instr
        else:
            # TODO: Custom exceptions
            raise ValueError("Incorrect address")

    def load_instruction(self, address):
        return self.instructions[address]

    def append_instructions(self, program: str):
        from ..isa.parser import RiscvParser

        if self.instructions:
            last_address = max(self.instructions.keys())
            next_address = last_address + self.instructions[last_address].length
        else:
            next_address = 0
        parser: RiscvParser = RiscvParser()
        for instr in parser.parse(program, start_address=0):
            self.save_instruction(next_address, instr=instr)
            next_address += instr.length


@dataclass
class ArchitecturalState:
    instruction_memory: InstructionMemory = field(default_factory=InstructionMemory)
    register_file: RegisterFile = field(default_factory=RegisterFile)
    memory: Memory = field(default_factory=Memory)
    csr_registers: CsrRegisterFile = field(default_factory=CsrRegisterFile)
    program_counter: int = 0
    performance_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)

    def change_privilege_level(self, level: int):
        if not level < 0 and not level > 3:
            self.csr_registers.privilege_level = level

    def get_privilege_level(self):
        return self.csr_registers.privilege_level
