from dataclasses import dataclass, field
import fixedint

from ..isa.parser import RiscvParser
from .performance_metrics import PerformanceMetrics
from .register_file import RegisterFile
from .memory import Memory, InstructionMemory, CsrRegisterFile


@dataclass
class ArchitecturalState:
    instruction_memory: InstructionMemory = field(default_factory=InstructionMemory)
    register_file: RegisterFile = field(default_factory=RegisterFile)
    memory: Memory = field(default_factory=Memory)
    csr_registers: CsrRegisterFile = field(default_factory=CsrRegisterFile)
    program_counter: int = 0
    performance_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    # pipeline: Pipeline

    def change_privilege_level(self, level: int):
        if not level < 0 and not level > 3:
            self.csr_registers.privilege_level = level

    def get_privilege_level(self):
        return self.csr_registers.privilege_level

    def instruction_at_pc(self) -> bool:
        return self.program_counter in self.instruction_memory.instructions
