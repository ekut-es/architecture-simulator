import unittest

from tests.riscv_programs.fibonacci_recursive import (
    fibonacci_recursive,
)

from tests.riscv_programs.sections import sections_simulation


class TestRiscvPrograms(unittest.TestCase):
    def test_sections_sim_without_data_cache(self):
        simulation = sections_simulation(data_cache_enable=False)
        simulation.run()

    def test_sections_sim_with_data_cache(self):
        simulation = sections_simulation(data_cache_enable=True)
        simulation.run()
