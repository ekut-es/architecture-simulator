from dataclasses import dataclass
import fixedint


@dataclass
class RegisterFile:
    registers: list[fixedint.MutableUInt32]


@dataclass
class ArchitecturalState:
    register_file: RegisterFile
    program_counter: int = 0
