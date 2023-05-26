import fixedint
import time


class PerformanceMetrics:
    def __init__(self) -> None:
        self.execution_time_s: float = -1
        self.instruction_count: int = 0
        self.instructions_per_second: float = -1
        self.branch_count: int = 0
        self.procedure_count: int = 0
        self.start: float = -1

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, index):
        # access of x0 will alway return zero, since x0 get´s initialized as zero and can not be changed
        # index out of bounds error will be thrown if trying to acces a register outside of x0 to x31
        return super().__getitem__(index)

    def __setitem__(self, index, value):
        # ensures, that register x0 stays 0 and that there are only 32 registers
        if index > 0 and index < 32:
            super().__setitem__(index, value)


class RegisterFile:
    """
    This class implements the register file.

    Args:
        registers:
            list[int / fixedint.MutableUInt32] => provided list will be used to init registers, x0 can have any value (test mode)

            no_arg => 32 registers with x0 is hard wired to zero
    """

    def __init__(self, registers=None) -> None:
        # initializes 32 registers with x0 hard wired to zero or uses the given registers
        self.registers: list[fixedint.MutableUInt32] = (
            Registers([fixedint.MutableUInt32(0)] * 32)
            if registers == None
            else registers
        )


class Memory:
    def __init__(self, length: int = 32, memory_file=None) -> None:
        self.length: int = length
        self.memory_file: dict[int, fixedint.MutableUInt8] = (
            {} if memory_file == None else memory_file
        )

    def load_byte(self, address: int) -> fixedint.MutableUInt8:
        try:
            addr1 = fixedint.MutableUInt8(
                int(self.memory_file[address % pow(2, self.length)])
            )
        except KeyError:
            addr1 = fixedint.MutableUInt8(0)
        return addr1

    def store_byte(self, address: int, value: fixedint.MutableUInt8):
        safe_value = fixedint.MutableUInt8(int(value))
        self.memory_file[address % pow(2, self.length)] = safe_value

    def load_halfword(self, address: int) -> fixedint.MutableUInt16:
        try:
            addr1 = fixedint.MutableUInt16(
                int(self.memory_file[address % pow(2, self.length)])
            )
        except KeyError:
            addr1 = fixedint.MutableUInt16(0)
        try:
            addr2 = fixedint.MutableUInt16(
                int(self.memory_file[(address + 1) % pow(2, self.length)]) << 8
            )
        except KeyError:
            addr2 = fixedint.MutableUInt16(0)

        return addr2 | addr1

    def store_halfword(self, address: int, value: fixedint.MutableUInt16):
        safe_value = fixedint.MutableUInt16(int(value))
        self.memory_file[address % pow(2, self.length)] = fixedint.MutableUInt8(
            int(safe_value[0:8])
        )
        self.memory_file[(address + 1) % pow(2, self.length)] = fixedint.MutableUInt8(
            int(safe_value[8:16])
        )

    def load_word(self, address: int) -> fixedint.MutableUInt32:
        try:
            addr1 = fixedint.MutableUInt32(
                int(self.memory_file[address % pow(2, self.length)])
            )
        except KeyError:
            addr1 = fixedint.MutableUInt32(0)
        try:
            addr2 = fixedint.MutableUInt32(
                int(self.memory_file[(address + 1) % pow(2, self.length)]) << 8
            )
        except KeyError:
            addr2 = fixedint.MutableUInt32(0)
        try:
            addr3 = fixedint.MutableUInt32(
                int(self.memory_file[(address + 2) % pow(2, self.length)]) << 16
            )
        except KeyError:
            addr3 = fixedint.MutableUInt32(0)
        try:
            addr4 = fixedint.MutableUInt32(
                int(self.memory_file[(address + 3) % pow(2, self.length)]) << 24
            )
        except KeyError:
            addr4 = fixedint.MutableUInt32(0)
        return addr4 | addr3 | addr2 | addr1

    def store_word(self, address: int, value: fixedint.MutableUInt32):
        safe_value = fixedint.MutableUInt32(int(value))
        self.memory_file[address % pow(2, self.length)] = fixedint.MutableUInt8(
            int(safe_value[0:8])
        )
        self.memory_file[(address + 1) % pow(2, self.length)] = fixedint.MutableUInt8(
            int(safe_value[8:16])
        )
        self.memory_file[(address + 2) % pow(2, self.length)] = fixedint.MutableUInt8(
            int(safe_value[16:24])
        )
        self.memory_file[(address + 3) % pow(2, self.length)] = fixedint.MutableUInt8(
            int(safe_value[24:32])
        )


class CsrRegisterFile(Memory):
    def __init__(
        self, memory_file=None, privelege_level: int = 0, length: int = 32
    ) -> None:
        super().__init__(memory_file=memory_file, length=length)
        self.privilege_level: int = privelege_level

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


class ArchitecturalState:
    def __init__(
        self,
        register_file=None,
        memory=None,
        csr_registers=None,
        program_counter: int = 0,
        performance_metrics=None,
    ) -> None:
        self.register_file: RegisterFile = (
            RegisterFile() if register_file == None else register_file
        )
        self.memory: Memory = Memory() if memory == None else memory
        self.csr_registers: CsrRegisterFile = (
            CsrRegisterFile() if csr_registers == None else csr_registers
        )
        self.program_counter: int = program_counter
        self.performance_metrics: PerformanceMetrics = (
            PerformanceMetrics() if performance_metrics == None else performance_metrics
        )

    def change_privilege_level(self, level: int):
        if not level < 0 and not level > 3:
            self.csr_registers.privilege_level = level

    def get_privilege_level(self):
        return self.csr_registers.privilege_level
