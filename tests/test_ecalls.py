from unittest import TestCase

from architecture_simulator.simulation.riscv_simulation import RiscvSimulation


class TestEcalls(TestCase):
    def test_ecalls(self):
        simulation = RiscvSimulation()
        simulation.load_program(
            """
li a0, 0x80000041
li a7, 1
ecall
li a7, 11
ecall
li a7, 34
ecall
li a7, 35
ecall
li a7, 36
ecall
"""
        )
        simulation.run()
        self.assertEqual(
            simulation.state.output,
            "-2147483583A0x800000410b100000000000000000000000010000012147483713",
        )

        simulation = RiscvSimulation()
        simulation.load_program(
            """
li a0, 0xBE700000
li a7, 2
ecall
"""
        )

        simulation = RiscvSimulation()
        simulation.load_program(
            """
li a7, 10
ecall
nop
"""
        )
        simulation.step()
        simulation.step()
        self.assertTrue(simulation.is_done())
        self.assertEqual(simulation.state.exit_code, 0)

        simulation = RiscvSimulation()
        simulation.load_program(
            """
li a0, 404
li a7, 93
ecall
nop
"""
        )
        simulation.step()
        simulation.step()
        simulation.step()
        self.assertTrue(simulation.is_done())
        self.assertEqual(simulation.state.exit_code, 404)

        simulation = RiscvSimulation()
        simulation.load_program(
            """
.data
    kaesekuchen: .string "Kaesekuchen ist toll."
.text
la a0, kaesekuchen
li a7, 4
ecall
"""
        )
        simulation.run()
        self.assertEqual(simulation.get_output(), "Kaesekuchen ist toll.")
        simulation.get_instruction_memory_entries()
