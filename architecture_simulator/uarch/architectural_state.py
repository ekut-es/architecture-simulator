from dataclasses import dataclass


@dataclass
class RegisterFile:
    registers: list[int]


@dataclass
class ArchitecturalState:
    register_file: RegisterFile
    program_counter: int = 0
