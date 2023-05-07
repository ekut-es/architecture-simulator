[1mdiff --git a/architecture_simulator/uarch/architectural_state.py b/architecture_simulator/uarch/architectural_state.py[m
[1mindex 94ea9f2..71a1655 100644[m
[1m--- a/architecture_simulator/uarch/architectural_state.py[m
[1m+++ b/architecture_simulator/uarch/architectural_state.py[m
[36m@@ -7,7 +7,43 @@[m [mclass RegisterFile:[m
     registers: list[fixedint.MutableUInt32][m
 [m
 [m
[32m+[m[32m@dataclass[m
[32m+[m[32mclass Memory:[m
[32m+[m[32m    memory_file: dict[int, fixedint.MutableUInt8][m
[32m+[m
[32m+[m[32m    def load_byte(self, adress: int) -> fixedint.MutableUInt8:[m
[32m+[m[32m        return self.memory_file[adress][m
[32m+[m
[32m+[m[32m    def store_byte(self, adress: int, value: fixedint.MutableUInt8):[m
[32m+[m[32m        self.memory_file[adress % pow(2, 32)] = value[m
[32m+[m
[32m+[m[32m    def load_halfword(self, adress: int) -> fixedint.MutableUInt16:[m
[32m+[m[32m        return ([m
[32m+[m[32m            fixedint.MutableUInt16(self.memory_file[adress + 1 % pow(2, 32)]) << 8[m
[32m+[m[32m            | self.memory_file[adress % pow(2, 32)][m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m    def store_halfword(self, adress: int, value: fixedint.MutableUInt16):[m
[32m+[m[32m        self.memory_file[adress % pow(2, 32)] = fixedint.MutableUInt8(value[0:8])[m
[32m+[m[32m        self.memory_file[adress + 1 % pow(2, 32)] = fixedint.MutableUInt8(value[8:16])[m
[32m+[m
[32m+[m[32m    def load_word(self, adress: int) -> fixedint.MutableUInt32:[m
[32m+[m[32m        return ([m
[32m+[m[32m            fixedint.MutableUInt32(self.memory_file[adress + 3 % pow(2, 32)]) << 24[m
[32m+[m[32m            | fixedint.MutableUInt32(self.memory_file[adress + 2 % pow(2, 32)]) << 16[m
[32m+[m[32m            | fixedint.MutableUInt32(self.memory_file[adress + 1 % pow(2, 32)]) << 8[m
[32m+[m[32m            | fixedint.MutableUInt32(self.memory_file[adress % pow(2, 32)])[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m    def store_word(self, adress: int, value: fixedint.MutableUInt32):[m
[32m+[m[32m        self.memory_file[adress % pow(2, 32)] = fixedint.MutableUInt8(value[0:8])[m
[32m+[m[32m        self.memory_file[adress + 1 % pow(2, 32)] = fixedint.MutableUInt8(value[8:16])[m
[32m+[m[32m        self.memory_file[adress + 2 % pow(2, 32)] = fixedint.MutableUInt8(value[16:24])[m
[32m+[m[32m        self.memory_file[adress + 3 % pow(2, 32)] = fixedint.MutableUInt8(value[24:32])[m
[32m+[m
[32m+[m
 @dataclass[m
 class ArchitecturalState:[m
     register_file: RegisterFile[m
[32m+[m[32m    memory: Memory[m
     program_counter: int = 0[m
[1mdiff --git a/tests/test_isa.py b/tests/test_isa.py[m
[1mindex c5774b0..931ee9f 100644[m
[1m--- a/tests/test_isa.py[m
[1m+++ b/tests/test_isa.py[m
[36m@@ -1,7 +1,7 @@[m
 import unittest[m
 import fixedint[m
 [m
[31m-from architecture_simulator.uarch.architectural_state import RegisterFile[m
[32m+[m[32mfrom architecture_simulator.uarch.architectural_state import RegisterFile, Memory[m
 from architecture_simulator.isa.rv32i_instructions import ([m
     ADD,[m
     BEQ,[m
[36m@@ -20,13 +20,19 @@[m [mfrom architecture_simulator.isa.parser import riscv_bnf, riscv_parser[m
 [m
 class TestInstructions(unittest.TestCase):[m
     def test_add(self):[m
[31m-        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 5, 9, 0]))[m
[32m+[m[32m        state = ArchitecturalState([m
[32m+[m[32m            register_file=RegisterFile(registers=[0, 5, 9, 0]),[m
[32m+[m[32m            memory=Memory(memory_file=()),[m
[32m+[m[32m        )[m
         add_1 = ADD(rs1=1, rs2=2, rd=0)[m
         state = add_1.behavior(state)[m
         self.assertEqual(state.register_file.registers, [14, 5, 9, 0])[m
 [m
     def test_sub(self):[m
[31m-        state = ArchitecturalState(register_file=RegisterFile(registers=[0, 5, 9, 0]))[m
[32m+[m[32m        state = ArchitecturalState([m
[32m+[m[32m            register_file=RegisterFile(registers=[0, 5, 9, 0]),[m
[32m+[m[32m            memory=Memory(memory_file=()),[m
[32m+[m[32m        )[m
         sub_1 = SUB(rs1=1, rs2=2, rd=0)[m
         state = sub_1.behavior(state)[m
         self.assertEqual(state.register_file.registers, [-4, 5, 9, 0])[m
[1mdiff --git a/tests/test_simulation.py b/tests/test_simulation.py[m
[1mindex 349b7cb..610516f 100644[m
[1m--- a/tests/test_simulation.py[m
[1m+++ b/tests/test_simulation.py[m
[36m@@ -1,6 +1,6 @@[m
 import unittest[m
 [m
[31m-from architecture_simulator.uarch.architectural_state import RegisterFile[m
[32m+[m[32mfrom architecture_simulator.uarch.architectural_state import RegisterFile, Memory[m
 from architecture_simulator.uarch.architectural_state import ArchitecturalState[m
 from architecture_simulator.simulation.simulation import Simulation[m
 [m
[36m@@ -9,7 +9,8 @@[m [mclass TestSimulation(unittest.TestCase):[m
     def test_simulation(self):[m
         simulation = Simulation([m
             state=ArchitecturalState([m
[31m-                register_file=RegisterFile(registers=[0, 2, 0, 0])[m
[32m+[m[32m                register_file=RegisterFile(registers=[0, 2, 0, 0]),[m
[32m+[m[32m                memory=Memory(memory_file=()),[m
             ),[m
             instructions={},[m
         )[m
