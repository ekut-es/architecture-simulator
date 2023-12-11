from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING

from architecture_simulator.uarch.toy.toy_architectural_state import (
    ToyArchitecturalState,
)
from architecture_simulator.isa.toy.toy_parser import ToyParser
from architecture_simulator.isa.toy.toy_instructions import (
    ToyInstruction,
    LDA,
    ZRO,
    STO,
)
from .simulation import Simulation
from .runtime_errors import StepSequenceError
from fixedint import MutableUInt16
from architecture_simulator.uarch.toy.SvgVisValues import SvgVisValues
from architecture_simulator.util.integer_representations import (
    get_12_bit_representations,
    get_16_bit_representations,
)
from architecture_simulator.gui.toy_svg_directives import (
    ToySvgDirectives,
    SvgFillDirectiveControlUnit,
)
from architecture_simulator.isa.toy.toy_micro_program import MicroProgram

if TYPE_CHECKING:
    from architecture_simulator.uarch.toy.toy_performance_metrics import (
        ToyPerformanceMetrics,
    )


class ToySimulation(Simulation):
    def __init__(
        self,
        unified_memory_size: Optional[int] = None,
    ):
        self.state = ToyArchitecturalState(unified_memory_size)
        self.next_cycle = 1
        super().__init__()

    def first_cycle_step(self):
        """
        Simulates the behaviour of the first cycle of a instruction.
        Can not be called if self.next_cycle = 2
        """
        if self.is_done():
            return
        if not self.next_cycle == 1:
            raise StepSequenceError(
                "Before you can call this function again, you have to call second_cycle_step()"
            )
        self.has_started = True
        self.next_cycle = 2
        self.state.loaded_instruction.behavior(self.state)
        self.state.address_of_current_instruction = (
            self.state.address_of_next_instruction
        )
        self.state.address_of_next_instruction = int(self.state.program_counter)
        self.state.performance_metrics.cycles += 1

    def second_cycle_step(self):
        """
        Simulates the behaviour of the second cycle of a instruction.
        Can not be called if self.next_cycle = 1
        """
        if self.is_done():
            return
        if not self.next_cycle == 2:
            raise StepSequenceError(
                "Bevore you can call this function again, you have to call first_cycle_step()"
            )
        old_op_code = self.state.loaded_instruction.op_code_value()
        self.state.visualisation_values = SvgVisValues(
            op_code_old=old_op_code,
            pc_old=MutableUInt16(int(self.state.program_counter)),
        )
        self.state.visualisation_values.ram_out = self.state.memory.read_halfword(
            int(self.state.program_counter)
        )
        if self.state.program_counter <= self.state.max_pc:
            self.state.loaded_instruction = ToyInstruction.from_integer(
                int(self.state.visualisation_values.ram_out)
            )
        else:
            self.state.loaded_instruction = None
        self.state.program_counter += MutableUInt16(1)
        self.state.performance_metrics.instruction_count += 1
        self.state.performance_metrics.cycles += 1
        self.next_cycle = 1

    def step(self):
        if not self.next_cycle == 1:
            raise StepSequenceError(
                "step() calls both first_cycle_step() and second_cycle_step(), so you can not call step after calling just first_cycle_step()."
            )
        self.first_cycle_step()
        self.second_cycle_step()
        return not self.is_done()

    def single_step(self):
        """Executes a single cycle."""
        if self.next_cycle == 1:
            self.first_cycle_step()
        else:
            self.second_cycle_step()

    def is_done(self) -> bool:
        return not self.state.instruction_loaded()

    def run(self):
        self.state.performance_metrics.resume_timer()
        while not self.is_done():
            self.step()
        self.state.performance_metrics.stop_timer()

    def load_program(self, program: str):
        self.state = ToyArchitecturalState()
        parser = ToyParser()
        parser.parse(program=program, state=self.state)

    def has_instructions(self) -> bool:
        return False if self.state.max_pc is None else self.state.max_pc >= 0

    def get_performance_metrics(self) -> ToyPerformanceMetrics:
        return self.state.performance_metrics

    def get_register_representations(self) -> dict[str, tuple[str, str, str, str]]:
        """Returns representations for the registers.

        Returns:
            dict[str, tuple[str, str, str, str]]: The keys "accu", "pc" and "ir" hold representations of their respective values as (bin, udec, hex, sdec) tuples.
        """
        accu_representation = (
            get_16_bit_representations(int(self.state.accu))
            if self.has_instructions()
            else ("", "", "", "")
        )
        pc_representation = (
            get_12_bit_representations(int(self.state.program_counter))
            if self.has_instructions()
            else ("", "", "", "")
        )
        ir_representation = (
            get_16_bit_representations(int(self.state.loaded_instruction))
            if self.state.loaded_instruction is not None
            else ("", "", "", "")
        )
        return {
            "accu": accu_representation,
            "pc": pc_representation,
            "ir": ir_representation,
        }

    def get_memory_table_entries(
        self,
    ) -> list[tuple[int, tuple[str, str, str, str], str, str]]:
        """Returns the values to display in the memory table.

        Returns:
            list[tuple[int, tuple[str, str, str, str], str, str]]: Sorted list of (address, representatinos, instruction_representation, current_cycle).
                instruction_representation will be "-" if the address doesn't count as storing an instruction.
                current_cycle will be "1", "2" or "".
        """
        entries = self.state.memory.half_wordwise_repr()
        result: list[tuple[int, tuple[str, str, str, str], str, str]] = []
        current_cycle = "1" if self.next_cycle == 2 else "2"
        # iterate over all entries in the memory
        for address, values in sorted(entries.items()):
            # get instruction string representation
            instruction_representation = self._get_instruction_representation(
                address=address, value=int(values[1])
            )
            # find out if the current address is loaded as instruction and in which cycle it is
            is_current_instruction = (
                self.state.address_of_current_instruction is not None
                and address == self.state.address_of_current_instruction
            )
            result.append(
                (
                    address,
                    values,
                    instruction_representation,
                    current_cycle if is_current_instruction else "",
                )
            )
        return result

    def _get_instruction_representation(self, address: int, value: int) -> str:
        """Returns the string to show as instruction in the memory table.

        Args:
            address (int): Memory address
            value (int): Value at the given address in memory.

        Returns:
            str: String representation of the given value, if the simulator considers it a valid instruction (address <= max_pc), else "-".
        """
        if self.state.max_pc is not None and address <= self.state.max_pc:
            return str(ToyInstruction.from_integer(value))
        return "-"

    def get_toy_svg_update_values(self) -> list[tuple[str, str, Any]]:
        """Returns all information needed to update the svg.

        Returns:
            list[tuple[str, str, Any]]: each tuple is [svg-id, what update function to use, argument for update function (Any)].
                They can be one of ("<id>","highlight", <#hexcolor>), ("<id>", "write", <content>), ("<id>", "show", <bool>)
        """
        result = ToySvgDirectives()
        if self.has_instructions():
            loaded_instruction = self.state.loaded_instruction
            visualisation_values = self.state.visualisation_values
            control_unit_values: list[bool]

            if self.next_cycle == 2:
                if loaded_instruction is not None:
                    control_unit_values = MicroProgram.get_mp_values(
                        type(loaded_instruction)
                    )
                else:
                    control_unit_values = [False for i in range(12)]
            else:
                control_unit_values = MicroProgram.second_half_micro_program

            # Arrows:
            result.path_accu_pc_accu_is_zero.do_highlight = visualisation_values.jump
            result.path_accu_alu.do_highlight = (
                visualisation_values.alu_out is not None
                and not type(loaded_instruction)
                in [
                    LDA,
                    ZRO,
                ]
            )
            result.path_alu_junction.do_highlight = (
                visualisation_values.alu_out is not None
            )
            result.path_junction_accu.do_highlight = control_unit_values[
                5
            ]  # 5 _> SET[ACCU]
            result.path_junction_ram.do_highlight = control_unit_values[
                0
            ]  # 0 _> WRITE[RAM]
            result.path_opcode_control_unit.do_highlight = True
            result.path_instaddress_junction.do_highlight = (
                visualisation_values.ram_out is not None
                or visualisation_values.jump
                or isinstance(loaded_instruction, STO)
            ) and not control_unit_values[4]
            result.path_junction_pc.do_highlight = visualisation_values.jump
            result.path_junction_multiplexer.do_highlight = (
                visualisation_values.ram_out is not None
                or isinstance(loaded_instruction, STO)
            ) and not control_unit_values[
                4
            ]  # 4 _> SET[IR]
            result.path_pc_multiplexer.do_highlight = control_unit_values[
                4
            ]  # 4 _> SET[IR]
            result.path_multiplexer_ram.do_highlight = (
                visualisation_values.ram_out is not None
                or isinstance(loaded_instruction, STO)
            )
            result.path_ram_junction.do_highlight = (
                visualisation_values.ram_out is not None
            )
            result.path_junction_alu.do_highlight = (
                visualisation_values.ram_out is not None
                and visualisation_values.alu_out is not None
            )
            result.path_junction_ir.do_highlight = control_unit_values[
                4
            ]  # 4 _> SET[IR]

            # Text:
            if loaded_instruction is not None:
                result.text_mnemonic.text = loaded_instruction.mnemonic
                result.text_opcode.text = str(loaded_instruction.op_code_value())
                result.text_address.text = str(
                    loaded_instruction.address_section_value()
                )
            result.text_program_counter.text = str(self.state.program_counter)
            alu_out = visualisation_values.alu_out
            ram_out = visualisation_values.ram_out
            result.text_alu_out.text = str(alu_out) if alu_out is not None else ""
            result.group_alu_out.do_show = alu_out is not None
            result.text_ram_out.text = str(ram_out) if ram_out is not None else ""
            result.text_accu.text = str(self.state.accu)

            # Textblocks over Arrows:
            old_opcode = visualisation_values.op_code_old
            result.group_old_opcode_and_mnemonic.do_show = old_opcode is not None
            if old_opcode is not None:  # do not remove is not None
                result.text_old_opcode_and_mnemonic.text = (
                    str(old_opcode)
                    + " "
                    + ToyInstruction.from_integer(old_opcode << 12).mnemonic
                )
            old_pc = visualisation_values.pc_old
            result.group_old_pc.do_show = old_pc is not None
            if old_pc is not None:  # do not remove is not None
                result.text_old_pc.text = str(old_pc)
            old_accu = visualisation_values.accu_old
            result.group_old_accu.do_show = old_accu is not None
            if old_accu is not None:  # do not remove is not None
                result.text_old_accu.text = str(old_accu)

            # Control Unit:
            control_unit_names = [
                "write_ram",
                "inc_pc",
                "set_pc",
                "addr_ir",
                "set_ir",
                "set_accu",
                "alucin",
                "alumode",
                "alu3",
                "alu2",
                "alu1",
                "alu0",
            ]
            for name, value in zip(control_unit_names, control_unit_values):
                control_unit_path = getattr(result, "path_control_unit_" + name)
                control_unit_text = getattr(result, "text_" + name)
                assert isinstance(control_unit_path, SvgFillDirectiveControlUnit)
                assert isinstance(control_unit_text, SvgFillDirectiveControlUnit)
                control_unit_path.do_highlight = value
                control_unit_text.do_highlight = value
        return result.export()
