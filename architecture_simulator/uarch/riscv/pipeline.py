from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass

from ...isa.riscv.instruction_types import EmptyInstruction

from .pipeline_registers import PipelineRegister


if TYPE_CHECKING:
    from architecture_simulator.uarch.riscv.riscv_architectural_state import (
        ArchitecturalState,
    )
    from .stages import Stage

#
# Pipeline wrapper Classs
#


class Pipeline:
    def __init__(
        self,
        stages: list[Stage],
        execution_ordering: list[int],
        state: ArchitecturalState,
    ) -> None:
        """constructor of the pipeline

        Args:
            stages (list[Stage]): the stages the user wants to build the pipeline out of
            execution_ordering (list[int]): the execution ordering of the different stages,
            the list gets iterated over from first to last element, and executes the ith element in the
            stages list!
            state (ArchitecturalState): gets the current architectural state as an argument
        """
        self.stages = stages
        self.num_stages = len(stages)
        self.execution_ordering = execution_ordering
        self.state = state
        self.pipeline_registers: list[PipelineRegister] = [
            PipelineRegister()
        ] * self.num_stages

    def step(self):
        """the pipeline step method, this is the central part of the pipeline! Every time it is called, it does one
        whole step of the pipeline, and every stage gets executed once in their ececution ordering
        """
        self.state.performance_metrics.cycles += 1
        next_pipeline_registers = [None] * self.num_stages
        for index in self.execution_ordering:
            try:
                next_pipeline_registers[index] = self.stages[index].behavior(
                    pipeline_registers=self.pipeline_registers,
                    index_of_own_input_register=(index - 1),
                    state=self.state,
                )
            except Exception as e:
                if index - 1 >= 0:
                    raise InstructionExecutionException(
                        address=self.pipeline_registers[
                            index - 1
                        ].address_of_instruction,
                        instruction_repr=self.pipeline_registers[
                            index - 1
                        ].instruction.__repr__(),
                        error_message=e.__repr__(),
                    )
                else:
                    raise
        self.pipeline_registers = next_pipeline_registers

        # if one of the stages wants to flush, do so (starting from the back makes sense)
        for index, pipeline_register in reversed(
            list(enumerate(self.pipeline_registers))
        ):
            flush_signal = pipeline_register.flush_signal
            if flush_signal is not None:
                self.state.performance_metrics.flushes += 1
                # This works because int(True) = 1, int(False) = 0
                # This is good code, trust me
                num_to_flush = index + flush_signal.inclusive
                self.pipeline_registers[:num_to_flush] = [
                    PipelineRegister()
                ] * num_to_flush
                self.state.program_counter = flush_signal.address
                break  # break since we don't care about the previous stages

    def is_empty(self) -> bool:
        """Return True if all pipeline registers (exluding the last) are empty (determined by whether the instruction in the pipeline register is empty).
            Note, that the last pipeline register is not considerd, because it will not be used as input for an other stage.

        Returns:
            bool: whether all pipeline registers are empty
        """
        return all(
            type(pipeline_register.instruction) == EmptyInstruction
            for pipeline_register in self.pipeline_registers[:-1]
        )

    def is_done(self) -> bool:
        """Return True if the pipeline is empty and there is no instruction at the program counter, so nothing will happen anymore

        Returns:
            bool: if the pipeline has finished
        """
        return self.is_empty() and not self.state.instruction_at_pc()


@dataclass
class InstructionExecutionException(RuntimeError):
    address: int
    instruction_repr: str
    error_message: str

    def __repr__(self):
        return f"There was an error executing the instruction at address '{self.address}': '{self.instruction_repr}':\n{self.error_message}"
