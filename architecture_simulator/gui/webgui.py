import archsim_js

from architecture_simulator.uarch.architectural_state import RegisterFile, Memory
from architecture_simulator.isa.instruction_types import Instruction
from architecture_simulator.isa.rv32i_instructions import ADD
from architecture_simulator.uarch.architectural_state import ArchitecturalState
from architecture_simulator.simulation.simulation import Simulation
import fixedint
import json

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
    update_tables(simulation)
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

    # update the registers after exeution of the instruction/s
    for reg_i, reg_val in enumerate(simulation.state.register_file.registers):
        archsim_js.update_single_register(reg_i, int(reg_val))

    # update the memory after exeution of the instruction/s
    for address, address_val in sorted(
        simulation.state.memory.memory_file.items(), key=lambda item: item[0]
    ):
        archsim_js.update_single_memory_address(hex(address), bin(address_val))

    update_tables(simulation)
    return simulation


# runs the simulation, takes a json string as input and returns the whole simulation
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

    # update the instructions after exeution of the instruction/s
    # currently not implemented

    # update the registers after exeution of the instruction/s
    for reg_i, reg_val in enumerate(simulation.state.register_file.registers):
        archsim_js.update_single_register(reg_i, int(reg_val))

    # update the memory after exeution of the instruction/s
    for address, address_val in sorted(
        simulation.state.memory.memory_file.items(), key=lambda item: item[0]
    ):
        archsim_js.update_single_memory_address(hex(address), bin(address_val))
        
    update_tables(simulation)

    return simulation


# resets the entire simulation
def reset_sim():
    global simulation
    if simulation is None:
        raise RuntimeError("state has not been initialized.")
    simulation = Simulation(
        state=ArchitecturalState(register_file=RegisterFile()), instructions={}
    )
    update_tables(simulation)
    return simulation

def update_tables(simulation):
        # appends all the registers either one at a time, or all at once with a json string
    archsim_js.clear_register_table()
    for reg_i, reg_val in enumerate(simulation.state.register_file.registers):
        archsim_js.update_register(reg_i, int(reg_val))

    # appends all the memory either one at a time or all at once with a json string
    archsim_js.clear_memory_table()
    for address, address_val in sorted(
        simulation.state.memory.memory_file.items(), key=lambda item: item[0]
    ):
        archsim_js.update_memory(hex(address), bin(address_val))
