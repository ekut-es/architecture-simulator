from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from architecture_simulator.settings.settings import Settings
from .riscv_performance_metrics import RiscvPerformanceMetrics
from .register_file import RegisterFile
from architecture_simulator.uarch.memory.memory import Memory, AddressingType
from ..memory.instruction_memory import InstructionMemory
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
from architecture_simulator.uarch.memory.instruction_memory_cache_system import (
    InstructionMemoryCacheSystem,
)
from architecture_simulator.uarch.memory.write_through_memory_system import (
    WriteThroughMemorySystem,
)

if TYPE_CHECKING:
    from architecture_simulator.uarch.memory.memory_system import MemorySystem
    from architecture_simulator.uarch.memory.instruction_memory_system import (
        InstructionMemorySystem,
    )
    from architecture_simulator.uarch.memory.cache import CacheOptions


class RiscvArchitecturalState:
    """The Architectural State for the RISC-V architecture."""

    def __init__(
        self,
        pipeline_mode: str = Settings().get()["default_pipeline_mode"],
        detect_data_hazards: bool = Settings().get()["hazard_detection"],
        memory: Optional[MemorySystem] = None,
        register_file: Optional[RegisterFile] = None,
        instruction_memory: Optional[InstructionMemorySystem] = None,
        data_cache: CacheOptions = Settings().get()["data_cache"],
        instruction_cache: CacheOptions = Settings().get()["instruction_cache"],
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
        ###
        if instruction_memory is not None:
            self.instruction_memory = instruction_memory
        else:
            if instruction_cache.enable:
                self.instruction_memory = InstructionMemoryCacheSystem(
                    instruction_memory=InstructionMemory[RiscvInstruction](),
                    num_index_bits=instruction_cache.num_index_bits,
                    num_block_bits=instruction_cache.num_block_bits,
                    associativity=instruction_cache.associativity,
                )
            else:
                self.instruction_memory = InstructionMemory[RiscvInstruction]()

        ###
        address_length: int = Settings().get()["memory_address_length"]
        if memory is not None:
            self.memory = memory
        else:
            if data_cache.enable:
                self.memory = WriteThroughMemorySystem(
                    memory=Memory(
                        AddressingType.BYTE,
                        address_length,
                        True,
                        range(
                            Settings().get()["memory_address_min_bytes"],
                            2**address_length,
                        ),
                    ),
                    num_index_bits=data_cache.num_index_bits,
                    num_block_bits=data_cache.num_block_bits,
                    associativity=data_cache.associativity,
                )
            else:
                self.memory = Memory(
                    AddressingType.BYTE,
                    address_length,
                    True,
                    range(
                        Settings().get()["memory_address_min_bytes"],
                        2**address_length,
                    ),
                )
        self.register_file = RegisterFile() if register_file is None else register_file
        self.csr_registers = CsrRegisterFile()
        self.program_counter = self.instruction_memory.get_address_range().start  # 0
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
