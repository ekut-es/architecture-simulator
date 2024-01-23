from typing import Any
from .svg_directives import SvgDirective, SvgFillDirective, SvgWriteDirective


class ToySvgDirectives:
    """A Class that holds all the SvgDirectives for the Toy SVG."""

    def __init__(self):
        # Path with different fill color.
        self.path_accu_pc_accu_is_zero = SvgFillDirectiveAlt()
        # All the normal paths.
        self.path_accu_alu = SvgFillDirectiveMain()
        self.path_alu_junction = SvgFillDirectiveMain()
        self.path_junction_accu = SvgFillDirectiveMain()
        self.path_junction_ram = SvgFillDirectiveMain()
        self.path_opcode_control_unit = SvgFillDirectiveMain()
        self.path_instaddress_junction = SvgFillDirectiveMain()
        self.path_junction_pc = SvgFillDirectiveMain()
        self.path_junction_multiplexer = SvgFillDirectiveMain()
        self.path_pc_multiplexer = SvgFillDirectiveMain()
        self.path_multiplexer_ram = SvgFillDirectiveMain()
        self.path_ram_junction = SvgFillDirectiveMain()
        self.path_junction_alu = SvgFillDirectiveMain()
        self.path_junction_ir = SvgFillDirectiveMain()
        # Normal Text fields.
        self.text_mnemonic = SvgWriteDirective()
        self.text_opcode = SvgWriteDirective()
        self.text_address = SvgWriteDirective()
        self.text_program_counter = SvgWriteDirective()
        self.text_ram_out = SvgWriteDirective()
        self.text_accu = SvgWriteDirective()
        # Groups for the text fields above paths to show or hide.
        self.group_old_opcode_and_mnemonic = SvgShowDirective()
        self.group_old_pc = SvgShowDirective()
        self.group_old_accu = SvgShowDirective()
        self.group_alu_out = SvgShowDirective()
        # Text fields for the above groups.
        self.text_old_opcode_and_mnemonic = SvgWriteDirective()
        self.text_old_pc = SvgWriteDirective()
        self.text_old_accu = SvgWriteDirective()
        self.text_alu_out = SvgWriteDirective()
        # Control unit signal paths and texts to highlight.
        self.path_control_unit_write_ram = SvgFillDirectiveControlUnit()
        self.text_write_ram = SvgFillDirectiveControlUnit()
        self.path_control_unit_inc_pc = SvgFillDirectiveControlUnit()
        self.text_inc_pc = SvgFillDirectiveControlUnit()
        self.path_control_unit_set_pc = SvgFillDirectiveControlUnit()
        self.text_set_pc = SvgFillDirectiveControlUnit()
        self.path_control_unit_addr_ir = SvgFillDirectiveControlUnit()
        self.text_addr_ir = SvgFillDirectiveControlUnit()
        self.path_control_unit_set_ir = SvgFillDirectiveControlUnit()
        self.text_set_ir = SvgFillDirectiveControlUnit()
        self.path_control_unit_set_accu = SvgFillDirectiveControlUnit()
        self.text_set_accu = SvgFillDirectiveControlUnit()
        self.path_control_unit_alucin = SvgFillDirectiveControlUnit()
        self.text_alucin = SvgFillDirectiveControlUnit()
        self.path_control_unit_alumode = SvgFillDirectiveControlUnit()
        self.text_alumode = SvgFillDirectiveControlUnit()
        self.path_control_unit_alu3 = SvgFillDirectiveControlUnit()
        self.text_alu3 = SvgFillDirectiveControlUnit()
        self.path_control_unit_alu2 = SvgFillDirectiveControlUnit()
        self.text_alu2 = SvgFillDirectiveControlUnit()
        self.path_control_unit_alu1 = SvgFillDirectiveControlUnit()
        self.text_alu1 = SvgFillDirectiveControlUnit()
        self.path_control_unit_alu0 = SvgFillDirectiveControlUnit()
        self.text_alu0 = SvgFillDirectiveControlUnit()

    def export(self) -> list[tuple[str, str, Any]]:
        """Exports all SvgDirectives into a format that the front end understands.

        Note: It will take all the SvgDirective attributes of the object.
        The name of the attribute has to be the id, except underscores will be replaced by dashes.

        Returns:
            list[tuple[str, str, Any]]: each tuple is [svg-id, what update function to use, argument for update function (Any)].
            They can be one of ("<id>","highlight", <#hexcolor>), ("<id>", "write", <content>), ("<id>", "show", <bool>)
        """
        result: list[tuple[str, str, Any]] = []
        for key, value in vars(self).items():
            if isinstance(value, SvgDirective):
                result.append(value.export(key.replace("_", "-")))
        return result


class SvgShowDirective(SvgDirective):
    """SVG Directive for showing/hiding an element."""

    def __init__(self):
        self.do_show = False

    def export(self, id: str) -> tuple[str, str, bool]:
        """Creates a tuple of the directive that the front end can understand.

        Args:
            id (str): The id to target.

        Returns:
            tuple[str, str, bool]: Tuple of (<id>, show, <value>)
        """
        return (id, "show", self.do_show)


class SvgFillDirectiveMain(SvgFillDirective):
    """SVG Fill Directive for normal paths."""

    def __init__(self):
        super().__init__(color_on="#ED6B03", color_off="#5f5f5f")


class SvgFillDirectiveAlt(SvgFillDirective):
    """SVG Fill Directive for secondary paths."""

    def __init__(self):
        super().__init__(color_on="#ED6B03", color_off="#000000")


class SvgFillDirectiveControlUnit(SvgFillDirective):
    """SVG Fill Directive for the control unit signals."""

    def __init__(self):
        super().__init__(color_on="#ED6B03", color_off="#000000")
