import unittest
import fixedint
from architecture_simulator.uarch.architectural_state import ArchitecturalState
from architecture_simulator.uarch.pipeline import (
    Pipeline,
    InstructionFetchStage,
    InstructionDecodeStage,
    ExecuteStage,
    MemoryAccessStage,
    RegisterWritebackStage,
    SingleStage,
)
from architecture_simulator.isa.parser import RiscvParser


class TestPipeline(unittest.TestCase):
    def test_rtypes(self):
        program = """add x1, x1, x2
        add x4, x5, x6
        sub x7, x8, x9"""
        pipeline = Pipeline(
            [
                InstructionFetchStage(),
                InstructionDecodeStage(),
                ExecuteStage(),
                MemoryAccessStage(),
                RegisterWritebackStage(),
            ],
            [0, 4, 1, 2, 3],
            state=ArchitecturalState(),
        )
        pipeline.state.instruction_memory.append_instructions(program)
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(5)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(8)
        pipeline.state.register_file.registers[5] = fixedint.MutableUInt32(32)
        pipeline.state.register_file.registers[6] = fixedint.MutableUInt32(20)
        pipeline.state.register_file.registers[8] = fixedint.MutableUInt32(32)
        pipeline.state.register_file.registers[9] = fixedint.MutableUInt32(20)
        for _ in range(20):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(13)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(52)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7], fixedint.MutableUInt32(12)
        )

    def test_data_hazard(self):
        program = """add x1, x0, x2
        add x0, x0, x0
        sll x3, x1, x2
        add x7, x0, x8
        add x0, x0, x0
        add x0, x0, x0
        sll x9, x7, x8
        """
        pipeline = Pipeline(
            [
                InstructionFetchStage(),
                InstructionDecodeStage(),
                ExecuteStage(),
                MemoryAccessStage(),
                RegisterWritebackStage(),
            ],
            [0, 4, 1, 2, 3],
            state=ArchitecturalState(),
        )
        pipeline.state.instruction_memory.append_instructions(program)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(2)
        pipeline.state.register_file.registers[8] = fixedint.MutableUInt32(2)
        for _ in range(20):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(2)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[3], fixedint.MutableUInt32(0)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7], fixedint.MutableUInt32(2)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[9], fixedint.MutableUInt32(8)
        )

    def test_single_stage(self):
        pipeline = Pipeline(
            [SingleStage()],
            [0],
            state=ArchitecturalState(),
        )
        n = 10
        pipeline.state.instruction_memory.append_instructions(
            f"""lui a0, 0
addi a0, a0, {n} # load n
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
End:"""
        )
        for _ in range(2000):
            pipeline.step()
        self.assertEqual(pipeline.state.register_file.registers[10], 55)
