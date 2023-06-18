import archsim_js

from architecture_simulator.uarch.architectural_state import (
    RegisterFile,
    Memory,
    InstructionMemory,
)
from architecture_simulator.isa.instruction_types import Instruction
from architecture_simulator.isa.rv32i_instructions import ADD
from architecture_simulator.uarch.architectural_state import ArchitecturalState
from architecture_simulator.simulation.simulation import Simulation
import fixedint

simulation = None


def sim_init():
    global simulation
    simulation = Simulation()
    update_tables()
    return simulation


def step_sim(instr: str):
    global simulation
    if simulation is None:
        raise RuntimeError("state has not been initialized.")

    # parse the instr json string into a python dict
    if simulation.state.instruction_memory.instructions == {}:
        simulation.state.instruction_memory.append_instructions(instr)

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
    simulation = Simulation()

    simulation.state.instruction_memory.append_instructions(instr)
    # run the simulation
    simulation.run_simulation()

    update_tables()

    return simulation


# resets the entire simulation
def reset_sim():
    global simulation
    if simulation is None:
        raise RuntimeError("state has not been initialized.")
    simulation = Simulation()
    update_tables()
    return simulation


def update_tables():
    global simulation
    if simulation is None:
        raise RuntimeError("state has not been initialized.")

    # appends all the registers one at a time
    archsim_js.clear_register_table()
    representations = simulation.state.register_file.reg_repr()
    for reg_i, reg_val in sorted(
        representations.items(),
        key=lambda item: item[0],
    ):
        archsim_js.update_register_table(reg_i, reg_val)  # int(reg_val)

    # appends all the memory one at a time
    archsim_js.clear_memory_table()
    representations = simulation.state.memory.memory_wordwise_repr()
    for address, address_value in sorted(
        representations.items(),
        key=lambda item: item[0],
    ):
        archsim_js.update_memory_table(hex(address), address_value)

    # appends all the instructions one at a time
    archsim_js.clear_instruction_table()
    for address, cmd in sorted(
        simulation.state.instruction_memory.instructions.items(),
        key=lambda item: item[0],
    ):
        archsim_js.update_instruction_table(hex(address), cmd.__repr__())
