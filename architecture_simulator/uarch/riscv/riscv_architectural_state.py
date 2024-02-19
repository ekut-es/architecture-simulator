from typing import Optional

from architecture_simulator.settings.settings import Settings
from .riscv_performance_metrics import RiscvPerformanceMetrics
from .register_file import RegisterFile
from architecture_simulator.uarch.memory import Memory, AddressingType
from ..instruction_memory import InstructionMemory
from .csr_registers import CsrRegisterFile
from architecture_simulator.isa.riscv.instruction_types import RiscvInstruction
from .stages import (
    SingleStage,
    InstructionFetchStage,
    InstructionDecodeStage,
    ExecuteStage,
    MemoryAccessStage,
    RegisterWritebackStage,
)
from .pipeline import Pipeline


class RiscvArchitecturalState:
    """The Architectural State for the RISC-V architecture."""

    def __init__(
        self,
        pipeline_mode: str = Settings().get()["default_pipeline_mode"],
        detect_data_hazards: bool = Settings().get()["hazard_detection"],
        memory: Optional[Memory] = None,
        register_file: Optional[RegisterFile] = None,
    ):
        if pipeline_mode == "five_stage_pipeline":
            stages = [
                InstructionFetchStage(),
                InstructionDecodeStage(detect_data_hazards=detect_data_hazards),
                ExecuteStage(),
                MemoryAccessStage(),
                RegisterWritebackStage(),
            ]
            execution_ordering = [0, 4, 1, 2, 3]
        else:
            stages = [SingleStage()]
            execution_ordering = [0]
        self.pipeline = Pipeline(
            stages=stages, execution_ordering=execution_ordering, state=self
        )
        self.instruction_memory = InstructionMemory[RiscvInstruction]()
        address_length: int = Settings().get()["memory_address_length"]
        self.memory = (
            Memory(
                AddressingType.BYTE,
                address_length,
                True,
                range(
                    Settings().get()["memory_address_min_bytes"], 2**address_length
                ),
            )
            if memory is None
            else memory
        )
        self.register_file = RegisterFile() if register_file is None else register_file
        self.csr_registers = CsrRegisterFile()
        self.program_counter = self.instruction_memory.address_range.start  # 0
        self.previous_program_counter = self.program_counter
        self.performance_metrics = RiscvPerformanceMetrics()

    def change_privilege_level(self, level: int):
        if not level < 0 and not level > 3:
            self.csr_registers.privilege_level = level

    def get_privilege_level(self):
        return self.csr_registers.privilege_level

    def instruction_at_pc(self) -> bool:
        """Return whether there is an instruction at the current program counter."""
        return self.instruction_memory.instruction_at_address(self.program_counter)
