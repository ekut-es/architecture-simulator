from typing import Any
from .svg_directives import SvgDirective, SvgFillDirective


class RiscvSvgDirectivesBase:
    def export(self) -> list[tuple[str, str, Any]]:
        """Exports all SvgDirectives into a format that the front end understands.

        Note: It will take all the SvgDirective attributes of the object.
        The name of the attribute has to be the id, except underscores will be replaced by dashes.

        Returns:
            list[tuple[str, str, Any]]: each tuple is [svg-id, what update function to use, argument for update function (Any)].
            They can be one of ("<id>","highlight", <#hexcolor>), ("<id>", "write-center", <content>), ("<id>", "write-left", <content>), ("<id>", "write-right", <content>)
        """
        result: list[tuple[str, str, Any]] = []
        for key, value in vars(self).items():
            if isinstance(value, SvgDirective):
                result.append(value.export(key.replace("_", "-")))
        return result


class RiscvFiveStageIFSvgDirectives(RiscvSvgDirectivesBase):
    def __init__(self):
        self.Fetch = SvgWriteCenterDirective()
        self.InstructionMemoryInstrText = SvgWriteRightDirective()
        self.InstructionMemory = SvgFillDirectiveBlue()
        self.InstructionReadAddressText = SvgWriteLeftDirective()
        self.PC = SvgWriteCenterDirective()
        self.FetchPCOut = SvgFillDirectiveBlue()
        self.FetchAddOutText = SvgWriteCenterDirective()
        self.FetchAddOut = SvgFillDirectiveBlue()
        self.I_LengthText = SvgWriteCenterDirective()
        self.FetchI_Length = SvgFillDirectiveBlue()


class RiscvFiveStageIDSvgDirectives(RiscvSvgDirectivesBase):
    def __init__(self):
        self.Decode = SvgWriteCenterDirective()
        self.RegisterFileReadAddress1Text = SvgWriteLeftDirective()
        self.DecodeInstructionMemory1 = SvgFillDirectiveBlue()
        self.RegisterFileReadAddress2Text = SvgWriteLeftDirective()
        self.DecodeInstructionMemory2 = SvgFillDirectiveBlue()
        self.RegisterFileReadData1Text = SvgWriteRightDirective()
        self.RegisterFileReadData1 = SvgFillDirectiveBlue()
        self.RegisterFileReadData2Text = SvgWriteRightDirective()
        self.RegisterFileReadData2 = SvgFillDirectiveBlue()
        self.ImmGenText = SvgWriteCenterDirective()
        self.ImmGenOut = SvgFillDirectiveBlue()
        self.DecodeInstructionMemory3 = SvgFillDirectiveBlue()
        self.DecodeInstructionMemory4Text = SvgWriteCenterDirective()
        self.DecodeInstructionMemory4 = SvgFillDirectiveBlue()
        self.DecodeFetchAddOutText = SvgWriteCenterDirective()
        self.DecodeFetchAddOut = SvgFillDirectiveBlue()
        self.DecodeUpperFetchPCOutText = SvgWriteCenterDirective()
        self.DecodeLowerFetchPCOutText = SvgWriteCenterDirective()
        self.DecodeUpperFetchPCOut = SvgFillDirectiveBlue()
        self.DecodeLowerFetchPCOut = SvgFillDirectiveBlue()
        self.DecodeInstructionMemory = SvgFillDirectiveBlue()


class RiscvFiveStageEXSvgDirectives(RiscvSvgDirectivesBase):
    def __init__(self):
        self.Execute = SvgWriteCenterDirective()
        self.ExecuteRightMuxOutText = SvgWriteCenterDirective()
        self.ExecuteRightMuxOut = SvgFillDirectiveBlue()
        self.ExecuteLeftMuxOutText = SvgWriteCenterDirective()
        self.ExecuteLeftMuxOut = SvgFillDirectiveBlue()
        self.ExecuteRegisterFileReadData1 = SvgFillDirectiveBlue()
        self.ExecuteRegisterFileReadData2Text2 = SvgWriteCenterDirective()
        self.ExecuteRegisterFileReadData2 = SvgFillDirectiveBlue()
        self.ExecuteImmGenText1 = SvgWriteCenterDirective()
        self.ExecuteImmGenText3 = SvgWriteCenterDirective()
        self.ExecuteImmGen = SvgFillDirectiveBlue()
        self.ALUResultText = SvgWriteLeftDirective()
        self.ExecuteAluResult = SvgFillDirectiveBlue()
        self.ExecuteInstructionMemory4Text = SvgWriteCenterDirective()
        self.ExecuteInstructionMemory4 = SvgFillDirectiveBlue()
        self.ExecuteAddText = SvgWriteCenterDirective()
        self.ExecuteAdd = SvgFillDirectiveBlue()
        self.ExecuteFetchAddOutText = SvgWriteCenterDirective()
        self.ExecuteFetchAddOut = SvgFillDirectiveBlue()
        self.ExecuteUpperFetchPCOutText = SvgWriteCenterDirective()
        self.ExecuteUpperFetchPCOut = SvgFillDirectiveBlue()
        self.ExecuteLowerFetchPCOut = SvgFillDirectiveBlue()
        self.ALUComparison = SvgFillDirectiveGreen()
        self.ControlUnitLeftRight3 = SvgFillDirectiveGreen()
        self.ControlUnitLeftRight4 = SvgFillDirectiveGreen()
        self.AluControl = SvgFillDirectiveBlue()


class RiscvFiveStageMEMSvgDirectives(RiscvSvgDirectivesBase):
    def __init__(self):
        self.Memory = SvgWriteCenterDirective()
        self.DataMemoryAddressText = SvgWriteLeftDirective()
        self.MemoryExecuteAluResultText = SvgWriteCenterDirective()
        self.MemoryExecuteAluResultText2 = SvgWriteCenterDirective()
        self.MemoryExecuteAluResult = SvgFillDirectiveBlue()
        self.DataMemoryWriteDataText = SvgWriteLeftDirective()
        self.MemoryRegisterFileReadData2 = SvgFillDirectiveBlue()
        self.DataMemoryReadDataText = SvgWriteRightDirective()
        self.DataMemoryReadData = SvgFillDirectiveBlue()
        self.MemoryInstructionMemory4Text = SvgWriteCenterDirective()
        self.MemoryInstructionMemory4 = SvgFillDirectiveBlue()
        self.MemoryALUComparison = SvgFillDirectiveGreen()
        self.MemoryJumpOut = SvgFillDirectiveGreen()
        self.MemoryExecuteAddOutText = SvgWriteCenterDirective()
        self.MemoryExecuteAddOut = SvgFillDirectiveBlue()
        self.MemoryFetchAddOutText = SvgWriteCenterDirective()
        self.MemoryFetchAddOut = SvgFillDirectiveBlue()
        self.MemoryImmGenText = SvgWriteCenterDirective()
        self.MemoryImmGen = SvgFillDirectiveBlue()
        self.ControlUnitLeftRight = SvgFillDirectiveGreen()
        self.ControlUnitLeft = SvgFillDirectiveGreen()


class RiscvFiveStageWBSvgDirectives(RiscvSvgDirectivesBase):
    def __init__(self):
        self.WriteBack = SvgWriteCenterDirective()
        self.RegisterFileWriteDataText = SvgWriteLeftDirective()
        self.WriteBackMuxOut = SvgFillDirectiveBlue()
        self.RegisterFileWriteRegisterText = SvgWriteLeftDirective()
        self.WriteBackInstructionMemory4 = SvgFillDirectiveBlue()
        self.WriteBackDataMemoryReadDataText = SvgWriteCenterDirective()
        self.WriteBackDataMemoryReadData = SvgFillDirectiveBlue()
        self.WriteBackExecuteAluResultText = SvgWriteCenterDirective()
        self.WriteBackExecuteAluResult = SvgFillDirectiveBlue()
        self.WriteBackFetchAddOutText = SvgWriteCenterDirective()
        self.WriteBackFetchAddOut = SvgFillDirectiveBlue()
        self.WriteBackImmGenText = SvgWriteCenterDirective()
        self.WriteBackImmGen = SvgFillDirectiveBlue()
        self.wbsrc = SvgWriteCenterDirective()
        self.ControlUnitLeftRight2 = SvgFillDirectiveBlue()


class RiscvFiveStageOTHERSvgDirectives(RiscvSvgDirectivesBase):
    def __init__(self):
        self.FetchRightMuxOutText = SvgWriteCenterDirective()
        self.FetchLeftMuxOutText = SvgWriteCenterDirective()
        self.FetchRightMuxOut = SvgFillDirectiveBlue()
        self.path2453_0_7_7_9 = SvgFillDirectiveBlue()
        self.path2453_2_5_7_0_7_5_1_0_4 = SvgFillDirectiveBlue()
        self.path2453_2_5_7_0_7_6_2_29 = SvgFillDirectiveBlue()


class SvgFillDirectiveBlue(SvgFillDirective):
    """SVG Fill Directive: highlight: blue, default: black"""

    def __init__(self):
        super().__init__(color_on="#0000FF", color_off="#000000")


class SvgFillDirectiveGreen(SvgFillDirective):
    """SVG Fill Directive: highlight: green, default: black"""

    def __init__(self):
        super().__init__(color_on="#008000", color_off="#000000")


class SvgWriteLeftDirective(SvgDirective):
    """SVG Directive for changing text with set_svg_text_complex_left_align"""

    def __init__(self):
        self.text = ""

    def export(self, id: str) -> tuple[str, str, str]:
        return (id, "write-left", self.text)


class SvgWriteCenterDirective(SvgDirective):
    """SVG Directive for changing text with set_svg_text_complex_middle_align"""

    def __init__(self):
        self.text = ""

    def export(self, id: str) -> tuple[str, str, str]:
        return (id, "write-center", self.text)


class SvgWriteRightDirective(SvgDirective):
    """SVG Directive for changing text with set_svg_text_complex_right_align"""

    def __init__(self):
        self.text = ""

    def export(self, id: str) -> tuple[str, str, str]:
        return (id, "write-right", self.text)
