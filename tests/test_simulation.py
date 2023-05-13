import unittest

from architecture_simulator.uarch.architectural_state import RegisterFile
from architecture_simulator.uarch.architectural_state import Memory
from architecture_simulator.uarch.architectural_state import ArchitecturalState
from architecture_simulator.simulation.simulation import Simulation
from architecture_simulator.isa.rv32i_instructions import ADDI, BNE, BEQ


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
                0: ADDI(rd=1, rs1=1, imm=1),
                4: ADDI(rd=1, rs1=1, imm=1),
                8: ADDI(rd=1, rs1=1, imm=1),
                12: ADDI(rd=1, rs1=1, imm=1),
                16: ADDI(rd=1, rs1=1, imm=1),
                20: ADDI(rd=1, rs1=1, imm=1),
                24: ADDI(rd=1, rs1=1, imm=1),
            },
        )
        metrics = simulation.run_simulation()
        self.assertEquals(int(simulation.state.register_file.registers[1]), 7)
        self.assertEquals(metrics.branch_count, 0)
        self.assertEquals(metrics.instruction_count, 7)
        self.assertGreater(metrics.instructions_per_second, 0)
        self.assertGreater(metrics.execution_time_s, 0)

        simulation = Simulation(
            state=ArchitecturalState(
                register_file=RegisterFile(registers=[0, 0, 0, 0])
            ),
            instructions={},
        )
        metrics = simulation.run_simulation()
        self.assertEquals(int(simulation.state.register_file.registers[0]), 0)
        self.assertEquals(metrics.branch_count, 0)
        self.assertEquals(metrics.instruction_count, 0)
        self.assertEquals(metrics.instructions_per_second, 0)
        self.assertGreaterEqual(metrics.execution_time_s, 0)

        simulation = Simulation(
            state=ArchitecturalState(
                register_file=RegisterFile(registers=[0, 0, 0, 0])
            ),
            instructions={
                0: ADDI(rd=2, rs1=0, imm=5),
                4: ADDI(rd=1, rs1=1, imm=1),
                8: BNE(rs1=1, rs2=2, imm=-2),
                12: BEQ(rs1=0, rs2=0, imm=4),
                16: ADDI(rd=0, rs1=0, imm=0),
                20: ADDI(rd=3, rs1=0, imm=64),
            },
        )
        metrics = simulation.run_simulation()
        self.assertEquals(simulation.state.register_file.registers, [0, 5, 5, 64])
        self.assertEquals(metrics.branch_count, 5)
        self.assertEquals(metrics.instruction_count, 13)
        self.assertGreater(metrics.instructions_per_second, 0)
        self.assertGreater(metrics.execution_time_s, 0)

        simulation = Simulation(
            state=ArchitecturalState(
                register_file=RegisterFile(registers=[0, 0, 0, 0])
            ),
            instructions={
                0: ADDI(rd=2, rs1=0, imm=33),
                4: ADDI(rd=1, rs1=1, imm=1),
                8: ADDI(rd=1, rs1=1, imm=1),
                12: ADDI(rd=1, rs1=1, imm=1),
                16: BNE(rs1=1, rs2=2, imm=-6),
            },
        )
        metrics = simulation.run_simulation()
        self.assertEquals(simulation.state.register_file.registers, [0, 33, 33, 0])
        self.assertEquals(metrics.branch_count, 10)
        self.assertEquals(metrics.instruction_count, 45)
        self.assertGreater(metrics.instructions_per_second, 0)
        self.assertGreater(metrics.execution_time_s, 0)
