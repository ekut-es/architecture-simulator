import unittest
from architecture_simulator.simulation.toy_simulation import ToySimulation
from architecture_simulator.isa.toy.toy_instructions import ADD, INC, STO, LDA
from architecture_simulator.simulation.runtime_errors import (
    InstructionExecutionException,
)


class TestToySimulation(unittest.TestCase):
    def test_step(self):
        simulation = ToySimulation()
        simulation.state.instruction_memory.write_instructions(
            [INC(), INC(), STO(1024), ADD(1024), STO(1025), INC(), LDA(4095)]
        )
        self.assertTrue(not simulation.is_done())
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
        self.assertTrue(simulation.is_done())

    def test_run(self):
        simulation = ToySimulation()
        simulation.state.instruction_memory.write_instructions(
            [INC(), INC(), STO(1024), ADD(1024), STO(1025), INC(), LDA(4095)]
        )
        self.assertTrue(not simulation.is_done())
        simulation.run()
        self.assertTrue(simulation.is_done())
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
        self.assertEqual(simulation.state.performance_metrics.branch_count, 3)
        self.assertGreater(simulation.state.performance_metrics.get_execution_time(), 0)

    def test_program(self):
        simulation = ToySimulation()
        program = """    # computes the sum of the numbers from 1 to n
    # result gets saved in MEM[1025]
    Loopcount = $400
    Result = $401
    :$400:20 # enter n here

    LDA Loopcount # skip to the end if n=0
    BRZ end
    loop:
        LDA Result
        ADD Loopcount
        STO Result
        LDA Loopcount
        DEC
        STO Loopcount
        BRZ end
        ZRO
        BRZ loop
    end:"""
        simulation.load_program(program)
        simulation.run()
        self.assertEqual(simulation.state.data_memory.read_halfword(1025), 210)

    def test_memory_issue(self):
        program = """INC
STO $400
INC"""
        simulation = ToySimulation()
        simulation.load_program(program)
        simulation.run()
        self.assertEqual(simulation.state.accu, 2)
        self.assertEqual(simulation.state.data_memory.memory_file[1024], 1)
        self.assertEqual(simulation.state.data_memory.read_halfword(1024), 1)

        program = """INC
STO $400
LDA $400
INC"""
        simulation = ToySimulation()
        simulation.load_program(program)
        simulation.run()
        self.assertEqual(simulation.state.accu, 2)
        self.assertEqual(simulation.state.data_memory.memory_file[1024], 1)
        self.assertEqual(simulation.state.data_memory.read_halfword(1024), 1)

    def test_instruction_execution_exception(self):
        simulation = ToySimulation()
        simulation.load_program(
            """INC
                                DEC
                                DEC
                                LDA 0
                                INC
                                INC"""
        )
        with self.assertRaises(InstructionExecutionException) as cm:
            simulation.run()
        self.assertEqual(cm.exception.address, 3)
        self.assertEqual(cm.exception.instruction_repr, "LDA $000")
