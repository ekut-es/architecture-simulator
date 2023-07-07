import unittest
import fixedint
from architecture_simulator.uarch.architectural_state import ArchitecturalState, Memory
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

    def test_add(self):
        program = """add x1, x1, x2
        add x4, x5, x6
        add x7, x8, x9"""
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
        pipeline.state.register_file.registers[8] = fixedint.MutableUInt32(-10)
        pipeline.state.register_file.registers[9] = fixedint.MutableUInt32(20)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(13)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(52)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7], fixedint.MutableUInt32(10)
        )

    def test_sub(self):
        program = """sub x1, x1, x2
        sub x4, x5, x6
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
        pipeline.state.register_file.registers[8] = fixedint.MutableUInt32(-10)
        pipeline.state.register_file.registers[9] = fixedint.MutableUInt32(20)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(-3)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(12)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7], fixedint.MutableUInt32(-30)
        )

    def test_sll(self):
        program = """sll x1, x1, x2
        sll x4, x5, x6
        sll x7, x8, x9"""
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
        pipeline.state.register_file.registers[5] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[6] = fixedint.MutableUInt32(31)
        pipeline.state.register_file.registers[8] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[9] = fixedint.MutableUInt32(20)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1],
            fixedint.MutableUInt32(5 * 2**8),
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4],
            fixedint.MutableUInt32(2147483648),
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7], fixedint.MutableUInt32(2**20)
        )

    def test_slt(self):
        program = """slt x1, x1, x2
        slt x4, x5, x6
        slt x7, x8, x9"""
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
        pipeline.state.register_file.registers[8] = fixedint.MutableUInt32(-10)
        pipeline.state.register_file.registers[9] = fixedint.MutableUInt32(20)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(0)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7], fixedint.MutableUInt32(1)
        )

    def test_sltu(self):
        program = """sltu x1, x1, x2
        sltu x4, x5, x6
        sltu x7, x8, x9"""
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
        pipeline.state.register_file.registers[8] = fixedint.MutableUInt32(-10)
        pipeline.state.register_file.registers[9] = fixedint.MutableUInt32(20)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(0)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7], fixedint.MutableUInt32(0)
        )

    def test_xor(self):
        program = """xor x1, x1, x2
        xor x4, x5, x6
        xor x7, x8, x9"""
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
        pipeline.state.register_file.registers[5] = fixedint.MutableUInt32(0)
        pipeline.state.register_file.registers[6] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[8] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[9] = fixedint.MutableUInt32(0)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(0)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7], fixedint.MutableUInt32(-1)
        )

    def test_srl(self):
        program = """srl x1, x1, x2
        srl x4, x5, x6
        srl x7, x8, x9"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[5] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[6] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[8] = fixedint.MutableUInt32(16)
        pipeline.state.register_file.registers[9] = fixedint.MutableUInt32(2)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(0)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7], fixedint.MutableUInt32(4)
        )

    def test_sra(self):
        program = """sra x1, x1, x2
        sra x4, x5, x6
        sra x7, x8, x9"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(16)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(2)
        pipeline.state.register_file.registers[5] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[6] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[8] = fixedint.MutableUInt32(100)
        pipeline.state.register_file.registers[9] = fixedint.MutableUInt32(20)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(4)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(-1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7], fixedint.MutableUInt32(0)
        )

    def test_or(self):
        program = """or x1, x1, x2
        or x4, x5, x6
        or x7, x8, x9"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[5] = fixedint.MutableUInt32(0)
        pipeline.state.register_file.registers[6] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[8] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[9] = fixedint.MutableUInt32(0)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7], fixedint.MutableUInt32(-1)
        )

    def test_and(self):
        program = """and x1, x1, x2
        and x4, x5, x6
        and x7, x8, x9"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[5] = fixedint.MutableUInt32(0)
        pipeline.state.register_file.registers[6] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[8] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[9] = fixedint.MutableUInt32(2)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(7):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(0)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7], fixedint.MutableUInt32(2)
        )

    def test_addi(self):
        program = """addi x1, x1, 1
        addi x2, x2, -1
        addi x3, x3, 1234
        addi x4, x4, 20"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(0)
        pipeline.state.register_file.registers[4] = fixedint.MutableUInt32(-100)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(8):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(2)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[2], fixedint.MutableUInt32(-2)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[3], fixedint.MutableUInt32(1234)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(-80)
        )

    def test_andi(self):
        program = """andi x1, x1, 1
        andi x2, x2, -1
        andi x3, x3, 1234
        andi x4, x4, 20"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(0)
        pipeline.state.register_file.registers[4] = fixedint.MutableUInt32(-100)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[2], fixedint.MutableUInt32(-1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[3], fixedint.MutableUInt32(0)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(20)
        )

    def test_ori(self):
        program = """ori x1, x1, 1
        ori x2, x2, -1
        ori x3, x3, 0
        ori x4, x4, 2"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(0)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(0)
        pipeline.state.register_file.registers[4] = fixedint.MutableUInt32(1)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[2], fixedint.MutableUInt32(-1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[3], fixedint.MutableUInt32(0)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(3)
        )

    def test_xori(self):
        program = """xori x1, x1, 1
        xori x2, x2, -1
        xori x3, x3, 0
        xori x4, x4, -1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(0)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(0)
        pipeline.state.register_file.registers[4] = fixedint.MutableUInt32(-1)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(0)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[2], fixedint.MutableUInt32(-1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[3], fixedint.MutableUInt32(0)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(0)
        )

    def test_slli(self):
        program = """slli x1, x1, 1
        slli x2, x2, 20
        slli x3, x3, 31
        slli x4, x4, 1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(0)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[4] = fixedint.MutableUInt32(8)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(2)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[2], fixedint.MutableUInt32(0)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[3], fixedint.MutableUInt32(2**31)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(16)
        )

    def test_srli(self):
        program = """srli x1, x1, 1
        srli x2, x2, 20
        srli x3, x3, 31
        srli x4, x4, 1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(2)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(100)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[4] = fixedint.MutableUInt32(16)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[2], fixedint.MutableUInt32(0)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[3], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(8)
        )

    def test_srai(self):
        program = """srai x1, x1, 1
        srai x2, x2, 20
        srai x3, x3, 31
        srai x4, x4, 1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(2)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(100)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[4] = fixedint.MutableUInt32(16)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[2], fixedint.MutableUInt32(0)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[3], fixedint.MutableUInt32(-1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(8)
        )

    def test_slti(self):
        program = """slti x1, x1, 1
        slti x2, x2, 0
        slti x3, x3, 20
        slti x4, x4, -1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(10)
        pipeline.state.register_file.registers[4] = fixedint.MutableUInt32(-3)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(0)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[2], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[3], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(1)
        )

    def test_sltiu(self):
        program = """sltiu x1, x1, 1
        sltiu x2, x2, 0
        sltiu x3, x3, 20
        sltiu x4, x4, -1"""
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
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(10)
        pipeline.state.register_file.registers[4] = fixedint.MutableUInt32(3)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(0)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[2], fixedint.MutableUInt32(0)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[3], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[4], fixedint.MutableUInt32(1)
        )

    def test_lb(self):
        program = """lb x6, 0(x0)
        lb x7, 1(x1)
        lb x8, 0(x3)
        lb x9, 47(x4)"""
        pipeline = Pipeline(
            [
                InstructionFetchStage(),
                InstructionDecodeStage(),
                ExecuteStage(),
                MemoryAccessStage(),
                RegisterWritebackStage(),
            ],
            [0, 4, 1, 2, 3],
            state=ArchitecturalState(
                memory=Memory(
                    memory_file=dict(
                        [
                            (0, fixedint.MutableUInt8(1)),
                            (1, fixedint.MutableUInt8(2)),
                            (2, fixedint.MutableUInt8(3)),
                            (3, fixedint.MutableUInt8(-1)),
                            (2**32 - 1, fixedint.MutableUInt8(4)),
                            (2047, fixedint.MutableUInt8(5)),
                        ]
                    ),
                    min_bytes=0,
                ),
            ),
        )
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(20)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[4] = fixedint.MutableUInt32(2000)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[6], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7], fixedint.MutableUInt32(3)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[8], fixedint.MutableUInt32(4)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[9], fixedint.MutableUInt32(5)
        )

    def test_lh(self):
        program = """lh x6, 0(x0)
        lh x7, 1(x1)
        lh x8, 0(x3)
        lh x9, 48(x4)"""
        pipeline = Pipeline(
            [
                InstructionFetchStage(),
                InstructionDecodeStage(),
                ExecuteStage(),
                MemoryAccessStage(),
                RegisterWritebackStage(),
            ],
            [0, 4, 1, 2, 3],
            state=ArchitecturalState(
                memory=Memory(
                    memory_file=dict(
                        [
                            (0, fixedint.MutableUInt8(1)),
                            (1, fixedint.MutableUInt8(1)),
                            (2, fixedint.MutableUInt8(0)),
                            (3, fixedint.MutableUInt8(-1)),
                            (2**32 - 1, fixedint.MutableUInt8(0)),
                            (2048, fixedint.MutableUInt8(5)),
                        ]
                    ),
                    min_bytes=0,
                ),
            ),
        )
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(20)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[4] = fixedint.MutableUInt32(2000)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[6], fixedint.MutableUInt32(257)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7],
            fixedint.MutableUInt32((2**32 - 1) - 255),
        )
        self.assertEqual(
            pipeline.state.register_file.registers[8],
            fixedint.MutableUInt32(256),  # circular memory
        )
        self.assertEqual(
            pipeline.state.register_file.registers[9], fixedint.MutableUInt32(5)
        )

    def test_lw(self):
        program = """lw x6, 0(x0)
        lw x7, 2(x1)
        lw x8, 0(x3)
        lw x9, 48(x4)"""
        pipeline = Pipeline(
            [
                InstructionFetchStage(),
                InstructionDecodeStage(),
                ExecuteStage(),
                MemoryAccessStage(),
                RegisterWritebackStage(),
            ],
            [0, 4, 1, 2, 3],
            state=ArchitecturalState(
                memory=Memory(
                    memory_file=dict(
                        [
                            (0, fixedint.MutableUInt8(1)),
                            (1, fixedint.MutableUInt8(1)),
                            (2, fixedint.MutableUInt8(1)),
                            (3, fixedint.MutableUInt8(1)),
                            (2**32 - 1, fixedint.MutableUInt8(0)),
                            (2048, fixedint.MutableUInt8(5)),
                        ]
                    ),
                    min_bytes=0,
                ),
            ),
        )
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(20)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[4] = fixedint.MutableUInt32(2000)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[6],
            fixedint.MutableUInt32(1 + 2**8 + 2**16 + 2**24),
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[8],
            fixedint.MutableUInt32(2**8 + 2**16 + 2**24),  # circular memory
        )
        self.assertEqual(
            pipeline.state.register_file.registers[9], fixedint.MutableUInt32(5)
        )

    def test_lbu(self):
        program = """lbu x6, 0(x0)
        lbu x7, 2(x1)
        lbu x8, 0(x3)
        lbu x9, 48(x4)"""
        pipeline = Pipeline(
            [
                InstructionFetchStage(),
                InstructionDecodeStage(),
                ExecuteStage(),
                MemoryAccessStage(),
                RegisterWritebackStage(),
            ],
            [0, 4, 1, 2, 3],
            state=ArchitecturalState(
                memory=Memory(
                    memory_file=dict(
                        [
                            (0, fixedint.MutableUInt8(1)),
                            (1, fixedint.MutableUInt8(1)),
                            (2, fixedint.MutableUInt8(5)),
                            (3, fixedint.MutableUInt8(-1)),
                            (2**32 - 1, fixedint.MutableUInt8(5)),
                            (2048, fixedint.MutableUInt8(5)),
                        ]
                    ),
                    min_bytes=0,
                ),
            ),
        )
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(20)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[4] = fixedint.MutableUInt32(2000)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[6], fixedint.MutableUInt32(1)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7],
            fixedint.MutableUInt32(0b11111111),
        )
        self.assertEqual(
            pipeline.state.register_file.registers[8],
            fixedint.MutableUInt32(5),  # no circular memory
        )
        self.assertEqual(
            pipeline.state.register_file.registers[9], fixedint.MutableUInt32(5)
        )

    def test_lhu(self):
        program = """lhu x6, 0(x0)
        lhu x7, 1(x1)
        lhu x8, 0(x3)
        lhu x9, 48(x4)"""
        pipeline = Pipeline(
            [
                InstructionFetchStage(),
                InstructionDecodeStage(),
                ExecuteStage(),
                MemoryAccessStage(),
                RegisterWritebackStage(),
            ],
            [0, 4, 1, 2, 3],
            state=ArchitecturalState(
                memory=Memory(
                    memory_file=dict(
                        [
                            (0, fixedint.MutableUInt8(1)),
                            (1, fixedint.MutableUInt8(1)),
                            (2, fixedint.MutableUInt8(0)),
                            (3, fixedint.MutableUInt8(-1)),
                            (2**32 - 1, fixedint.MutableUInt8(5)),
                            (2048, fixedint.MutableUInt8(5)),
                        ]
                    ),
                    min_bytes=0,
                ),
            ),
        )
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(1)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(20)
        pipeline.state.register_file.registers[3] = fixedint.MutableUInt32(-1)
        pipeline.state.register_file.registers[4] = fixedint.MutableUInt32(2000)
        pipeline.state.instruction_memory.append_instructions(program)
        for _ in range(10):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[6], fixedint.MutableUInt32(257)
        )
        self.assertEqual(
            pipeline.state.register_file.registers[7],
            fixedint.MutableUInt32(0b1111111100000000),
        )
        self.assertEqual(
            pipeline.state.register_file.registers[8],
            fixedint.MutableUInt32(261),  # circular memory
        )
        self.assertEqual(
            pipeline.state.register_file.registers[9], fixedint.MutableUInt32(5)
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
