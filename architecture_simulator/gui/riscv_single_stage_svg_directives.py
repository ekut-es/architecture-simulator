from typing import Any
from .svg_directives import SvgDirective, SvgWriteDirective


class RiscvSingleStageSvgDirectives:
    """A Class that holds all the SvgDirectives for the RiscvSingleStage SVG."""

    def __init__(self) -> None:
        # Text Fields

        self.add_imm_text: SvgWriteDirective = SvgWriteDirective()
        self.add_instr_len_text: SvgWriteDirective = SvgWriteDirective()
        self.instr_len_text: SvgWriteDirective = SvgWriteDirective()

        self.pc_text: SvgWriteDirective = SvgWriteDirective()

        self.instr_mem_instr_text: SvgWriteDirective = SvgWriteDirective()
        self.instr_mem_read_addr_text: SvgWriteDirective = SvgWriteDirective()

        self.reg_file_read_addr1_text: SvgWriteDirective = SvgWriteDirective()
        self.reg_file_read_addr2_text: SvgWriteDirective = SvgWriteDirective()
        self.reg_file_read_data_1_text: SvgWriteDirective = SvgWriteDirective()
        self.reg_file_read_data_2_text: SvgWriteDirective = SvgWriteDirective()
        self.reg_file_write_reg_text: SvgWriteDirective = SvgWriteDirective()
        self.reg_file_write_data_text: SvgWriteDirective = SvgWriteDirective()

        self.imm_gen_value_text: SvgWriteDirective = SvgWriteDirective()

        self.alu_result_text: SvgWriteDirective = SvgWriteDirective()

        self.data_memory_address_text: SvgWriteDirective = SvgWriteDirective()
        self.data_memory_read_data_text: SvgWriteDirective = SvgWriteDirective()
        self.data_memory_write_data_value_text: SvgWriteDirective = SvgWriteDirective()

        # Paths

        # Control Unit paths

        # Binary signals
        self.control_unit_2mux_pc_path: SvgFillDirectiveRed = SvgFillDirectiveRed()
        self.control_unit_to_and_path: SvgFillDirectiveRed = SvgFillDirectiveRed()
        self.alu_control_to_read_data_2mux_path: SvgFillDirectiveRed = (
            SvgFillDirectiveRed()
        )
        self.alu_control_to_read_data_1_mux_path: SvgFillDirectiveRed = (
            SvgFillDirectiveRed()
        )
        self.control_unit_write_data_path: SvgFillDirectiveRed = SvgFillDirectiveRed()
        self.control_unit_read_data_path: SvgFillDirectiveRed = SvgFillDirectiveRed()
        self.control_unit_to_reg_file_path: SvgFillDirectiveRed = SvgFillDirectiveRed()

        # Non Binary signals
        self.control_unit_to_4mux_path: SvgFillDirectiveRed = SvgFillDirectiveRed()
        self.alu_control_to_alu_path: SvgFillDirectiveRed = SvgFillDirectiveRed()
        self.control_unit_to_alu_control_path: SvgFillDirectiveRed = (
            SvgFillDirectiveRed()
        )
        # Other paths
        self.instr_to_aluctrl_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.pc_to_add_imm_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.pc_to_2mux_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.pc_to_instr_mem_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.pc_out_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()

        self.instr_mem_to_read_addr1_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.instr_mem_to_read_addr2_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.instr_mem_to_write_reg_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.instr_mem_to_imm_gen_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.to_immgen_or_aluctrl_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.instr_mem_to_control_unit_path: SvgFillDirectiveBlue = (
            SvgFillDirectiveBlue()
        )

        self.imm_gen_out_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.imm_gen_to_add_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.imm_gen_to_4mux_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.imm_gen_joint_to_2mux_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.imm_gen_to_joint_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()

        self.read_data2_to_mem_write_data_path: SvgFillDirectiveBlue = (
            SvgFillDirectiveBlue()
        )
        self.read_data_1_mux_to_alu_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.read_data_1_to_2mux_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.read_data_2_2mux_to_alu_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.read_data_2_joint_to_2mux_path: SvgFillDirectiveBlue = (
            SvgFillDirectiveBlue()
        )
        self.read_data_2_to_joint_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()

        self.alu_out_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.alu_out_to_4mux_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.alu_out_to_2mux_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.alu_comparison_to_and_path: SvgFillDirectiveRed = SvgFillDirectiveRed()
        self.alu_to_data_memory_address_path: SvgFillDirectiveBlue = (
            SvgFillDirectiveBlue()
        )

        self.and_to_mux_path: SvgFillDirectiveRed = SvgFillDirectiveRed()

        self.add_imm_to_mux_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.add_instr_len_to_2mux_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.add_instr_len_to_4mux_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.add_instr_len_out_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()

        self.two_mux_2mux_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()
        self.two_mux_to_pc_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()

        self.instr_len_to_add_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()

        self.four_mux_to_write_data_path: SvgFillDirectiveBlue = SvgFillDirectiveBlue()

        self.data_mem_read_data_to_4mux_path: SvgFillDirectiveBlue = (
            SvgFillDirectiveBlue()
        )

    def export(self) -> list[tuple[str, str, Any]]:
        """Exports all SvgDirectives into a format that the front end understands.

        Note: It will take all the SvgDirective attributes of the object.
        The name of the attribute has to be the id, except underscores will be replaced by dashes.

        Returns:
            list[tuple[str, str, Any]]: each tuple is [svg-id, what update function to use, argument for update function (Any)].
            They can be one of ("<id>","highlight", <#hexcolor>), ("<id>", "write", <content>)
        """
        result: list[tuple[str, str, Any]] = []
        for key, value in vars(self).items():
            if isinstance(value, SvgDirective):
                result.append(value.export(key.replace("_", "-")))
        return result


class SvgFillDirective(SvgDirective):
    """SVG Fill Directive base class. The colors for highlighting are set here."""

    def __init__(self, color_on: str, color_off: str):
        self._color_on = color_on
        self._color_off = color_off
        self.do_highlight = False

    def export(self, id: str) -> tuple[str, str, str]:
        """Creates a tuple of the directive that the front end can understand.

        Args:
            id (str): The id to target.

        Returns:
            tuple[str, str, str]: Tuple of (<id>, highlight, <#hexccolor>)
        """
        return (
            id,
            "highlight-plain",
            self._color_on if self.do_highlight else self._color_off,
        )


class SvgFillDirectiveBlue(SvgFillDirective):
    """SVG Fill Directive: highlight: blue, default: black"""

    def __init__(self):
        super().__init__(color_on="#0000FF", color_off="#000000")


class SvgFillDirectiveRed(SvgFillDirective):
    """SVG Fill Directive: highlight: red, default: black"""

    def __init__(self):
        super().__init__(color_on="#A51E37", color_off="#000000")
