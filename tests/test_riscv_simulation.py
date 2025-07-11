import unittest
import fixedint
from copy import deepcopy

from architecture_simulator.uarch.riscv.register_file import RegisterFile
from architecture_simulator.uarch.memory.memory import (
    Memory,
    MemoryAddressError,
    AddressingType,
)
from architecture_simulator.uarch.memory.instruction_memory import InstructionMemory
from architecture_simulator.uarch.riscv.riscv_architectural_state import (
    RiscvArchitecturalState,
)
from architecture_simulator.simulation.riscv_simulation import RiscvSimulation
from architecture_simulator.isa.riscv.rv32i_instructions import ADDI, BNE, BEQ, JAL, LW
from architecture_simulator.uarch.riscv.pipeline import InstructionExecutionException


class TestRiscvSimulation(unittest.TestCase):
    def test_simulation(self):
        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                register_file=RegisterFile(registers=[0, 2, 0, 0]),
                memory=Memory(AddressingType.BYTE, 32),
            )
        )
        simulation.load_program("add x0, x0, x1\nadd x0, x0, x1")
        # simulation.append_instructions("sub x0, x0, x1")
        simulation.step()
        self.assertEqual(simulation.state.register_file.registers[0], 2)
        simulation.step()
        self.assertEqual(simulation.state.register_file.registers[0], 4)
        # simulation.step_simulation()
        # self.assertEqual(simulation.state.register_file.registers[0], 2)

    def test_simulation_jal(self):
        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                register_file=RegisterFile(registers=[0, 2, 0, 0]),
                memory=Memory(AddressingType.BYTE, 32),
            )
        )
        simulation.load_program("nop\nnop\nnop\nnop\njal x1, 8")
        simulation.step()
        simulation.step()
        simulation.step()
        simulation.step()
        jal_instruction = JAL(rd=1, imm=8)
        expected_state = deepcopy(simulation.state)
        expected_state = jal_instruction.behavior(expected_state)
        simulation.step()
        self.assertEqual(simulation.state.register_file.registers[1], 20)
        self.assertEqual(
            simulation.state.program_counter, expected_state.program_counter + 4
        )

    def test_simulation_jal_fivestage(self):
        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                pipeline_mode="five_stage_pipeline",
                register_file=RegisterFile(registers=[0, 2, 0, 0]),
                memory=Memory(AddressingType.BYTE, 32),
            ),
        )
        simulation.load_program("nop\nnop\nnop\nnop\njal x1, -8")
        # simulation.append_instructions("sub x0, x0, x1")
        simulation.step()
        simulation.step()
        simulation.step()
        simulation.step()
        jal_instruction = JAL(rd=1, imm=-8)
        expected_state = deepcopy(simulation.state)
        expected_state = jal_instruction.behavior(expected_state)
        simulation.step()
        simulation.step()
        simulation.step()
        simulation.step()
        self.assertEqual(
            simulation.state.program_counter, expected_state.program_counter + 4
        )
        simulation.step()
        simulation.step()
        self.assertEqual(simulation.state.register_file.registers[1], 20)

    def test_run_simulation(self):
        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                register_file=RegisterFile(registers=[0, 0, 0, 0])
            ),
        )
        simulation.state.instruction_memory.instructions = {
            0: ADDI(rd=1, rs1=1, imm=1),
            4: ADDI(rd=1, rs1=1, imm=1),
            8: ADDI(rd=1, rs1=1, imm=1),
            12: ADDI(rd=1, rs1=1, imm=1),
            16: ADDI(rd=1, rs1=1, imm=1),
            20: ADDI(rd=1, rs1=1, imm=1),
            24: ADDI(rd=1, rs1=1, imm=1),
        }
        simulation.run()
        self.assertEqual(int(simulation.state.register_file.registers[1]), 7)
        self.assertEqual(simulation.state.performance_metrics.branch_count, 0)
        self.assertEqual(simulation.state.performance_metrics.instruction_count, 7)
        self.assertEqual(simulation.state.performance_metrics.procedure_count, 0)
        self.assertGreater(simulation.state.performance_metrics._execution_time_s, 0)

        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                register_file=RegisterFile(registers=[0, 0, 0, 0])
            )
        )

        simulation.run()
        self.assertEqual(int(simulation.state.register_file.registers[0]), 0)
        self.assertEqual(simulation.state.performance_metrics.branch_count, 0)
        self.assertEqual(simulation.state.performance_metrics.instruction_count, 0)
        self.assertEqual(simulation.state.performance_metrics.procedure_count, 0)
        self.assertGreaterEqual(
            simulation.state.performance_metrics._execution_time_s, 0
        )

        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                register_file=RegisterFile(registers=[0, 0, 0, 0])
            ),
        )
        simulation.state.instruction_memory.instructions = {
            0: ADDI(rd=2, rs1=0, imm=5),
            4: ADDI(rd=1, rs1=1, imm=1),
            8: BNE(rs1=1, rs2=2, imm=-4),
            12: BEQ(rs1=0, rs2=0, imm=8),
            16: ADDI(rd=0, rs1=0, imm=0),
            20: ADDI(rd=3, rs1=0, imm=64),
        }
        simulation.run()
        self.assertEqual(simulation.state.register_file.registers, [0, 5, 5, 64])
        self.assertEqual(simulation.state.performance_metrics.branch_count, 5)
        self.assertEqual(simulation.state.performance_metrics.instruction_count, 13)
        self.assertEqual(simulation.state.performance_metrics.procedure_count, 0)
        self.assertGreater(simulation.state.performance_metrics._execution_time_s, 0)

        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                register_file=RegisterFile(registers=[0, 0, 0, 0])
            ),
        )
        simulation.state.instruction_memory.instructions = {
            0: ADDI(rd=2, rs1=0, imm=33),
            4: ADDI(rd=1, rs1=1, imm=1),
            8: ADDI(rd=1, rs1=1, imm=1),
            12: ADDI(rd=1, rs1=1, imm=1),
            16: BNE(rs1=1, rs2=2, imm=-12),
        }
        simulation.run()
        self.assertEqual(simulation.state.register_file.registers, [0, 33, 33, 0])
        self.assertEqual(simulation.state.performance_metrics.branch_count, 10)
        self.assertEqual(simulation.state.performance_metrics.instruction_count, 45)
        self.assertEqual(simulation.state.performance_metrics.procedure_count, 0)
        self.assertGreater(simulation.state.performance_metrics._execution_time_s, 0)

        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                register_file=RegisterFile(registers=[0, 0, 0, 0])
            )
        )
        simulation.state.instruction_memory.instructions = {
            0: ADDI(rd=3, rs1=0, imm=8),
            4: JAL(rd=2, imm=8),
            8: ADDI(rd=1, rs1=1, imm=1),
            12: BEQ(rs1=0, rs2=0, imm=4),
            16: JAL(rd=2, imm=4),
            20: ADDI(rd=1, rs1=1, imm=-10),
        }
        simulation.run()
        self.assertEqual(
            simulation.state.register_file.registers, [0, pow(2, 32) - 10, 20, 8]
        )
        self.assertEqual(simulation.state.performance_metrics.branch_count, 1)
        self.assertEqual(simulation.state.performance_metrics.instruction_count, 5)
        self.assertEqual(simulation.state.performance_metrics.procedure_count, 2)
        self.assertGreater(simulation.state.performance_metrics._execution_time_s, 0)

    def test_against_class_variables(self):
        """Some tests against class variables (some things used to be class variables and were thus shared between objects, which was undesired)"""
        simulation1 = RiscvSimulation(
            state=RiscvArchitecturalState(memory=Memory(AddressingType.BYTE, 32))
        )
        simulation2 = RiscvSimulation(
            state=RiscvArchitecturalState(memory=Memory(AddressingType.BYTE, 32))
        )

        simulation1.state.register_file.registers[5] = fixedint.UInt32(12)
        self.assertEqual(int(simulation1.state.register_file.registers[5]), 12)
        self.assertEqual(int(simulation2.state.register_file.registers[5]), 0)

        simulation1.state.instruction_memory.instructions = {
            0: ADDI(rd=5, rs1=12, imm=12)
        }
        self.assertEqual(len(simulation1.state.instruction_memory.instructions), 1)
        self.assertEqual(len(simulation2.state.instruction_memory.instructions), 0)

        simulation1.state.csr_registers.write_byte(address=5, value=fixedint.UInt8(12))
        self.assertEqual(
            (int(simulation1.state.csr_registers.read_byte(address=5))), 12
        )
        self.assertEqual((int(simulation2.state.csr_registers.read_byte(address=5))), 0)

        simulation1.state.performance_metrics.instruction_count = 12
        self.assertEqual(simulation1.state.performance_metrics.instruction_count, 12)
        self.assertEqual(simulation2.state.performance_metrics.instruction_count, 0)

        simulation1.state.memory.write_byte(address=5, value=fixedint.UInt8(12))
        self.assertEqual(int(simulation1.state.memory.read_byte(address=5)), 12)
        self.assertEqual(int(simulation2.state.memory.read_byte(address=5)), 0)

    def test_step_simulation_over(self):
        simulation = RiscvSimulation()
        simulation.state.instruction_memory.instructions = {
            0: ADDI(rd=1, rs1=1, imm=1),
            4: ADDI(rd=1, rs1=1, imm=1),
            8: ADDI(rd=1, rs1=1, imm=1),
            12: ADDI(rd=1, rs1=1, imm=1),
        }

        self.assertTrue(simulation.step())
        self.assertTrue(simulation.step())
        self.assertTrue(simulation.step())
        self.assertTrue(not simulation.step())

    def test_simulation_errors(self):
        simulation = RiscvSimulation()
        simulation.state.instruction_memory.instructions = {
            0: ADDI(rd=1, rs1=1, imm=1),
            4: LW(rd=1, rs1=0, imm=0),
            8: ADDI(rd=1, rs1=1, imm=1),
            12: ADDI(rd=1, rs1=1, imm=1),
        }

        with self.assertRaises(InstructionExecutionException) as cm:
            simulation.run()
        self.assertEqual(
            cm.exception.__repr__(),
            InstructionExecutionException(
                address=4,
                instruction_repr=simulation.state.instruction_memory.instructions[4],
                error_message=MemoryAddressError(
                    address=0,
                    min_address_incl=2**14,
                    max_address_incl=2**32 - 1,
                    memory_type="data memory",
                ).__repr__(),
            ).__repr__(),
        )

    def test_five_stage_simulation(self):
        program = f"""lui a0, 0
        addi a0, a0, 10 # load n
        addi s0, zero, 1 # load 1 for comparison
        addi sp, zero, 1024 # adjust sp
        jal ra, Fib # fib(n)
        beq zero, zero, End # go to end
        Fib:
        bgeu s0, a0, FibReturn # n <= 1
        addi sp, sp, -8 # adjust sp for ra and n
        sw ra, 4(sp) # store ra
        sw a0, 0(sp) # store n
        addi a0, a0, -1 # a0 = n - 1
        jal ra, Fib
        lw t0, 0(sp) # restore argument
        sw a0, 0(sp) # store return value (fib(n-1))
        addi a0, t0, -2 # a0 = n - 2
        jal ra, Fib
        lw t0, 0(sp) # t0 = fib(n-1)
        lw ra, 4(sp) # restore ra
        addi sp, sp, 8 # return sp to original size
        add a0, a0, t0 # a0 = fib(n-2) + fib(n-1)
        FibReturn:
        jalr zero, ra, 0
        End:"""

        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                register_file=RegisterFile(), memory=Memory(AddressingType.BYTE, 32)
            ),
            mode="five_stage_pipeline",
        )
        simulation.load_program(program)
        simulation.run()
        self.assertEqual(simulation.state.register_file.registers[10], 55)

    def test_five_stage_performance_metrics_1(self):
        simulation = RiscvSimulation(mode="five_stage_pipeline")
        programm = """
        addi x1, x0, 4
        label:
        addi x1, x1, -1
        bne x0, x1, label
        jal x0, test
        test:
        """
        simulation.load_program(program=programm)
        simulation.run()
        self.assertGreater(simulation.state.performance_metrics._execution_time_s, 0)
        self.assertEqual(simulation.state.performance_metrics.instruction_count, 10)
        self.assertEqual(simulation.state.performance_metrics.branch_count, 3)
        self.assertEqual(simulation.state.performance_metrics.procedure_count, 1)

    def test_five_stage_performance_metrics_2(self):
        simulation = RiscvSimulation(mode="five_stage_pipeline")
        programm = """
        add x0, x0, x0
        addi x1, x1, 1
        add x1, x1, x1
        add x0, x0, x0
        add x0, x0, x0
        beq x0, x0, label
        label:
        """
        simulation.load_program(program=programm)
        simulation.run()
        self.assertEqual(simulation.state.performance_metrics.flushes, 1)
        self.assertEqual(simulation.state.performance_metrics.stalls, 1)
        self.assertEqual(simulation.state.performance_metrics.cycles, 12)

    def test_off_by_one_fix(self):
        simulation = RiscvSimulation(mode="five_stage_pipeline")
        programm = """
        add x0, x0, x0
        """
        simulation.load_program(program=programm)
        simulation.run()
        self.assertEqual(simulation.state.performance_metrics.cycles, 5)

    def test_singele_stage_cycles(self):
        simulation = RiscvSimulation()
        programm = """
        add x0, x0, x0
        """
        simulation.load_program(program=programm)
        simulation.run()
        self.assertEqual(simulation.state.performance_metrics.cycles, 1)

    def test_turn_off_detect_data_hazards(self):
        simulation = RiscvSimulation(
            detect_data_hazards=False, mode="five_stage_pipeline"
        )
        programm = """
        addi x1, x0, 15
        add x0, x0, x0
        addi x1, x1, 1
        add x0, x0, x0
        add x0, x0, x0
        addi x2, x0, 7
        addi x2, x2, 2
        add x0, x0, x0
        add x0, x0, x0
        addi x2, x2, 1
        """
        simulation.load_program(program=programm)
        simulation.run()
        self.assertEqual(simulation.state.register_file.registers[1], 1)
        self.assertEqual(simulation.state.register_file.registers[2], 3)
        self.assertEqual(simulation.state.performance_metrics.flushes, 0)
        self.assertEqual(simulation.state.performance_metrics.cycles, 14)
        self.assertEqual(simulation.state.performance_metrics.instruction_count, 10)

    def test_five_stage_performance_metrics_3(self):
        simulation = RiscvSimulation(
            detect_data_hazards=True, mode="five_stage_pipeline"
        )
        programm = """
    	# multiplication
        addi x1, x0, 16 # x
        addi x2, x0, 10 # y
        loop:
        add x3, x3, x1
        addi x2, x2, -1
        bne x2, zero, loop
        """
        simulation.load_program(program=programm)
        simulation.run()
        self.assertEqual(simulation.state.register_file.registers[3], 160)
        self.assertEqual(simulation.state.performance_metrics.instruction_count, 32)
        self.assertEqual(simulation.state.performance_metrics.branch_count, 9)
        self.assertEqual(simulation.state.performance_metrics.flushes, 9)
        self.assertEqual(simulation.state.performance_metrics.stalls, 11)

    def test_has_started(self):
        sim = RiscvSimulation()
        self.assertTrue(not sim.has_started)
        sim.load_program("NOP\nADDI x1, x0, 3")
        self.assertTrue(not sim.has_started)
        sim.step()
        self.assertTrue(sim.has_started)
        sim.step()
        self.assertTrue(sim.has_started)
