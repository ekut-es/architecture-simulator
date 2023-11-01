from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from architecture_simulator.uarch.toy.toy_architectural_state import (
    ToyArchitecturalState,
)
from architecture_simulator.isa.toy.toy_parser import ToyParser
from architecture_simulator.isa.toy.toy_instructions import ToyInstruction
from .simulation import Simulation
from .runtime_errors import InstructionExecutionException

if TYPE_CHECKING:
    from architecture_simulator.uarch.toy.toy_performance_metrics import (
        ToyPerformanceMetrics,
    )


class ToySimulation(Simulation):
    def __init__(
        self,
        instruction_memory_range: Optional[range] = None,
        data_memory_range: Optional[range] = None,
    ):
        self.state = ToyArchitecturalState()  # NOTE ???

    # step first clock
    # step second clock
    def step(self):
        if not self.is_done():
            program_counter = self.state.program_counter
            instruction = ToyInstruction.from_integer(
                int(self.state.memory.read_halfword(int(program_counter)))
            )
            # inc pc
            try:
                instruction.behavior(self.state)
                self.state.performance_metrics.instruction_count += 1
            except Exception as e:
                raise InstructionExecutionException(
                    address=int(program_counter),
                    instruction_repr=str(instruction),
                    error_message=e.__repr__(),
                )
        return not self.is_done()

    def is_done(self) -> bool:
        return not self.state.instruction_at_pc()

    def run(self):
        self.state.performance_metrics.resume_timer()
        while not self.is_done():
            self.step()
        self.state.performance_metrics.stop_timer()

    def load_program(self, program: str):
        self.state = ToyArchitecturalState()
        parser = ToyParser()
        parser.parse(program=program, state=self.state)

    def has_instructions(self) -> bool:
        return False if self.state.max_pc is None else self.state.max_pc >= 0

    def get_performance_metrics(self) -> ToyPerformanceMetrics:
        return self.state.performance_metrics
