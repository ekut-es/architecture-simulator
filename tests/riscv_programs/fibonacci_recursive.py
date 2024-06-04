from architecture_simulator.simulation.riscv_simulation import RiscvSimulation
from fixedint import UInt32


def get_fibonacci_recursive(n: int) -> str:
    return f"""addi a0, zero, {n} # load n
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


def fibonacci_recursive_simulation(n: int) -> RiscvSimulation:
    simulation = RiscvSimulation()
    simulation.load_program(get_fibonacci_recursive(n))
    return simulation


def fibonacci_recursive(n: int) -> UInt32:
    simulation = fibonacci_recursive_simulation(n)
    simulation.run()
    return simulation.state.register_file.registers[10]


if __name__ == "__main__":
    # simulation = fibonacci_recursive_simulation(22)
    # simulation.run_simulation()
    # print(simulation.state.register_file.registers[10])
    # print(simulation.state.performance_metrics)

    simulation = fibonacci_recursive_simulation(20)
    simulation.run()
    print(simulation.state.register_file.registers[10])
    print(simulation.state.performance_metrics)
