from typing import Optional
from dataclasses import dataclass
import time


@dataclass
class PerformanceMetrics:
    """A class to store and meassure the performance of a simulation.
    This class contains information which not all ISAs/simulations need,
    so you might want to create your own performance metrics class for other ISAs.
    """

    execution_time_s: float = 0
    instruction_count: int = 0
    branch_count: int = 0
    procedure_count: int = 0
    _start: Optional[float] = None
    cycles: int = 0
    flushes: int = 0

    def resume_timer(self):
        """Start/resume the timer which measures the time for which the simulation has been running.
        Calling this function when the timer is already running won't do anything, the timer will just keep running.
        """
        if self._start is None:
            self._start = time.time()

    def stop_timer(self):
        """Stops the timer which measures the time for which the simulation has been running.
        Calling this function when the timer is not running will not do anything."""
        if self._start is None:
            return
        self.execution_time_s += time.time() - self._start
        self._start = None

    def __repr__(self) -> str:
        representation = ""
        # self.execution_time_s only counts the time until the last "stop" of the timer
        # so we add the time since the last start if the simulation is currently running
        # this also affects the instructions per second, so we also calculate them here
        execution_time = self.execution_time_s + (
            (time.time() - self._start) if self._start is not None else 0
        )
        instructions_per_second = (
            (self.instruction_count / execution_time) if execution_time else -1
        )

        representation += f"execution time: {execution_time:.2f}s\n"
        if instructions_per_second != -1:
            representation += (
                f"instructions per second: {instructions_per_second:.2f}\n"
            )
        representation += f"instruction count: {self.instruction_count} \n"
        representation += f"branch count: {self.branch_count}\n"
        representation += f"procedure count: {self.procedure_count}\n"
        representation += f"cycles: {self.cycles}\n"
        representation += f"flushes: {self.flushes}\n"
        if not self.instruction_count == 0:
            representation += f"cycles per instruction: {(self.cycles / self.instruction_count):.2f}\n"
        return representation
