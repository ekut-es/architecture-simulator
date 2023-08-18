from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class PerformanceMetrics(ABC):
    """An abstract base class for holding and measuring the performance and statistics of a simulation."""

    _execution_time_s: float = 0
    instruction_count: int = 0
    _start: Optional[float] = None

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
        self._execution_time_s += time.time() - self._start
        self._start = None

    def get_execution_time(self) -> float:
        """Returns the time for which the timer has been running. If the timer is still running, the time since it was last started is also considered. Do not access _execution_time_s for that reason.

        Returns:
            float: The time for which the timer has been running, in seconds.
        """
        return self._execution_time_s + (
            (time.time() - self._start) if self._start is not None else 0
        )

    @abstractmethod
    def __repr__(self):
        """A string representation of the performance metrics for the end user."""
