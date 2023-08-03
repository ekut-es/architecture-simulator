import unittest
from architecture_simulator.simulation.toy_simulation import ToySimulation
from architecture_simulator.isa.toy.toy_instructions import ADD, INC, STO, LDA


class TestToySimulation(unittest.TestCase):
    def test_step(self):
        simulation = ToySimulation()
        simulation.state.instruction_memory.write_instructions(
            [INC(), INC(), STO(1024), ADD(1024), STO(1025), INC(), LDA(4095)]
        )
        self.assert_(not simulation.is_done())
        simulation.step()
        self.assertEqual(simulation.state.accu, 1)
        simulation.step()
        self.assertEqual(simulation.state.accu, 2)
        simulation.step()
        self.assertEqual(simulation.state.data_memory.read_halfword(1024), 2)
        simulation.step()
        self.assertEqual(simulation.state.accu, 4)
        simulation.step()
        self.assertEqual(simulation.state.data_memory.read_halfword(1025), 4)
        simulation.step()
        self.assertEqual(simulation.state.accu, 5)
        simulation.step()
        self.assertEqual(simulation.state.accu, 0)
        self.assert_(simulation.is_done())

    def test_run(self):
        simulation = ToySimulation()
        simulation.state.instruction_memory.write_instructions(
            [INC(), INC(), STO(1024), ADD(1024), STO(1025), INC(), LDA(4095)]
        )
        self.assert_(not simulation.is_done())
        simulation.run()
        self.assert_(simulation.is_done())
        self.assertEqual(simulation.state.program_counter, 7)
        self.assertEqual(simulation.state.accu, 0)
        self.assertEqual(simulation.state.data_memory.read_halfword(1024), 2)
        self.assertEqual(simulation.state.data_memory.read_halfword(1025), 4)
        self.assertEqual(simulation.state.data_memory.read_halfword(4095), 0)

    def test_load_program(self):
        simulation = ToySimulation()
        program = """INC
        DEC
        INC
        STO $400
        ADD $400
        STO $400
        ADD $400"""
        simulation.load_program(program)
        simulation.run()
        self.assertEqual(simulation.state.data_memory.read_halfword(0x400), 2)
        self.assertEqual(simulation.state.accu, 4)

    def test_performance_metrics(self):
        simulation = ToySimulation()
        program = """INC
        INC
        INC
        INC
        DEC
        BRZ $008
        ZRO
        BRZ $003
        BRZ $009
        ADD $400"""
        simulation.load_program(program)
        simulation.run()
        self.assertEqual(simulation.state.accu, 0)
        self.assertEqual(simulation.state.performance_metrics.instruction_count, 13)
        self.assertEqual(simulation.state.performance_metrics.cycles, 13)
        self.assertEqual(simulation.state.performance_metrics.branch_count, 3)
        self.assertGreater(simulation.state.performance_metrics.execution_time_s, 0)
