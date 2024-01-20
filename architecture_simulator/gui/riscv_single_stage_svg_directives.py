from typing import Any
from .svg_directives import SvgDirective, SvgFillDirective, SvgWriteDirective


class RiscvSingleStageSvgDirectives:
    """A Class that holds all the SvgDirectives for the RiscvSingleStage SVG."""

    def __init__(self):
        pass

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


class SvgFillDirectiveBlue(SvgFillDirective):
    """SVG Fill Directive: highlight: blue, default: black"""

    def __init__(self):
        super().__init__(color_on="#0000FF", color_off="#000000")


class SvgFillDirectiveGreen(SvgFillDirective):
    """SVG Fill Directive: highlight: green, default: black"""

    def __init__(self):
        super().__init__(color_on="#008000", color_off="#000000")
