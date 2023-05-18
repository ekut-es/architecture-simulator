from dataclasses import dataclass
import fixedint


@dataclass
class RegisterFile:
    registers: list[fixedint.MutableUInt32]


@dataclass
class Memory:
    memory_file: dict[int, fixedint.MutableUInt8]

    def load_byte(self, address: int) -> fixedint.MutableUInt8:
        try:
            addr1 = fixedint.MutableUInt8(int(self.memory_file[address % pow(2, 32)]))
        except KeyError:
            addr1 = fixedint.MutableUInt8(0)
        return addr1

    def store_byte(self, address: int, value: fixedint.MutableUInt8):
        safe_value = fixedint.MutableUInt8(int(value))
        self.memory_file[address % pow(2, 32)] = safe_value

    def load_halfword(self, address: int) -> fixedint.MutableUInt16:
        try:
            addr1 = fixedint.MutableUInt16(int(self.memory_file[address % pow(2, 32)]))
        except KeyError:
            addr1 = fixedint.MutableUInt16(0)
        try:
            addr2 = fixedint.MutableUInt16(
                int(self.memory_file[(address + 1) % pow(2, 32)]) << 8
            )
        except KeyError:
            addr2 = fixedint.MutableUInt16(0)

        return addr2 | addr1

    def store_halfword(self, address: int, value: fixedint.MutableUInt16):
        safe_value = fixedint.MutableUInt16(int(value))
        self.memory_file[address % pow(2, 32)] = fixedint.MutableUInt8(
            int(safe_value[0:8])
        )
        self.memory_file[(address + 1) % pow(2, 32)] = fixedint.MutableUInt8(
            int(safe_value[8:16])
        )

    def load_word(self, address: int) -> fixedint.MutableUInt32:
        try:
            addr1 = fixedint.MutableUInt32(int(self.memory_file[address % pow(2, 32)]))
        except KeyError:
            addr1 = fixedint.MutableUInt32(0)
        try:
            addr2 = fixedint.MutableUInt32(
                int(self.memory_file[(address + 1) % pow(2, 32)]) << 8
            )
        except KeyError:
            addr2 = fixedint.MutableUInt32(0)
        try:
            addr3 = fixedint.MutableUInt32(
                int(self.memory_file[(address + 2) % pow(2, 32)]) << 16
            )
        except KeyError:
            addr3 = fixedint.MutableUInt32(0)
        try:
            addr4 = fixedint.MutableUInt32(
                int(self.memory_file[(address + 3) % pow(2, 32)]) << 24
            )
        except KeyError:
            addr4 = fixedint.MutableUInt32(0)
        return addr4 | addr3 | addr2 | addr1

    def store_word(self, address: int, value: fixedint.MutableUInt32):
        safe_value = fixedint.MutableUInt32(int(value))
        self.memory_file[address % pow(2, 32)] = fixedint.MutableUInt8(
            int(safe_value[0:8])
        )
        self.memory_file[(address + 1) % pow(2, 32)] = fixedint.MutableUInt8(
            int(safe_value[8:16])
        )
        self.memory_file[(address + 2) % pow(2, 32)] = fixedint.MutableUInt8(
            int(safe_value[16:24])
        )
        self.memory_file[(address + 3) % pow(2, 32)] = fixedint.MutableUInt8(
            int(safe_value[24:32])
        )


@dataclass
class CsrRegisterFile(Memory):
    privilege_level: int = 0

    def load_byte(self, adress: int) -> fixedint.MutableUInt8:
        self.checkForLegalAdress(adress)
        self.checkPrivilegeLevel(adress)
        return super().load_byte(adress)

    def store_byte(self, adress: int, value: fixedint.MutableUInt8):
        self.checkForLegalAdress(adress)
        self.checkPrivilegeLevel(adress)
        self.checkReadOnly(adress)
        return super().store_byte(adress, value)

    def load_halfword(self, adress: int) -> fixedint.MutableUInt16:
        self.checkForLegalAdress(adress)
        self.checkPrivilegeLevel(adress)
        return super().load_halfword(adress)

    def store_halfword(self, adress: int, value: fixedint.MutableUInt16):
        self.checkForLegalAdress(adress)
        self.checkPrivilegeLevel(adress)
        self.checkReadOnly(adress)
        return super().store_halfword(adress, value)

    def load_word(self, adress: int) -> fixedint.MutableUInt32:
        self.checkForLegalAdress(adress)
        self.checkPrivilegeLevel(adress)
        return super().load_word(adress)

    def store_word(self, adress: int, value: fixedint.MutableUInt32):
        self.checkForLegalAdress(adress)
        self.checkPrivilegeLevel(adress)
        self.checkReadOnly(adress)
        return super().store_word(adress, value)

    def checkPrivilegeLevel(self, adress: int):
        if (adress & 0b001100000000) > self.privilege_level:
            raise Exception(
                "illegal action: privilege level too low to access this csr register"
            )

    def checkForLegalAdress(self, adress: int):
        if adress < 0 or adress > 4095:
            raise Exception("illegal action: csr register does not exist")

    def checkReadOnly(self, adress: int):
        if adress & 0b100000000000 and adress & 0b010000000000:
            raise Exception(
                "illegal action: attempting to write into read-only csr register"
            )


@dataclass
class ArchitecturalState:
    register_file: RegisterFile
    memory: Memory = Memory(memory_file={})
    csr_registers: CsrRegisterFile = CsrRegisterFile(memory_file={})
    program_counter: int = 0

    def changePrivilegeLevel(self, level: int):
        if not level < 0 and not level > 3:
            self.csr_registers.privilege_level = level

    def getPrivilegeLevel(self):
        return self.csr_registers.privilege_level


import json

dic = dict()
l = [{hex(1): "a"}, {2: "b"}]
dic[0] = l
print(dic)
print(json.dumps(dic))
