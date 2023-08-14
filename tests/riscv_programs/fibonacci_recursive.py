from architecture_simulator.isa.riscv.rv32i_instructions import (
    ADD,
    ADDI,
    AND,
    BEQ,
    BGE,
    JAL,
    JALR,
    LUI,
    LW,
    SW,
)
from architecture_simulator.simulation.riscv_simulation import RiscvSimulation
from architecture_simulator.uarch.riscv.riscv_architectural_state import (
    RiscvArchitecturalState,
    RegisterFile,
    Memory,
)
from fixedint import MutableUInt32


def fibonacci_recursive_simulation(n: int) -> RiscvSimulation:
    simulation = RiscvSimulation(
        state=RiscvArchitecturalState(
            register_file=RegisterFile(registers=[MutableUInt32(0)] * 32),
            memory=Memory(min_bytes=0),
        ),
    )
    simulation.state.instruction_memory.instructions = {
        0: LUI(rd=10, imm=0),  # loading n
        4: ADDI(rd=10, rs1=10, imm=n),
        8: ADDI(rd=2, rs1=0, imm=1024),  # setting initial stack pointer
        12: JAL(rd=1, imm=8),  # call fib(n)
        16: BEQ(rs1=0, rs2=0, imm=88),  # jump to end
        # Start of fib(n) procedure
        20: BGE(rs1=0, rs2=10, imm=68),  # branch if n <= 0
        24: ADDI(rd=5, rs1=0, imm=1),
        28: BEQ(rs1=5, rs2=10, imm=68),  # branch if n == 1
        32: ADDI(rd=2, rs1=2, imm=-8),  # adjust sp for 2 items
        36: SW(rs1=2, rs2=1, imm=4),  # store stack pointer
        40: SW(rs1=2, rs2=10, imm=0),  # store n
        44: ADDI(rd=10, rs1=10, imm=-1),  # x10 = n-1
        48: JAL(rd=1, imm=-28),  # call fib(n-1)
        52: LW(rd=5, rs1=2, imm=0),  # restore n
        56: SW(rs1=2, rs2=10, imm=0),  # store return value (fib(n-1))
        60: ADDI(rd=10, rs1=5, imm=-2),  # x10 = n-2
        64: JAL(rd=1, imm=-44),  # call fib(n-2)
        68: LW(rd=5, rs1=2, imm=0),  # load from memory: x5 = fib(n-1)
        72: LW(rd=1, rs1=2, imm=4),  # restore return address
        76: ADDI(rd=2, rs1=2, imm=8),  # decrease stack pointer for 2 items
        80: ADD(rd=10, rs1=10, rs2=5),  # x10 = fib(n-2) + fib(n-1)
        84: JALR(rd=7, rs1=1, imm=0),
        88: AND(rd=10, rs1=10, rs2=0),  # branch target: case n <= 0
        92: JALR(rd=7, rs1=1, imm=0),
        96: ADDI(rd=10, rs1=0, imm=1),  # branch target: case n == 1
        100: JALR(rd=7, rs1=1, imm=0),
        # end of fib(n) procedure
    }
    return simulation


def fibonacci_recursive(n: int) -> MutableUInt32:
    simulation = fibonacci_recursive_simulation(n)
    simulation.run()
    return simulation.state.register_file.registers[10]


# example program for calculating fibonacci numbers in a terribly recursive way
# Note: The immediates from the B-Types and jal will probably need to be halved, since they are interpreted as multiples of 2 bytes (but the assembler wants them as bytes directly)
# Note: add the instructions manually to Simulation.instructions, then use Simulation.step_simulation until pc hits 104
"""
lui x10, 0
addi x10, x10, 10
addi x2, x0, 1024
jal x1, 8 # fib(n)
beq x0, x0, 88 # go to end
bge x0, x10, 68 # n <= 0
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

"""
Fibonacci Recursive 2 is an updated version of the original fibonacci recursive program.
The algorithm was altered slightly so that you can calculate the number of procedure calls: it is (2*Fib(n+1) - 1).
The real differences are: Usage of the parser, labels, and ABI register names"""


def fibonacci_recursive_simulation_2(n: int) -> RiscvSimulation:
    simulation = RiscvSimulation()
    simulation.load_program(
        f"""addi a0, zero, {n} # load n
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
    return simulation


def fibonacci_recursive_2(n: int) -> MutableUInt32:
    simulation = fibonacci_recursive_simulation_2(n)
    simulation.run()
    return simulation.state.register_file.registers[10]


if __name__ == "__main__":
    # simulation = fibonacci_recursive_simulation(22)
    # simulation.run_simulation()
    # print(simulation.state.register_file.registers[10])
    # print(simulation.state.performance_metrics)

    simulation = fibonacci_recursive_simulation_2(20)
    simulation.run()
    print(simulation.state.register_file.registers[10])
    print(simulation.state.performance_metrics)
