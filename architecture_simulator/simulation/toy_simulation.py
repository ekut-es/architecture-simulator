from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from architecture_simulator.uarch.toy.toy_architectural_state import (
    ToyArchitecturalState,
)
from architecture_simulator.isa.toy.toy_parser import ToyParser
from architecture_simulator.isa.toy.toy_instructions import ToyInstruction
from .simulation import Simulation
from .runtime_errors import StepSequenceError
from fixedint import MutableUInt16
from architecture_simulator.uarch.toy.SvgVisValues import SvgVisValues

if TYPE_CHECKING:
    from architecture_simulator.uarch.toy.toy_performance_metrics import (
        ToyPerformanceMetrics,
    )


class ToySimulation(Simulation):
    def __init__(
        self,
        unified_memory_size: Optional[int] = None,
    ):
        self.state = ToyArchitecturalState(unified_memory_size)
        self.next_cycle = 1

    def first_cycle_step(self):
        """
        Simulates the behaviour of the first cycle of a instruction.
        Can not be called if self.next_cycle = 2
        """
        if self.is_done():
            return
        if not self.next_cycle == 1:
            raise StepSequenceError(
                "Bevore you can call this function again, you have to call second_cycle_step()"
            )
        self.next_cycle = 2
        self.state.loaded_instruction.behavior(self.state)

    def second_cycle_step(self):
        """
        Simulates the behaviour of the second cycle of a instruction.
        Can not be called if self.next_cycle = 1
        """
        if self.is_done():
            return
        if not self.next_cycle == 2:
            raise StepSequenceError(
                "Bevore you can call this function again, you have to call first_cycle_step()"
            )
        old_op_code = (int(self.state.loaded_instruction) >> 12) & 0xF
        self.state.visualisation_values = SvgVisValues(
            op_code_old=old_op_code, pc_old=self.state.program_counter
        )
        if self.state.program_counter <= self.state.max_pc:
            self.state.visualisation_values.ram_out = self.state.memory.read_halfword(
                int(self.state.program_counter)
            )
            self.state.loaded_instruction = ToyInstruction.from_integer(
                int(self.state.visualisation_values.ram_out)
            )
        else:
            self.state.loaded_instruction = None
        self.state.program_counter += MutableUInt16(1)
        self.state.performance_metrics.instruction_count += 1
        self.next_cycle = 1

    def step(self):
        if not self.next_cycle == 1:
            raise StepSequenceError(
                "step() calls both first_cycle_step() and second_cycle_step(), so you can not call step after calling just first_cycle_step()."
            )
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
