from __future__ import annotations
from typing import TYPE_CHECKING
from architecture_simulator.simulation.runtime_errors import (
    InstructionExecutionException,
)

from ...isa.riscv.instruction_types import EmptyInstruction

from .pipeline_registers import PipelineRegister


if TYPE_CHECKING:
    from architecture_simulator.uarch.riscv.riscv_architectural_state import (
        RiscvArchitecturalState,
    )
    from .stages import Stage


class Pipeline:
    """The pipeline class which works on a list of stages."""

    def __init__(
        self,
        stages: list[Stage],
        execution_ordering: list[int],
        state: RiscvArchitecturalState,
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

        # if != None: [index of stage to cause stall, remaining duration of stall]
        self.stalled: list[int] | None = None
        # holds the old contents of pipeline registers that are used as input for stalled stages
        self.stalled_pipeline_regs: list[PipelineRegister] | None = None

    def step(self):
        """the pipeline step method, this is the central part of the pipeline! Every time it is called, it does one
        whole step of the pipeline, and every stage gets executed once in their execution ordering
        """
        self.state.performance_metrics.cycles += 1
        next_pipeline_registers = [None] * self.num_stages
        for index in self.execution_ordering:
            try:
                if self.stalled is not None:
                    if index == 0:  # first stage must not be recomputed when stalling
                        next_pipeline_registers[0] = self.pipeline_registers[0]
                        continue
                    elif (
                        index == self.stalled[0] + 1
                    ):  # first stage after the stalled stages must get an empty PipelineRegister while stalling
                        tmp = self.pipeline_registers[self.stalled[0]]
                        self.pipeline_registers[self.stalled[0]] = PipelineRegister()
                        next_pipeline_registers[index] = self.stages[index].behavior(
                            pipeline_registers=self.pipeline_registers,
                            index_of_own_input_register=(index - 1),
                            state=self.state,
                        )
                        self.pipeline_registers[self.stalled[0]] = tmp
                        continue
                    elif (
                        index <= self.stalled[0]
                    ):  # other stalled stages should get the old PipelineRegister values stored in stalled_pipeline_regs
                        tmp = self.pipeline_registers[index - 1]
                        self.pipeline_registers[index - 1] = self.stalled_pipeline_regs[
                            index - 1
                        ]
                        next_pipeline_registers[index] = self.stages[index].behavior(
                            pipeline_registers=self.pipeline_registers,
                            index_of_own_input_register=(index - 1),
                            state=self.state,
                        )
                        self.pipeline_registers[index - 1] = tmp
                        continue

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

        # Check if a stage has produced a meaningfull stall signal
        for index, pipeline_register in reversed(
            list(enumerate(next_pipeline_registers))
        ):
            if (
                pipeline_register is not None
                and pipeline_register.stall_signal is not None
                and (self.stalled is None or index > self.stalled[0])
            ):
                self.stalled = [index, pipeline_register.stall_signal.duration + 1]
                self.state.performance_metrics.stalls += 1
                break

        # keep PipelineRegister values in stalled_pipeline_regs
        if self.stalled and self.stalled_pipeline_regs is None:
            self.stalled_pipeline_regs = self.pipeline_registers[: self.stalled[0]]

            for reg in self.stalled_pipeline_regs:
                reg.is_of_stalled_value = True

        self.pipeline_registers = next_pipeline_registers

        # Check if done stalling
        if self.stalled is not None:
            self.stalled[1] -= 1
            if self.stalled[1] == 0:
                self.stalled = None
                self.stalled_pipeline_regs = None

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

                # Unstall stages that have been flushed
                if self.stalled is not None and self.stalled[0] < num_to_flush:
                    self.stalled = None
                    self.stalled_pipeline_regs = None

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
        """Return True if the simulation was stopped with an ecall or if
        the pipeline is empty and there is no instruction at the program counter,
        so nothing would happen anymore

        Returns:
            bool: if the pipeline has finished
        """
        return self.state.exit_code is not None or (
            self.is_empty() and not self.state.instruction_at_pc()
        )
