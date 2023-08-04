from abc import ABC, abstractmethod


class Simulation(ABC):
    @abstractmethod
    def step(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def is_done(self):
        pass

    @abstractmethod
    def load_program(self, program: str):
        pass
