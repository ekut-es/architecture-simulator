import unittest

from architecture_simulator.uarch.architectural_state import RegisterFile
from architecture_simulator.uarch.architectural_state import ArchitecturalState
from architecture_simulator.simulation.simulation import Simulation


class TestSimulation(unittest.TestCase):
    def test_simulation(self):
        simulation = Simulation(
            state=ArchitecturalState(
                register_file=RegisterFile(registers=[0, 2, 0, 0])
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
