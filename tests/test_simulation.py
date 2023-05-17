import unittest

from architecture_simulator.uarch.architectural_state import RegisterFile
from architecture_simulator.uarch.architectural_state import Memory
from architecture_simulator.uarch.architectural_state import ArchitecturalState
from architecture_simulator.simulation.simulation import Simulation
from architecture_simulator.examples.examples import fibonacci_recursive


class TestSimulation(unittest.TestCase):
    def test_simulation(self):
        simulation = Simulation(
            state=ArchitecturalState(
                register_file=RegisterFile(registers=[0, 2, 0, 0]),
                memory=Memory(memory_file=()),
            ),
            instructions={},
        )
        simulation.append_instructions("add x0, x0, x1\nadd x0, x0, x1")
        # simulation.append_instructions("sub x0, x0, x1")
        simulation.step_simulation()
        self.assertEqual(simulation.state.register_file.registers[0], 2)
        simulation.step_simulation()
        self.assertEqual(simulation.state.register_file.registers[0], 4)
        # simulation.step_simulation()
        # self.assertEqual(simulation.state.register_file.registers[0], 2)

    def test_fibonacci_recursive(self):
        self.assertEqual(int(fibonacci_recursive(-5)), 0)
        self.assertEqual(int(fibonacci_recursive(0)), 0)
        self.assertEqual(int(fibonacci_recursive(1)), 1)
        self.assertEqual(int(fibonacci_recursive(2)), 1)
        self.assertEqual(int(fibonacci_recursive(3)), 2)
        self.assertEqual(int(fibonacci_recursive(4)), 3)
        self.assertEqual(int(fibonacci_recursive(5)), 5)
        self.assertEqual(int(fibonacci_recursive(6)), 8)
        self.assertEqual(int(fibonacci_recursive(7)), 13)
        self.assertEqual(int(fibonacci_recursive(20)), 6765)
