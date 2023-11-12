from typing import Any


class ToySvgDirectives:
    def __init__(self):
        self.path_accu_pc_accu_is_zero = SvgFillDirectiveAlt()

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

        self.text_mnemonic = SvgWriteDirective()
        self.text_opcode = SvgWriteDirective()
        self.text_address = SvgWriteDirective()
        self.text_program_counter = SvgWriteDirective()
        self.text_ram_out = SvgWriteDirective()
        self.text_accu = SvgWriteDirective()

        self.group_old_opcode_and_mnemonic = SvgShowDirective()
        self.group_old_pc = SvgShowDirective()
        self.group_old_accu = SvgShowDirective()
        self.group_alu_out = SvgShowDirective()

        self.text_old_opcode_and_mnemonic = SvgWriteDirective()
        self.text_old_pc = SvgWriteDirective()
        self.text_old_accu = SvgWriteDirective()
        self.text_alu_out = SvgWriteDirective()

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
        result: list[tuple[str, str, Any]] = []
        for key, value in vars(self).items():
            if isinstance(value, SvgDirective):
                result.append(value.export(key.replace("_", "-")))
        return result


class SvgDirective:
    def export(self, id: str) -> tuple[str, str, Any]:
        raise NotImplementedError()


class SvgWriteDirective(SvgDirective):
    def __init__(self):
        self.text = ""

    def export(self, id: str) -> tuple[str, str, str]:
        return (id, "write", self.text)


class SvgShowDirective(SvgDirective):
    def __init__(self):
        self.do_show = False

    def export(self, id: str) -> tuple[str, str, bool]:
        return (id, "show", self.do_show)


class SvgFillDirective(SvgDirective):
    def __init__(self, color_on: str, color_off: str):
        self._color_on = color_on
        self._color_off = color_off
        self.do_highlight = False

    def export(self, id: str) -> tuple[str, str, str]:
        return (
            id,
            "highlight",
            self._color_on if self.do_highlight else self._color_off,
        )


class SvgFillDirectiveMain(SvgFillDirective):
    def __init__(self):
        super().__init__(color_on="#ff3300", color_off="#5f5f5f")


class SvgFillDirectiveAlt(SvgFillDirective):
    def __init__(self):
        super().__init__(color_on="#ff3300", color_off="#000000")


class SvgFillDirectiveControlUnit(SvgFillDirective):
    def __init__(self):
        super().__init__(color_on="#ff3300", color_off="#000000")
