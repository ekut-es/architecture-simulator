from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from architecture_simulator.uarch.performance_metrics import PerformanceMetrics


class Simulation(ABC):
    def __init__(self):
        self.has_started = False

    @abstractmethod
    def step(self) -> bool:
        """Execute the next instruction. Does nothing if there are no more instructions to execute.

        Returns:
            bool: True if the simulation has not yet finished, else False.
        """

    @abstractmethod
    def run(self):
        """Execute instructions until the simulation has finished."""

    @abstractmethod
    def is_done(self) -> bool:
        """Return whether the simulation has finished.

        Returns:
            bool: Whether the simulation has finished.
        """

    @abstractmethod
    def load_program(self, program: str):
        """Load a program into the simulation.

        Args:
            program (str): A text format assembly program.
        """

    @abstractmethod
    def has_instructions(self) -> bool:
        """Returns whether there are any instructions loaded in the simulation (e.g. in the instruction memory).

        Returns:
            bool: Whether there are any instructions in the simulation.
        """

    @abstractmethod
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get the performance metrics of the simulation.

        Returns:
            PerformanceMetrics: The performance metrics which contain statistics about the simulation.
        """

    def get_performance_metrics_str(self) -> str:
        """
        Returns:
            str: The string representation of the performance metrics.
        """
        return str(self.get_performance_metrics())
