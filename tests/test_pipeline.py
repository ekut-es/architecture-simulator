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
)
from architecture_simulator.isa.parser import RiscvParser


class TestPipeline(unittest.TestCase):
    def test_bla(self):
        program = """add x1, x1, x2
        add x4, x5, x6
        sub x7, x8, x9"""
        parser = RiscvParser()
        instructions = parser.parse(program)
        pipeline = Pipeline(
            [
                InstructionFetchStage(),
                InstructionDecodeStage(),
                ExecuteStage(),
                MemoryAccessStage(),
                RegisterWritebackStage(),
            ],
            [0, 3, 1, 2, 4],
            state=ArchitecturalState(),
        )
        pipeline.state.instruction_memory.instructions = instructions
        pipeline.state.register_file.registers[1] = fixedint.MutableUInt32(5)
        pipeline.state.register_file.registers[2] = fixedint.MutableUInt32(8)
        pipeline.state.register_file.registers[5] = fixedint.MutableUInt32(32)
        pipeline.state.register_file.registers[6] = fixedint.MutableUInt32(20)
        pipeline.state.register_file.registers[8] = fixedint.MutableUInt32(32)
        pipeline.state.register_file.registers[9] = fixedint.MutableUInt32(20)
        for _ in range(7):
            pipeline.step()
        self.assertEqual(
            pipeline.state.register_file.registers[1], fixedint.MutableUInt32(13)
        )
