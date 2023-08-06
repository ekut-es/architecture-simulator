from abc import ABC, abstractmethod


class Simulation(ABC):
    @abstractmethod
    def step(self) -> bool:
        """Execute the next instruction.

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
