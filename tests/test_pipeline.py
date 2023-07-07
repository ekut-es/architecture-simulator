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
    def assert_steps(self, pipeline: Pipeline, steps: int):
        """Execute the given amount of steps on the pipeline and assert the pipeline is finished after exactly that amount of steps and not earlier or later.
            Note: Internally, it does (n+1) steps because it takes one more step to clear the last pipeline register. This doesn't change the behavior of the method.
        Args:
            pipeline (Pipeline): pipeline to test.
            steps (int): number of steps needed to finish the pipeline.
        """
        for step in range(steps):
            pipeline.step()
            self.assert_(
                not pipeline.is_done(), f"Pipeline already finished after {step} steps."
            )
        pipeline.step()
        self.assert_(pipeline.is_done(), "Pipeline has not yet finished.")

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
        for _ in range(100):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(2)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[3], fixedint.MutableUInt32(8)
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

    def test_stypes(self):
        program = """sb x2, 0(x1)
        sh x3, 4(x1)
        sw x4, 8(x1)
        sb x5, 12(x1)
        sb x5, 13(x1)
        sb x5, 14(x1)
        sb x5, 15(x1)
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(2**16)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(2**8 - 1)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(2**16 - 1)
        pipeline.state.register_file.registers[4] = fixedint.MutableUInt32(2**32 - 1)
        pipeline.state.register_file.registers[5] = fixedint.MutableUInt32(2**7)
        self.assert_steps(pipeline=pipeline, steps=11)
        self.assertEqual(
            pipeline.state.memory.load_byte(2**16), fixedint.MutableUInt8(2**8 - 1)
        )
        self.assertEqual(
            pipeline.state.memory.load_halfword(2**16 + 4),
            fixedint.MutableUInt16(2**16 - 1),
        )
        self.assertEqual(
            pipeline.state.memory.load_word(2**16 + 8),
            fixedint.MutableUInt32(2**32 - 1),
        )
        self.assertEqual(
            pipeline.state.memory.load_word(2**16 + 12),
            fixedint.MutableUInt32(2**7 + 2**15 + 2**23 + 2**31),
        )

    def test_data_hazard_handling_2(self):
        program = """
        add x0, x0, x0
        add x2, x1, x1
        add x3, x2, x2
        add x4, x3, x3
        add x0, x0, x0
        sub x5, x2, x3
        add x0, x0, x0
        add x0, x0, x0
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(7)

        self.assert_steps(pipeline=pipeline, steps=16)
        self.assertEqual(
            pipeline.state.register_file.registers[2], fixedint.MutableUInt32(14)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[3], fixedint.MutableUInt32(28)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(56)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[5], fixedint.MutableUInt32(-14)
        )

    def test_data_hazard_handling_and_branch(self):
        program = """
        start:
        add x2, x2, x2
        sub x3, x3, x1
        sub x3, x3, x1
        add x3, x3, x1
        blt x0, x3, start
        add x2, x2, x1
        sub x2, x2, x1
        end:
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(10)
        self.assert_steps(pipeline=pipeline, steps=145)
        self.assertEqual(
            pipeline.state.register_file.registers[2], fixedint.MutableUInt32(2**10)
        )

    def test_btypes(self):
        # 0 < 0
        program = """add x1, x0, x2
        blt x0, x0, 8
        add x3, x0, x2
        add x4, x0, x2
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
        for _ in range(8):
            pipeline.step()
        self.assertEqual(pipeline.state.register_file.registers[1], 2)
        self.assertEqual(pipeline.state.register_file.registers[2], 2)
        self.assertEqual(pipeline.state.register_file.registers[3], 2)
        self.assertEqual(pipeline.state.register_file.registers[4], 2)

        # 0 == 0
        program = """add x1, x0, x2
        beq x0, x0, 8
        add x3, x0, x2
        add x4, x0, x2"""
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
        self.assert_steps(pipeline=pipeline, steps=10)
        self.assertEqual(pipeline.state.register_file.registers[1], 2)
        self.assertEqual(pipeline.state.register_file.registers[2], 2)
        self.assertEqual(
            pipeline.state.register_file.registers[3], 0
        )  # add x3, x0, x2 should have been skipped
        self.assertEqual(pipeline.state.register_file.registers[4], 2)

    def test_beq(self):
        # 0 == 0
        program = """add x1, x0, x2
        beq x0, x0, 8
        add x3, x0, x2
        add x4, x0, x2"""
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
        self.assert_steps(pipeline=pipeline, steps=10)
        self.assertEqual(pipeline.state.register_file.registers[1], 2)
        self.assertEqual(pipeline.state.register_file.registers[2], 2)
        self.assertEqual(
            pipeline.state.register_file.registers[3], 0
        )  # add x3, x0, x2 should have been skipped
        self.assertEqual(pipeline.state.register_file.registers[4], 2)

        # 0 == 2
        program = """add x1, x0, x2
        beq x0, x2, 8
        add x3, x0, x2
        add x4, x0, x2"""
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
        self.assert_steps(pipeline=pipeline, steps=8)
        self.assertEqual(pipeline.state.register_file.registers[1], 2)
        self.assertEqual(pipeline.state.register_file.registers[2], 2)
        self.assertEqual(pipeline.state.register_file.registers[3], 2)
        self.assertEqual(pipeline.state.register_file.registers[4], 2)

    def test_bne(self):
        # 8 != 2
        program = """add x1, x0, x2
        bne x3, x2, 8
        add x3, x0, x2
        add x4, x0, x2"""
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
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(8)
        self.assert_steps(pipeline=pipeline, steps=10)
        self.assertEqual(pipeline.state.register_file.registers[1], 2)
        self.assertEqual(pipeline.state.register_file.registers[2], 2)
        self.assertEqual(pipeline.state.register_file.registers[3], 8)
        self.assertEqual(pipeline.state.register_file.registers[4], 2)

        # 8 != 8
        program = """add x1, x0, x3
        add x0, x0, x0
        add x0, x0, x0
        bne x1, x3, 8
        add x3, x0, x2
        add x4, x0, x2"""
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
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(8)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(8)
        self.assert_steps(pipeline=pipeline, steps=10)
        self.assertEqual(pipeline.state.register_file.registers[1], 8)
        self.assertEqual(pipeline.state.register_file.registers[2], 8)
        self.assertEqual(pipeline.state.register_file.registers[3], 8)
        self.assertEqual(pipeline.state.register_file.registers[4], 8)

    def test_blt(self):
        # 0 < 1
        program = """blt x0, x1, 8
        add x2, x1, x1
        add x3, x1, x1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=9)
        self.assertEqual(pipeline.state.register_file.registers[1], 1)
        self.assertEqual(pipeline.state.register_file.registers[2], 0)
        self.assertEqual(pipeline.state.register_file.registers[3], 2)

        # -1 < 0
        program = """blt x1, x0, 8
        add x2, x1, x1
        sub x3, x0, x1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(-1)
        self.assert_steps(pipeline=pipeline, steps=9)
        self.assertEqual(pipeline.state.register_file.registers[1], 2**32 - 1)
        self.assertEqual(pipeline.state.register_file.registers[2], 0)
        self.assertEqual(pipeline.state.register_file.registers[3], 1)

        # 0 < 0
        program = """blt x0, x0, 8
        add x2, x1, x1
        add x3, x1, x1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=7)
        self.assertEqual(pipeline.state.register_file.registers[1], 1)
        self.assertEqual(pipeline.state.register_file.registers[2], 2)
        self.assertEqual(pipeline.state.register_file.registers[3], 2)

    def test_bge(self):
        # 0 >= 0
        program = """bge x0, x0, 8
        add x2, x1, x1
        add x3, x1, x1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=9)
        self.assertEqual(pipeline.state.register_file.registers[1], 1)
        self.assertEqual(pipeline.state.register_file.registers[2], 0)
        self.assertEqual(pipeline.state.register_file.registers[3], 2)

        # 1 >= 0
        program = """bge x1, x0, 8
        add x2, x1, x1
        add x3, x1, x1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=9)
        self.assertEqual(pipeline.state.register_file.registers[1], 1)
        self.assertEqual(pipeline.state.register_file.registers[2], 0)
        self.assertEqual(pipeline.state.register_file.registers[3], 2)

        # 0 >= 1
        program = """bge x0, x1, 8
        add x2, x1, x1
        add x3, x1, x1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=7)
        self.assertEqual(pipeline.state.register_file.registers[1], 1)
        self.assertEqual(pipeline.state.register_file.registers[2], 2)
        self.assertEqual(pipeline.state.register_file.registers[3], 2)

        # 0 >= -1
        program = """bge x0, x1, 8
        add x2, x5, x5
        add x3, x5, x5"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[5] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=9)
        self.assertEqual(pipeline.state.register_file.registers[1], fixedint.UInt32(-1))
        self.assertEqual(pipeline.state.register_file.registers[2], 0)
        self.assertEqual(pipeline.state.register_file.registers[3], 2)

    def test_bltu(self):
        # 0 < 1
        program = """bltu x0, x1, 8
        add x2, x1, x1
        add x3, x1, x1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=9)
        self.assertEqual(pipeline.state.register_file.registers[1], 1)
        self.assertEqual(pipeline.state.register_file.registers[2], 0)
        self.assertEqual(pipeline.state.register_file.registers[3], 2)

        # 2**32 - 1 < 0
        program = """bltu x1, x0, 8
        add x2, x5, x5
        sub x3, x0, x1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[5] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=7)
        self.assertEqual(pipeline.state.register_file.registers[1], 2**32 - 1)
        self.assertEqual(pipeline.state.register_file.registers[2], 2)
        self.assertEqual(pipeline.state.register_file.registers[3], 1)

        # 0 < 0
        program = """bltu x0, x0, 8
        add x2, x1, x1
        add x3, x1, x1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=7)
        self.assertEqual(pipeline.state.register_file.registers[1], 1)
        self.assertEqual(pipeline.state.register_file.registers[2], 2)
        self.assertEqual(pipeline.state.register_file.registers[3], 2)

    def test_bgeu(self):
        # 0 >= 0
        program = """bgeu x0, x0, 8
        add x2, x1, x1
        add x3, x1, x1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=9)
        self.assertEqual(pipeline.state.register_file.registers[1], 1)
        self.assertEqual(pipeline.state.register_file.registers[2], 0)
        self.assertEqual(pipeline.state.register_file.registers[3], 2)

        # 1 >= 0
        program = """bgeu x1, x0, 8
        add x2, x1, x1
        add x3, x1, x1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=9)
        self.assertEqual(pipeline.state.register_file.registers[1], 1)
        self.assertEqual(pipeline.state.register_file.registers[2], 0)
        self.assertEqual(pipeline.state.register_file.registers[3], 2)

        # 0 >= 1
        program = """bgeu x0, x1, 8
        add x2, x1, x1
        add x3, x1, x1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=7)
        self.assertEqual(pipeline.state.register_file.registers[1], 1)
        self.assertEqual(pipeline.state.register_file.registers[2], 2)
        self.assertEqual(pipeline.state.register_file.registers[3], 2)

        # 0 >= 2**32 - 1
        program = """bgeu x0, x1, 8
        add x2, x5, x5
        add x3, x5, x5"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[5] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=7)
        self.assertEqual(pipeline.state.register_file.registers[1], fixedint.UInt32(-1))
        self.assertEqual(pipeline.state.register_file.registers[2], 2)
        self.assertEqual(pipeline.state.register_file.registers[3], 2)

    def test_jal(self):
        program = """jal x2, 8
        add x1, x1, x1
        add x3, x1, x1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=9)
        self.assertEqual(pipeline.state.register_file.registers[1], 1)
        self.assertEqual(pipeline.state.register_file.registers[2], 4)
        self.assertEqual(pipeline.state.register_file.registers[3], 2)

        program = """jal x2, 4
        add x1, x1, x1
        add x3, x1, x1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=12)
        self.assertEqual(pipeline.state.register_file.registers[1], 2)
        self.assertEqual(pipeline.state.register_file.registers[2], 4)
        self.assertEqual(pipeline.state.register_file.registers[3], 4)

        program = """add x8, x0, x0
        add x9, x0, x0
        jal x2, Bananenbrot
        jal x3, Kaesekuchen
        add x6, x1, x1
        Bananenbrot:
        add x4, x1, x1
        Kaesekuchen:
        add x5, x1, x1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=12)
        self.assertEqual(pipeline.state.register_file.registers[1], 1)
        self.assertEqual(pipeline.state.register_file.registers[2], 12)
        self.assertEqual(pipeline.state.register_file.registers[3], 0)
        self.assertEqual(pipeline.state.register_file.registers[4], 2)
        self.assertEqual(pipeline.state.register_file.registers[5], 2)
        self.assertEqual(pipeline.state.register_file.registers[6], 0)

        program = """add x8, x0, x0
        add x9, x0, x0
        jal x2, Bananenbrot
        jal x3, Kaesekuchen
        add x1, x1, x1
        Bananenbrot:
        add x4, x1, x1
        Kaesekuchen:
        add x5, x1, x1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        self.assert_steps(pipeline=pipeline, steps=12)
        self.assertEqual(pipeline.state.register_file.registers[1], 1)
        self.assertEqual(pipeline.state.register_file.registers[2], 12)
        self.assertEqual(pipeline.state.register_file.registers[3], 0)
        self.assertEqual(pipeline.state.register_file.registers[4], 2)
        self.assertEqual(pipeline.state.register_file.registers[5], 2)

    def test_jalr(self):
        program = """jalr x2, x1, 20"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(8)
        self.assert_steps(pipeline=pipeline, steps=5)
        self.assertEqual(pipeline.state.program_counter, 28)
        self.assertEqual(pipeline.state.register_file.registers[2], 4)

        program = """add x0, x0, x0
        jalr x2, x1, 13
        add x3, x1, x1
        add x4, x1, x1
        add x5, x1, x1
        add x6, x1, x1
        add x7, x1, x1
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(8)
        self.assert_steps(pipeline=pipeline, steps=11)
        self.assertEqual(pipeline.state.register_file.registers[2], 8)
        self.assertEqual(pipeline.state.register_file.registers[3], 0)
        self.assertEqual(pipeline.state.register_file.registers[4], 0)
        self.assertEqual(pipeline.state.register_file.registers[5], 0)
        self.assertEqual(pipeline.state.register_file.registers[6], 16)
        self.assertEqual(pipeline.state.register_file.registers[7], 16)

    def test_lui(self):
        program = """lui x1, 1
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(8)
        self.assert_steps(pipeline=pipeline, steps=5)
        self.assertEqual(pipeline.state.register_file.registers[1], 4096)

        program = f"""lui x1, 1
        lui x2, 0
        lui x3, {2**20}
        lui x4, {2**20 - 1}
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(8)
        self.assert_steps(pipeline=pipeline, steps=8)
        self.assertEqual(pipeline.state.register_file.registers[1], 4096)
        self.assertEqual(pipeline.state.register_file.registers[2], 0)
        self.assertEqual(pipeline.state.register_file.registers[3], 0)
        self.assertEqual(
            pipeline.state.register_file.registers[4], (2**32 - 1) & ~(2**12 - 1)
        )

    def test_auipc(self):
        program = """auipc x1, 1
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(8)
        self.assert_steps(pipeline=pipeline, steps=5)
        self.assertEqual(pipeline.state.register_file.registers[1], 4096)

        program = f"""add x0, x0, x0
        add x0, x0, x0
        add x0, x0, x0
        auipc x1, 1
        auipc x2, 2
        auipc x3, {2**19}
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(8)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(5555)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(3334141)
        self.assert_steps(pipeline=pipeline, steps=10)
        self.assertEqual(pipeline.state.register_file.registers[1], 4096 + 12)
        self.assertEqual(pipeline.state.register_file.registers[2], 8192 + 16)
        self.assertEqual(pipeline.state.register_file.registers[3], 2**31 + 20)
