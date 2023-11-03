from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from architecture_simulator.uarch.toy.toy_architectural_state import (
    ToyArchitecturalState,
)
from architecture_simulator.isa.toy.toy_parser import ToyParser
from architecture_simulator.isa.toy.toy_instructions import ToyInstruction
from .simulation import Simulation
from .runtime_errors import InstructionExecutionException
from fixedint import MutableUInt16

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
        self.next_cycle = 1

    def first_cycle_step(self):
        if self.is_done():
            return
        if not self.next_cycle == 1:
            return  # NOTE: Proper Error
        self.next_cycle = 2
        self.state.loaded_instruction.behavior(self.state)

    def second_cycle_step(self):
        if self.is_done():
            return
        if not self.next_cycle == 2:
            return  # NOTE: Proper Error
        if self.state.program_counter <= self.state.max_pc:
            self.state.loaded_instruction = ToyInstruction.from_integer(
                int(self.state.memory.read_halfword(int(self.state.program_counter)))
            )
        else:
            self.state.loaded_instruction = None
        self.state.program_counter += MutableUInt16(1)
        self.state.performance_metrics.instruction_count += 1
        self.next_cycle = 1

    # step first clock
    # step second clock
    def step(self):
        if not self.next_cycle == 1:
            return True  # NOTE: Proper Error
        self.first_cycle_step()
        self.second_cycle_step()
        return not self.is_done()

    def is_done(self) -> bool:
        return not self.state.instruction_loaded()

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
