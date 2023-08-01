from fixedint import MutableUInt16
from typing import Optional

from .toy_memory import ToyMemory
from ..memory import InstructionMemory
from architecture_simulator.isa.toy.toy_instructions import ToyInstruction
from ..performance_metrics import PerformanceMetrics


class ToyArchitecturalState:
    def __init__(
        self,
        instruction_memory_range: Optional[range] = None,
        data_memory_range: Optional[range] = None,
    ):
        self.program_counter = MutableUInt16(
            instruction_memory_range.start if instruction_memory_range else 0
        )
        self.accu = MutableUInt16(0)
        self.instruction_memory = InstructionMemory[ToyInstruction](
            address_range=(
                instruction_memory_range if instruction_memory_range else range(0, 1024)
            )
        )
        self.data_memory = ToyMemory(
            address_range=(
                data_memory_range if data_memory_range else range(1024, 4096)
            )
        )
        self.performance_metrics = PerformanceMetrics()

    def increment_pc(self):
        self.program_counter += MutableUInt16(1)

    def instruction_at_pc(self) -> bool:
        """Return whether there is an instruction in the instruction memory at the current program counter.

        Returns:
            bool: Whether there is an instruction in the instruction memory at the current program counter.
        """
        return self.instruction_memory.instruction_at_address(int(self.program_counter))
