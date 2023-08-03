import fixedint
from dataclasses import dataclass

from ..memory import Memory


class CsrRegisterFile(Memory):
    """A class for the CSR memory."""

    def __init__(self, privilege_level: int = 0, min_bytes: int = 0):
        super().__init__()
        self.privilege_level = privilege_level
        self.min_bytes = min_bytes

    def read_byte(self, address: int) -> fixedint.MutableUInt8:
        self.check_for_legal_address(address)
        self.check_privilege_level(address)
        return super().read_byte(address)

    def write_byte(self, address: int, value: fixedint.MutableUInt8):
        self.check_for_legal_address(address)
        self.check_privilege_level(address)
        self.check_read_only(address)
        return super().write_byte(address, value)

    def read_halfword(self, address: int) -> fixedint.MutableUInt16:
        self.check_for_legal_address(address)
        self.check_privilege_level(address)
        return super().read_halfword(address)

    def write_halfword(self, address: int, value: fixedint.MutableUInt16):
        self.check_for_legal_address(address)
        self.check_privilege_level(address)
        self.check_read_only(address)
        return super().write_halfword(address, value)

    def read_word(self, address: int) -> fixedint.MutableUInt32:
        self.check_for_legal_address(address)
        self.check_privilege_level(address)
        return super().read_word(address)

    def write_word(self, address: int, value: fixedint.MutableUInt32):
        self.check_for_legal_address(address)
        self.check_privilege_level(address)
        self.check_read_only(address)
        return super().write_word(address, value)

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
