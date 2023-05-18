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
            register_file=RegisterFile(registers=[0, 2, 0, 0, 4]),
            memory=Memory(
                memory_file=dict(
                    [
                        (0, fixedint.MutableUInt8(1)),
                        (1, fixedint.MutableUInt8(2)),
                        (2, fixedint.MutableUInt8(3)),
                        (3, fixedint.MutableUInt8(-1)),
                        (pow(2, 32) - 1, fixedint.MutableUInt8(4)),
                        (2047, fixedint.MutableUInt8(5)),
                    ]
                )
            ),
        ),
        instructions={},
    )

    for reg_i in range(len(simulation.state.register_file.registers)):
        archsim_js.append_register(
            reg_i, simulation.state.register_file.registers[reg_i]
        )

    for address, address_val in simulation.state.memory.memory_file.items():
        archsim_js.append_memory(address, int(address_val))

    return simulation


def step_sim(instr: str):
    global simulation
    if simulation is None:
        raise RuntimeError("state has not been initialized.")

    # parse the instr json string into a python dict
    instr_parsed = json.loads(instr)

    # append all instructions
    for cmd in instr_parsed.values():
        simulation.append_instructions(cmd)

    # step the simulation
    simulation.step_simulation()

    # update the registers after exeution of the instruction/s
    for reg_i, reg_val in enumerate(simulation.state.register_file.registers):
        archsim_js.update_register(reg_i, reg_val)

    # update the memory after exeution of the instruction/s
    for address, address_val in simulation.state.memory.memory_file.items():
        archsim_js.update_memory(address, address_val)

    return simulation


# runs the simulation, takes a json string as input and returns the whole simulation
def run_sim(instr: str):
    global simulation
    if simulation is None:
        raise RuntimeError("state has not been initialized.")

    # parse the instr json string into a python dict
    instr_parsed = json.loads(instr)

    # append all instructions
    for cmd in instr_parsed.values():
        simulation.append_instructions(cmd)

    # run the simulation
    simulation.run_simulation()

    # update the registers after exeution of the instruction/s
    for reg_i, reg_val in enumerate(simulation.state.register_file.registers):
        archsim_js.update_register(reg_i, reg_val)

    # update the memory after exeution of the instruction/s
    for address, address_val in simulation.state.memory.memory_file.items():
        archsim_js.update_memory(address, address_val)

    return simulation
