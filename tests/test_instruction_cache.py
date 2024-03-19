from unittest import TestCase

from architecture_simulator.uarch.memory.instruction_memory_cache_system import (
    InstructionMemoryCacheSystem,
)
from architecture_simulator.uarch.memory.instruction_memory import InstructionMemory
from architecture_simulator.isa.riscv.rv32i_instructions import ADDI
from architecture_simulator.uarch.riscv.riscv_performance_metrics import (
    RiscvPerformanceMetrics,
)


class TestCache(TestCase):
    def test_case_1(self):
        instr_mem = InstructionMemory()
        mem_sys = InstructionMemoryCacheSystem(
            instr_mem, 2, 0, 1, RiscvPerformanceMetrics()
        )

        mem_sys.write_instructions([ADDI(0, 0, i * 4) for i in range(32)])
        mem_sys.read_instruction(0)
        mem_sys.read_instruction(4)
        mem_sys.read_instruction(8)
        mem_sys.read_instruction(12)
        mem_sys.read_instruction(16)
        mem_sys.read_instruction(4)
        mem_sys.read_instruction(8)
        mem_sys.read_instruction(12)

        self.assertEqual(mem_sys.accesses, 8)
        self.assertEqual(mem_sys.hits, 3)

    def test_case_2(self):
        instr_mem = InstructionMemory()
        mem_sys = InstructionMemoryCacheSystem(
            instr_mem, 1, 3, 1, RiscvPerformanceMetrics()
        )

        mem_sys.write_instructions([ADDI(0, 0, i * 4) for i in range(32)])

        mem_sys.read_instruction(0)
        mem_sys.read_instruction(4)
        mem_sys.read_instruction(8)
        mem_sys.read_instruction(12)
        mem_sys.read_instruction(16)
        mem_sys.read_instruction(20)
        mem_sys.read_instruction(24)
        mem_sys.read_instruction(28)

        mem_sys.read_instruction(32)
        mem_sys.read_instruction(60)

        mem_sys.read_instruction(64)

        mem_sys.read_instruction(0)

        self.assertEqual(mem_sys.accesses, 12)
        self.assertEqual(mem_sys.hits, 8)

    def test_case_3(self):
        instr_mem = InstructionMemory()
        mem_sys = InstructionMemoryCacheSystem(
            instr_mem, 0, 0, 4, RiscvPerformanceMetrics()
        )

        mem_sys.write_instructions([ADDI(0, 0, i * 4) for i in range(32)])

        mem_sys.read_instruction(0)
        mem_sys.read_instruction(4)
        mem_sys.read_instruction(8)
        mem_sys.read_instruction(12)
        mem_sys.read_instruction(0)
        mem_sys.read_instruction(16)
        mem_sys.read_instruction(12)

        self.assertEqual(mem_sys.accesses, 7)
        self.assertEqual(mem_sys.hits, 2)
