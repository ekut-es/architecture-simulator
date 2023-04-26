import archsim_js

from architecture_simulator.uarch.architectural_state import RegisterFile
from architecture_simulator.isa.instruction_types import Instruction
from architecture_simulator.isa.rv32i_instructions import ADD
from architecture_simulator.uarch.architectural_state import ArchitecturalState
from architecture_simulator.simulation.simulation import Simulation

simulation = None


def sim_init():
    global simulation
    simulation = Simulation(
        state=ArchitecturalState(register_file=RegisterFile(registers=[0, 2, 0, 0])),
        instructions={},
    )

    for reg_i in range(len(simulation.state.register_file.registers)):
        archsim_js.append_register(
            reg_i, simulation.state.register_file.registers[reg_i]
        )

    return simulation


def exec_instr(instr: str):
    global simulation
    if simulation is None:
        raise RuntimeError("state has not been initialized.")
    simulation.append_instructions(instr)
    simulation.step_simulation()
    for reg_i, reg_val in enumerate(simulation.state.register_file.registers):
        archsim_js.update_register(reg_i, reg_val)
    return simulation
