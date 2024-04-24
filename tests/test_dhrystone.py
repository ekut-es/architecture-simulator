from unittest import TestCase
from architecture_simulator.simulation.riscv_simulation import RiscvSimulation
from fixedint import UInt32
from pathlib import Path


class TestDhrystone(TestCase):
    def test_dhrystone(self) -> UInt32:
        simulation = RiscvSimulation()
        dhry_path = Path(__file__).parent / "riscv_programs" / "dhrystone.s"
        simulation.load_program(dhry_path.read_text())
        simulation.run()
        return simulation.state.register_file.registers[10]
