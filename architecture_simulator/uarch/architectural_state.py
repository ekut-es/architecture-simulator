from dataclasses import dataclass
import fixedint


@dataclass
class RegisterFile:
    registers: list[fixedint.MutableUInt32]


@dataclass
class Memory:
    memory_file: dict[int, fixedint.MutableUInt8]

    def load_byte(self, adress: int) -> fixedint.MutableUInt8:
        self.preventMissingAdress(adress)
        return self.memory_file[adress % pow(2, 32)]

    def store_byte(self, adress: int, value: fixedint.MutableUInt8):
        self.memory_file[adress % pow(2, 32)] = value

    def load_halfword(self, adress: int) -> fixedint.MutableUInt16:
        self.preventMissingAdress(adress)
        return (
            fixedint.MutableUInt16(
                int(self.memory_file[(adress + 1) % pow(2, 32)]) << 8
            )
            | self.memory_file[adress % pow(2, 32)]
        )

    def store_halfword(self, adress: int, value: fixedint.MutableUInt16):
        self.memory_file[adress % pow(2, 32)] = fixedint.MutableUInt8(int(value[0:8]))
        self.memory_file[(adress + 1) % pow(2, 32)] = fixedint.MutableUInt8(
            int(value[8:16])
        )

    def load_word(self, adress: int) -> fixedint.MutableUInt32:
        self.preventMissingAdress(adress)
        return (
            fixedint.MutableUInt32(
                int(self.memory_file[(adress + 3) % pow(2, 32)]) << 24
            )
            | fixedint.MutableUInt32(
                int(self.memory_file[(adress + 2) % pow(2, 32)]) << 16
            )
            | fixedint.MutableUInt32(
                int(self.memory_file[(adress + 1) % pow(2, 32)]) << 8
            )
            | fixedint.MutableUInt32(int(self.memory_file[adress % pow(2, 32)]))
        )

    def store_word(self, adress: int, value: fixedint.MutableUInt32):
        self.memory_file[adress % pow(2, 32)] = fixedint.MutableUInt8(int(value[0:8]))
        self.memory_file[(adress + 1) % pow(2, 32)] = fixedint.MutableUInt8(
            int(value[8:16])
        )
        self.memory_file[(adress + 2) % pow(2, 32)] = fixedint.MutableUInt8(
            int(value[16:24])
        )
        self.memory_file[(adress + 3) % pow(2, 32)] = fixedint.MutableUInt8(
            int(value[24:32])
        )
        
    def preventMissingAdress(self, adress: int):
        if not adress in self.memory_file:
            self.store_word(adress, fixedint.MutableUInt32(0))
            
@dataclass
class CsrRegisterFile(Memory):
    privilege_level: int = 0
    
    def load_byte(self, adress: int) -> fixedint.MutableUInt8:
        self.checkPrivilegeLevel(adress)
        self.preventMissingAdress(adress)
        return super().load_byte(adress)
    
    def store_byte(self, adress: int, value: fixedint.MutableUInt8):
        self.checkPrivilegeLevel(adress)
        self.preventMissingAdress(adress)
        self.checkReadOnly(adress)
        return super().store_byte(adress, value)
    
    def load_halfword(self, adress: int) -> fixedint.MutableUInt16:
        self.checkPrivilegeLevel(adress)
        self.preventMissingAdress(adress)
        return super().load_halfword(adress)
    
    def store_halfword(self, adress: int, value: fixedint.MutableUInt16):
        self.checkPrivilegeLevel(adress)
        self.preventMissingAdress(adress)
        self.checkReadOnly(adress)
        return super().store_halfword(adress, value)
    
    def load_word(self, adress: int) -> fixedint.MutableUInt32:
        self.checkPrivilegeLevel(adress)
        self.preventMissingAdress(adress)
        return super().load_word(adress)
    
    def store_word(self, adress: int, value: fixedint.MutableUInt32):
        self.checkPrivilegeLevel(adress)
        self.preventMissingAdress(adress)
        self.checkReadOnly(adress)
        return super().store_word(adress, value)
    
    def checkPrivilegeLevel(self, adress: int):
        if (adress & 0b001100000000) > self.privilege_level:
            raise Exception("illegal action: privilege level too low to access this csr register")
        
    def preventMissingAdress(self, adress: int):
        if adress < 0 | adress > 4095:
            raise Exception("illegal action: csr register does not exist")
        elif not adress in self.memory_file:
            super().store_word(adress, fixedint.MutableUInt32(0))

    def checkReadOnly(self, adress: int):
        if adress & 0b100000000000 and adress & 0b010000000000:
            raise Exception("illegal action: attempting to write into read-only csr register")
        
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
    
