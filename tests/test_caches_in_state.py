from unittest import TestCase

from architecture_simulator.simulation.riscv_simulation import RiscvSimulation
from architecture_simulator.uarch.riscv.riscv_architectural_state import (
    RiscvArchitecturalState,
)
from architecture_simulator.uarch.memory.write_through_memory_system import (
    WriteThroughMemorySystem,
)
from architecture_simulator.uarch.memory.write_back_memory_system import (
    WriteBackMemorySystem,
)
from architecture_simulator.uarch.memory.instruction_memory_cache_system import (
    InstructionMemoryCacheSystem,
)
from architecture_simulator.uarch.memory.instruction_memory import InstructionMemory
from architecture_simulator.uarch.memory.memory import Memory
from architecture_simulator.uarch.memory.memory import AddressingType
from architecture_simulator.uarch.riscv.riscv_performance_metrics import (
    RiscvPerformanceMetrics,
)
from architecture_simulator.uarch.memory.cache import CacheOptions
from tests.riscv_programs.fibonacci_recursive import get_fibonacci_recursive


class TestCache(TestCase):
    def test_instr_cache1(self):
        test_code = """addi a0, zero, 10 # load n
addi s0, zero, 1 # load 1 for comparison
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
End: nop"""

        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                instruction_memory=InstructionMemoryCacheSystem(
                    InstructionMemory(), 1, 2, 1, RiscvPerformanceMetrics()
                )
            )
        )

        simulation.load_program(test_code)
        simulation.run()

        self.assertEqual(
            simulation.state.instruction_memory.get_cache_stats()["hits"], "1144"
        )

    def test_instr_cache2(self):
        test_code = """addi x1, x0, 1
        addi x1, x0, 2
        addi x1, x0, 3
        addi x1, x0, 4
        addi x1, x0, 5
        addi x1, x0, 6
        addi x1, x0, 7
        addi x1, x0, 8"""

        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                instruction_memory=InstructionMemoryCacheSystem(
                    InstructionMemory(), 2, 1, 1, RiscvPerformanceMetrics()
                )
            )
        )

        simulation.load_program(test_code)
        simulation.run()

        self.assertEqual(
            simulation.state.instruction_memory.get_cache_stats()["hits"], "4"
        )
        self.assertEqual(
            simulation.state.instruction_memory.get_cache_stats()["accesses"], "8"
        )

    def test_instr_cache3(self):
        test_code = """addi x2, x0, 2
        start: nop
        nop
        addi x1, x1, 1
        blt x1, x2, start
        """

        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                instruction_memory=InstructionMemoryCacheSystem(
                    InstructionMemory(), 2, 0, 1, RiscvPerformanceMetrics()
                )
            )
        )

        simulation.load_program(test_code)
        simulation.run()

        self.assertEqual(
            simulation.state.instruction_memory.get_cache_stats()["hits"], "4"
        )
        self.assertEqual(
            simulation.state.instruction_memory.get_cache_stats()["accesses"], "9"
        )

    def test_instr_cache4(self):
        test_code = """addi x2, x0, 2
        start: nop
        nop
        addi x1, x1, 1
        blt x1, x2, start
        """

        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                instruction_memory=InstructionMemoryCacheSystem(
                    InstructionMemory(), 0, 0, 4, RiscvPerformanceMetrics()
                )
            )
        )

        simulation.load_program(test_code)
        simulation.run()

        self.assertEqual(
            simulation.state.instruction_memory.get_cache_stats()["hits"], "4"
        )
        self.assertEqual(
            simulation.state.instruction_memory.get_cache_stats()["accesses"], "9"
        )

    def test_instr_cache5(self):
        test_code = """addi a0, zero, 10 # load n
addi s0, zero, 1 # load 1 for comparison
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
End: nop"""

        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                instruction_memory=InstructionMemoryCacheSystem(
                    InstructionMemory(), 0, 1, 4, RiscvPerformanceMetrics()
                )
            )
        )

        simulation.load_program(test_code)
        simulation.run()

        self.assertEqual(
            simulation.state.instruction_memory.get_cache_stats()["hits"], "1057"
        )
        self.assertEqual(
            simulation.state.instruction_memory.get_cache_stats()["accesses"], "1503"
        )
        self.assertEqual(
            simulation.state.instruction_memory.get_cache_stats()["accesses"],
            str(simulation.state.performance_metrics.instruction_count),
        )

    def test_data_cache1(self):
        test_code = """.data
my_data_arr: .word 0,1,2,3,4,5,6,7,8,9
.text
la x1, my_data_arr
lw x0, 4(x1)
lw x0, 4(x1)
lw x0, 4(x1)
lw x0, 4(x1)
lw x0, 4(x1)
lw x0, 4(x1)
lw x0, 4(x1)
lw x0, 4(x1)
lw x0, 4(x1)
lw x0, 4(x1)
"""

        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                memory=WriteThroughMemorySystem(
                    Memory(AddressingType.BYTE, 32), 1, 2, 2, RiscvPerformanceMetrics()
                )
            )
        )

        simulation.load_program(test_code)
        simulation.run()

        self.assertEqual(simulation.state.memory.get_cache_stats()["hits"], "9")
        self.assertEqual(simulation.state.memory.get_cache_stats()["accesses"], "10")

    def test_data_cache2(self):
        test_code = """.data
my_data_arr: .word 0,1,2,3,4,5,6,7,8,9
.text
la x1, my_data_arr
lw x0, 0(x1)
lw x0, 4(x1)
lw x0, 8(x1)
lw x0, 12(x1)
lw x0, 16(x1)
lw x0, 0(x1)
lw x0, 8(x1)
lw x0, 12(x1)
"""

        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                memory=WriteThroughMemorySystem(
                    Memory(AddressingType.BYTE, 32), 0, 0, 4, RiscvPerformanceMetrics()
                )
            )
        )

        simulation.load_program(test_code)
        simulation.run()

        self.assertEqual(simulation.state.memory.get_cache_stats()["hits"], "2")
        self.assertEqual(simulation.state.memory.get_cache_stats()["accesses"], "8")

    def test_data_cache3(self):
        test_code = """.data
my_data_arr: .word 0,1,2,3,4,5,6,7,8,9
.text
la x1, my_data_arr
lw x0, 0(x1)
lw x0, 8(x1)
lw x0, 16(x1)
lw x0, 24(x1)
lw x0, 4(x1)
lw x0, 12(x1)
lw x0, 20(x1)
lw x0, 28(x1)
lw x0, 32(x1)
lw x0, 0(x1)
lw x0, 16(x1)
lw x0, 20(x1)
"""

        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                memory=WriteThroughMemorySystem(
                    Memory(AddressingType.BYTE, 32),
                    0,
                    1,
                    4,
                    performance_metrics=RiscvPerformanceMetrics(),
                    miss_penality=3,
                )
            )
        )
        # TODO: Change me once configuration is possible
        simulation.state.memory.performance_metrics = (
            simulation.state.performance_metrics
        )

        simulation.load_program(test_code)
        simulation.run()

        self.assertEqual(simulation.state.memory.get_cache_stats()["hits"], "6")
        self.assertEqual(simulation.state.memory.get_cache_stats()["accesses"], "12")
        self.assertEqual(simulation.state.performance_metrics.cycles, 32)

    def test_instr_cache_miss_penality_1(self):
        test_code = """
add x0, x0, x0
add x0, x0, x0
add x0, x0, x0
add x0, x0, x0
add x0, x0, x0
add x0, x0, x0
add x0, x0, x0
add x0, x0, x0
"""

        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                instruction_memory=InstructionMemoryCacheSystem(
                    InstructionMemory(),
                    1,
                    1,
                    1,
                    RiscvPerformanceMetrics(),
                    7,
                )
            )
        )

        # TODO: Change me once configuration is possible
        simulation.state.instruction_memory.performance_metrics = (
            simulation.state.performance_metrics
        )

        simulation.load_program(test_code)
        simulation.run()

        self.assertEqual(
            simulation.state.instruction_memory.get_cache_stats()["hits"], "4"
        )
        self.assertEqual(
            simulation.state.instruction_memory.get_cache_stats()["accesses"], "8"
        )
        self.assertEqual(simulation.state.performance_metrics.cycles, 36)

    def test_write_back_dirty_on_write(self):
        # Regression test for a bug where a write miss would not set the dirty bit
        # in a write back cache system
        simulation = RiscvSimulation(
            state=RiscvArchitecturalState(
                memory=WriteBackMemorySystem(
                    Memory(AddressingType.BYTE, 32), 1, 0, 1, RiscvPerformanceMetrics()
                )
            )
        )

        simulation.load_program(
            """
li x1, 0x4000

li x2, 80
sw x2, 8(x1)

li x2, 160
sw x2, 16(x1)

lw x3, 8(x1)
"""
        )
        simulation.run()
        self.assertEqual(simulation.state.register_file.registers[3], 80)

    def test_fibonacci_write_through(self):
        # test on a small cache
        simulation = RiscvSimulation(
            data_cache=CacheOptions(True, 0, 0, 1, "wt", "plru", 0),
            instruction_cache=CacheOptions(True, 0, 0, 1, "wt", "plru", 0),
        )
        simulation.load_program(get_fibonacci_recursive(10))
        simulation.run()
        self.assertEqual(simulation.state.register_file.registers[10], 55)

        # test on a larger cache
        simulation = RiscvSimulation(
            data_cache=CacheOptions(True, 1, 1, 2, "wt", "plru", 0),
            instruction_cache=CacheOptions(True, 1, 1, 2, "wt", "plru", 0),
        )
        simulation.load_program(get_fibonacci_recursive(10))
        simulation.run()
        self.assertEqual(simulation.state.register_file.registers[10], 55)

    def test_fibonacci_write_back(self):
        simulation = RiscvSimulation(
            data_cache=CacheOptions(True, 0, 0, 1, "wb", "plru", 0),
            instruction_cache=CacheOptions(True, 0, 0, 1, "wb", "plru", 0),
        )
        simulation.load_program(get_fibonacci_recursive(10))
        simulation.run()
        self.assertEqual(simulation.state.register_file.registers[10], 55)

        # test on a larger cache
        simulation = RiscvSimulation(
            data_cache=CacheOptions(True, 1, 1, 2, "wb", "plru", 0),
            instruction_cache=CacheOptions(True, 1, 1, 2, "wb", "plru", 0),
        )
        simulation.load_program(get_fibonacci_recursive(10))
        simulation.run()
        self.assertEqual(simulation.state.register_file.registers[10], 55)
