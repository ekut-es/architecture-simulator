from architecture_simulator.simulation.riscv_simulation import RiscvSimulation
from architecture_simulator.uarch.memory.cache import CacheOptions
from fixedint import UInt32


def sections_simulation(data_cache_enable: bool) -> RiscvSimulation:
    simulation = RiscvSimulation(
        data_cache=CacheOptions(
            enable=data_cache_enable,
            num_index_bits=0,
            num_block_bits=0,
            associativity=1,
            cache_type="wb",
            replacement_strategy="lru",
            miss_penalty=0,
        )
    )
    simulation.load_program(
        f""".data
    my_var1: .byte -128
    my_var2: .half 0x1234, 0b1010, 999
    my_var3: .word 0x12345678, 0b111
    text1:   .string "Hello, World!"  # ASCII byte array
.text
    la x1, my_var1     # load address of my_var1 into x1
    lh x2, my_var2     # load halfword from my_var2 into x2
    lh x3, my_var2[0]  # same effect as above
    lh x4, my_var2[2]  # x4 = 999
    lw x5, my_var3[1]  # x5 = 0b111
    lb x6, text1[11]   # x6 = '!'"""
    )
    return simulation


def sections() -> list[UInt32]:
    simulation = sections_simulation(True)
    simulation.run()
    return simulation.state.register_file.registers


if __name__ == "__main__":

    simulation = sections_simulation(True)
    simulation.run()
    print(simulation.state.register_file.registers[10])
    print(simulation.state.performance_metrics)
