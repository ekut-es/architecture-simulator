from typing import Any


class SvgDirective:
    """Base class for SVG Directives which tell the front end how to manipulate the svg."""

    def export(self, id: str) -> tuple[str, str, Any]:
        """Creates a tuple of the directive that the front end can understand.

        Args:
            id (str): The id to target.

        Returns:
            tuple[str, str, Any]: Tuple of (<id>, <action>, <value>)
        """
        raise NotImplementedError()


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
            "highlight",
            self._color_on if self.do_highlight else self._color_off,
        )


class SvgWriteDirective(SvgDirective):
    """SVG Directive for changing text."""

    def __init__(self):
        self.text = ""

    def export(self, id: str) -> tuple[str, str, str]:
        """Creates a tuple of the directive that the front end can understand.

        Args:
            id (str): The id to target.

        Returns:
            tuple[str, str, str]: Tuple of (<id>, write, <value>)
        """
        return (id, "write", self.text)
