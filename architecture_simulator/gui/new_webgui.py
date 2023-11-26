from architecture_simulator.simulation.toy_simulation import ToySimulation
from architecture_simulator.simulation.riscv_simulation import RiscvSimulation


def get_simulation(isa: str) -> RiscvSimulation | ToySimulation:
    isa = isa.lower()
    if isa == "riscv":
        return RiscvSimulation()
    else:
        return ToySimulation()
