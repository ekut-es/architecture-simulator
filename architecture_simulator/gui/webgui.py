import archsim_js

from architecture_simulator.uarch.architectural_state import RegisterFile, Memory
from architecture_simulator.isa.instruction_types import Instruction
from architecture_simulator.isa.rv32i_instructions import ADD
from architecture_simulator.uarch.architectural_state import ArchitecturalState
from architecture_simulator.simulation.simulation import Simulation
import fixedint

simulation = None


def sim_init():
    global simulation
    simulation = Simulation(
        state=ArchitecturalState(
            register_file=RegisterFile(registers=[0, 2, 0, 8, 6]),
            memory=Memory(
                memory_file=dict(
                    [
                        (0, fixedint.MutableUInt8(1)),
                        (1, fixedint.MutableUInt8(2)),
                        (2, fixedint.MutableUInt8(3)),
                        (3, fixedint.MutableUInt8(-1)),
                        (pow(2, 32) - 1, fixedint.MutableUInt8(4)),
                        (2047, fixedint.MutableUInt8(5)),
                        (10, fixedint.MutableUInt8(10)),
                    ]
                )
            ),
        ),
        instructions={},
    )
    update_tables()
    return simulation


def step_sim(instr: str):
    global simulation
    if simulation is None:
        raise RuntimeError("state has not been initialized.")

    # parse the instr json string into a python dict
    if simulation.instructions == {}:
        simulation.append_instructions(instr)

    # step the simulation
    simulation.step_simulation()

    update_tables()

    return simulation


# runs the simulation, takes a string as input and returns the whole simulation
def run_sim(instr: str):
    global simulation
    if simulation is None:
        raise RuntimeError("state has not been initialized.")

    # reset the instruction list
    simulation.instructions = {}
    simulation.state.program_counter = 0

    simulation.append_instructions(instr)
    # run the simulation
    simulation.run_simulation()

    update_tables()

    return simulation


# resets the entire simulation
def reset_sim():
    global simulation
    if simulation is None:
        raise RuntimeError("state has not been initialized.")
    simulation = Simulation(
        state=ArchitecturalState(register_file=RegisterFile()), instructions={}
    )
    update_tables()
    return simulation


def update_tables():
    global simulation
    if simulation is None:
        raise RuntimeError("state has not been initialized.")

    # appends all the registers one at a time
    archsim_js.clear_register_table()
    for reg_i, reg_val in enumerate(simulation.state.register_file.registers):
        archsim_js.update_register_table(reg_i, int(reg_val))

    # appends all the memory one at a time
    archsim_js.clear_memory_table()
    for address, address_val in sorted(
        simulation.state.memory.memory_file.items(), key=lambda item: item[0]
    ):
        archsim_js.update_memory_table(hex(address), bin(address_val))

    # appends all the instructions one at a time
    archsim_js.clear_instruction_table()
    for address, cmd in sorted(
        simulation.instructions.items(), key=lambda item: item[0]
    ):
        archsim_js.update_instruction_table(hex(address), cmd.__repr__())
