import unittest
from architecture_simulator.simulation.toy_simulation import ToySimulation
from architecture_simulator.isa.toy.toy_instructions import ADD, INC, STO, LDA
from architecture_simulator.simulation.runtime_errors import StepSequenceError


class TestToySimulation(unittest.TestCase):
    def test_step(self):
        simulation = ToySimulation()
        for addr, instr in enumerate(
            [INC(), INC(), STO(1024), ADD(1024), STO(1025), INC(), LDA(4095)]
        ):
            simulation.state.memory.write_halfword(addr, instr)
        simulation.state.max_pc = 6
        simulation.state.loaded_instruction = INC()
        self.assertTrue(not simulation.is_done())
        simulation.step()
        self.assertEqual(simulation.state.accu, 1)
        simulation.step()
        self.assertEqual(simulation.state.accu, 2)
        simulation.step()
        simulation.state.memory.read_halfword(1024)
        self.assertEqual(simulation.state.memory.read_halfword(1024), 2)
        simulation.step()
        self.assertEqual(simulation.state.accu, 4)
        simulation.step()
        self.assertEqual(simulation.state.memory.read_halfword(1025), 4)
        simulation.step()
        self.assertEqual(simulation.state.accu, 5)
        simulation.step()
        self.assertEqual(simulation.state.accu, 0)
        self.assertTrue(simulation.is_done())

    def test_run(self):
        simulation = ToySimulation()
        for addr, instr in enumerate(
            [INC(), INC(), STO(1024), ADD(1024), STO(1025), INC(), LDA(4095)]
        ):
            simulation.state.memory.write_halfword(addr, instr)
        simulation.state.max_pc = 7
        simulation.state.loaded_instruction = INC()
        self.assertTrue(not simulation.is_done())
        simulation.run()
        self.assertTrue(simulation.is_done())
        self.assertEqual(simulation.state.program_counter, 9)
        self.assertEqual(simulation.state.accu, 0)
        self.assertEqual(simulation.state.memory.read_halfword(1024), 2)
        self.assertEqual(simulation.state.memory.read_halfword(1025), 4)
        self.assertEqual(simulation.state.memory.read_halfword(4095), 0)

    def test_load_program(self):
        simulation = ToySimulation()
        program = """INC
        DEC
        INC
        STO 0x400
        ADD 0x400
        STO 0x400
        ADD 0x400"""
        simulation.load_program(program)
        simulation.run()
        self.assertEqual(simulation.state.memory.read_halfword(0x400), 2)
        self.assertEqual(simulation.state.accu, 4)

    def test_performance_metrics(self):
        simulation = ToySimulation()
        program = """INC
        INC
        INC
        INC
        DEC
        BRZ 0x008
        ZRO
        BRZ 0x003
        BRZ 0x009
        ADD 0x400"""
        simulation.load_program(program)
        simulation.run()
        self.assertEqual(simulation.state.accu, 0)
        self.assertEqual(simulation.state.performance_metrics.instruction_count, 13)
        self.assertEqual(simulation.state.performance_metrics.branch_count, 3)
        self.assertEqual(simulation.state.performance_metrics.cycles, 26)
        self.assertGreater(simulation.state.performance_metrics.get_execution_time(), 0)

    def test_program(self):
        simulation = ToySimulation()
        program = """    # computes the sum of the numbers from 1 to n
    # result gets saved in MEM[1025]
    Loopcount = 0x400
    Result = 0x401
    :0x400:20 # enter n here

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
        self.assertEqual(simulation.state.memory.read_halfword(1025), 210)

    def test_memory_issue(self):
        program = """INC
STO 0x400
INC"""
        simulation = ToySimulation()
        simulation.load_program(program)
        simulation.run()
        self.assertEqual(simulation.state.accu, 2)
        self.assertEqual(simulation.state.memory.memory_file[1024], 1)
        self.assertEqual(simulation.state.memory.read_halfword(1024), 1)

        program = """INC
STO 0x400
LDA 0x400
INC"""
        simulation = ToySimulation()
        simulation.load_program(program)
        simulation.run()
        self.assertEqual(simulation.state.accu, 2)
        self.assertEqual(simulation.state.memory.memory_file[1024], 1)
        self.assertEqual(simulation.state.memory.read_halfword(1024), 1)

    def test_vis_data(self):
        sim = ToySimulation()
        sim.load_program(
            """
            num = 0x400
            :0x400:11
            LDA num
            INC
            DEC
            ADD num
            SUB num
            SUB num
            BRZ label
            label:
            """
        )
        self.assertEqual(sim.state.visualisation_values.alu_out, None)
        self.assertEqual(sim.state.visualisation_values.ram_out, int(LDA(0x400)))
        self.assertEqual(sim.state.visualisation_values.jump, False)
        # LDA
        sim.first_cycle_step()
        self.assertEqual(sim.state.visualisation_values.alu_out, 11)
        self.assertEqual(sim.state.visualisation_values.ram_out, 11)
        self.assertEqual(sim.state.visualisation_values.jump, False)
        sim.second_cycle_step()
        # INC
        sim.first_cycle_step()
        self.assertEqual(sim.state.visualisation_values.alu_out, 12)
        self.assertEqual(sim.state.visualisation_values.ram_out, None)
        self.assertEqual(sim.state.visualisation_values.jump, False)
        sim.second_cycle_step()
        # DEC
        sim.step()
        # ADD
        sim.first_cycle_step()
        self.assertEqual(sim.state.visualisation_values.alu_out, 22)
        self.assertEqual(sim.state.visualisation_values.ram_out, 11)
        self.assertEqual(sim.state.visualisation_values.jump, False)
        sim.second_cycle_step()
        # SUB
        sim.step()
        # SUB
        sim.step()
        # BRZ
        sim.first_cycle_step()
        self.assertEqual(sim.state.visualisation_values.alu_out, None)
        self.assertEqual(sim.state.visualisation_values.ram_out, None)
        self.assertEqual(sim.state.visualisation_values.jump, True)
        sim.second_cycle_step()

    def test_cycle_steps(self):
        sim = ToySimulation()
        self.assertEqual(sim.state.loaded_instruction, None)
        self.assertTrue(sim.is_done())
        self.assertEqual(sim.state.program_counter, 1)
        sim.load_program("")
        self.assertEqual(sim.state.max_pc, -1)
        self.assertEqual(sim.state.loaded_instruction, None)
        sim.load_program("INC")
        self.assertEqual(sim.state.max_pc, 0)
        self.assertEqual(sim.state.loaded_instruction, INC())
        sim.first_cycle_step()
        self.assertEqual(sim.state.accu, 1)
        self.assertEqual(sim.state.loaded_instruction, INC())
        self.assertEqual(sim.state.program_counter, 1)
        with self.assertRaises(StepSequenceError):
            sim.first_cycle_step()
        sim.second_cycle_step()
        self.assertEqual(sim.state.loaded_instruction, None)
        self.assertEqual(sim.state.program_counter, 2)
        self.assertTrue(sim.is_done())
