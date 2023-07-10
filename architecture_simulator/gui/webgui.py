import archsim_js
from architecture_simulator.isa.parser import ParserException

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
from dataclasses import dataclass

simulation = None


@dataclass
class StateNotInitializedError(RuntimeError):
    def __repr__(self):
        return "state has not been initialized."


def sim_init():
    global simulation
    simulation = Simulation()
    update_ui()
    return simulation


def step_sim(instr: str):
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    # parse the instr json string into a python dict
    if simulation.state.instruction_memory.instructions == {}:
        try:
            simulation.state.instruction_memory.append_instructions(instr)
        except ParserException as Parser_Exception:
            archsim_js.set_output(Parser_Exception.__repr__())

    # step the simulation
    simulation_ended_flag = simulation.step_simulation()

    update_ui()

    return (simulation.state.performance_metrics.__repr__(), simulation_ended_flag)


def resume_timer():
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    simulation.state.performance_metrics.resume_timer()


def stop_timer():
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    simulation.state.performance_metrics.stop_timer()


def get_performance_metrics():
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    return simulation.state.performance_metrics.__repr__()


# runs the simulation, takes a string as input and returns the whole simulation
# def run_sim(instr: str):
#     global simulation
#     if simulation is None:
#         raise StateNotInitializedError()

#     # reset the instruction list
#     simulation = Simulation()

#     simulation.state.instruction_memory.append_instructions(instr)
#     # run the simulation
#     simulation.run_simulation()

#     update_ui()

#     return simulation


# resets the entire simulation
def reset_sim():
    global simulation
    if simulation is None:
        raise StateNotInitializedError()
    simulation = Simulation()
    update_ui()
    return simulation


def parse_input(instr: str):
    global simulation
    if simulation is None:
        raise StateNotInitializedError()
    simulation.state.instruction_memory.instructions = {}
    try:
        simulation.state.instruction_memory.append_instructions(instr)
        archsim_js.remove_all_highlights()
    except ParserException as Parser_Exception:
        archsim_js.set_output(Parser_Exception.__repr__())
        archsim_js.highlight(
            Parser_Exception.line_number, str=Parser_Exception.__repr__()
        )
    update_ui()


def update_ui():
    update_tables()
    # update_performance_metrics()


def update_tables():
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    # appends all the registers one at a time
    archsim_js.clear_register_table()
    representations = simulation.state.register_file.reg_repr()
    for reg_i, reg_val in sorted(
        representations.items(),
        key=lambda item: item[0],
    ):
        reg_abi = simulation.state.register_file.get_abi_names(reg_i)
        archsim_js.update_register_table(reg_i, reg_val, reg_abi)  # int(reg_val)

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


# #actual comment: output = performance metric repr but if parser produces error, overwrite output with error
# def update_output():
#     global simulation
#     if simulation is None:
#         raise RuntimeError("state has not been initialized.")

#     archsim_js.update_output(simulation.state.performance_metrics.__repr__())
