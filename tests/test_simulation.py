import unittest

from architecture_simulator.uarch.architectural_state import RegisterFile
from architecture_simulator.uarch.architectural_state import Memory
from architecture_simulator.uarch.architectural_state import ArchitecturalState
from architecture_simulator.simulation.simulation import Simulation


class TestSimulation(unittest.TestCase):
    def test_simulation(self):
        simulation = Simulation(
            state=ArchitecturalState(
                register_file=RegisterFile(registers=[0, 2, 0, 0]),
                memory=Memory(memory_file=()),
            ),
            instructions={},
        )
        simulation.append_instructions("add x0, x0, x1\nadd x0, x0, x1")
        # simulation.append_instructions("sub x0, x0, x1")
        simulation.step_simulation()
        self.assertEqual(simulation.state.register_file.registers[0], 2)
        simulation.step_simulation()
        self.assertEqual(simulation.state.register_file.registers[0], 4)
        # simulation.step_simulation()
        # self.assertEqual(simulation.state.register_file.registers[0], 2)

    # example program for calculating fibonacci numbers in a terribly recursive way
    # Note: The immediates from the B-Types and jal will probably need to be halved, since they are interpreted as multiples of 2 bytes (but the assembler wants them as bytes directly)
    # Note: add the instructions manually to Simulation.instructions, then use Simulation.step_simulation until pc hits 108
    """
    lui x10, 0
    addi x10, x10, 10
    addi x2, x0, 1024
    jal x1, 8 # fib(n)
    beq x0, x0, 88 # go to end
    bgeu x0, x10, 68 # n <= 0
    addi x5, x0, 1
    beq x5, x10, 68 # n == 1
    addi x2, x2, -8 # adjust sp for ra and x10
    sw x1, 4(x2) # store sp
    sw x10, 0(x2) # store n
    addi x10, x10, -1 # x10 = n - 1
    jal x1, -28 # goto 5 (beginning)
    lw x5, 0(x2) # restore argument
    sw x10, 0(x2) # store return value (fib(n-1))
    addi x10, x5, -2 # x10 = n - 2
    jal x1, -44 # goto 5 (beginning)
    lw x5, 0(x2) # x5 = fib(n-1)
    lw x1, 4(x2) # restore ra
    addi x2, x2, 8 # return sp to original size
    add x10, x10, x5 # x10 = fib(n-2) + fib(n-1)
    jalr x7, x1, 0
    and x10, x10, x0 # <- n <= 0
    jalr x7, x1, 0
    addi x10, x0, 1 # <- n == 1
    jalr x7, x1, 0
    and x0, x0, x0 # end
    """
