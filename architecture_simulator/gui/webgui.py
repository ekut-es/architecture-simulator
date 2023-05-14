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

    for mem_i in simulation.state.memory.memory_file.keys():
        archsim_js.append_memory(mem_i, int(simulation.state.memory.memory_file[mem_i]))

    return simulation


def exec_instr(instr: str):
    global simulation
    if simulation is None:
        raise RuntimeError("state has not been initialized.")
    simulation.append_instructions(instr)
    simulation.step_simulation()
    for reg_i, reg_val in enumerate(simulation.state.register_file.registers):
        archsim_js.update_register(reg_i, reg_val)
    for address, address_val in enumerate(simulation.state.memory.memory_file):
        archsim_js.update_memory(address, address_val)
    return simulation
