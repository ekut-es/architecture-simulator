import unittest

from architecture_simulator.uarch.architectural_state import RegisterFile
from architecture_simulator.uarch.architectural_state import Memory
from architecture_simulator.uarch.architectural_state import ArchitecturalState
from architecture_simulator.simulation.simulation import Simulation
from architecture_simulator.isa.rv32i_instructions import ADDI


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

    def test_run_simulation(self):
        simulation = Simulation(
            state=ArchitecturalState(
                register_file=RegisterFile(registers=[0, 0, 0, 0])
            ),
            instructions={
                0: ADDI(1, 1, 1),
                4: ADDI(1, 1, 1),
                8: ADDI(1, 1, 1),
                12: ADDI(1, 1, 1),
                16: ADDI(1, 1, 1),
                20: ADDI(1, 1, 1),
                24: ADDI(1, 1, 1),
            },
        )
        simulation.run_simulation()
        self.assertEquals(int(simulation.state.register_file.registers[1]), 7)

        simulation = Simulation(
            state=ArchitecturalState(
                register_file=RegisterFile(registers=[0, 0, 0, 0])
            ),
            instructions={},
        )
        simulation.run_simulation()
        # basically just checking if it terminated
        self.assertEquals(int(simulation.state.register_file.registers[0]), 0)
