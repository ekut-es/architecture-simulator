import pyparsing as pp
from abc import ABC, abstractmethod
from typing import Any

from architecture_simulator.isa.parser_exceptions import (
    ParserSyntaxException,
    ParserDirectiveException,
    DuplicateLabelException,
)


class Parser(ABC):
    """
    An abstract base class for Parsers that can provides some basic functionality
    and ensures the implementation of a parse method. Functions:\n
        _sanitize(): remove comments, empty lines, leading/trailing whitespace, ...\n
        _tokenize(): turns lines into tokens\n
        _segment(): determines text and data segment\n
    """

    _pattern_line: pp.ParserElement

    def __init__(self) -> None:
        self.program: str = ""
        self.labels: dict[str, int] = {}

    @abstractmethod
    def parse(self, program: str, state: Any, **kwargs):
        ...

    def _sanitize(self) -> None:
        """Removes leading/trailing whitespace, empty lines, comments from self.program.\n
        Gives each line a line number (starting at 1).\n
        Stores the result in self.sanitized_program.\n"""
        self.sanitized_program: list[tuple[int, str]] = []
        # remove empty lines, lines that only contain white space and comment lines. Enumerate all lines before removing lines.
        self.sanitized_program = [
            (index + 1, line)
            for index, line in enumerate(self.program.splitlines())
            if line.strip() and not line.strip().startswith("#")
        ]
        # remove comments from lines that also contain an instruction and strip the line
        self.sanitized_program = [
            (index, line.split("#", 1)[0].strip())
            for index, line in self.sanitized_program
        ]

    def _tokenize(self) -> None:
        """Turns self.sanitized_program into tokens and stores them in self.token_list
        (together with the line numbers and the original line)."""
        self.token_list: list[tuple[int, str, pp.ParseResults]] = []
        for line_number, line in self.sanitized_program:
            try:
                self.token_list.append(
                    (line_number, line, self._pattern_line.parseString(line))
                )
            except pp.ParseException:
                raise ParserSyntaxException(line_number=line_number, line=line)

    def _segment(self) -> None:
        """Determines the segments of the program (data and text) and stores them in self.data and self.text."""
        self.data: list[tuple[int, str, pp.ParseResults]] = []
        self.text: list[tuple[int, str, pp.ParseResults]] = []

        if self.token_list == []:
            return

        data_exists = False
        text_exists = True
        self.text = self.token_list

        # first line is segment directive
        if not isinstance(self.token_list[0][2][0], str):
            # [0] -> first element in list, [2] -> ParseResult, [0] -> outer layer of parse result
            if self.token_list[0][2][0].get("directive") == "data":
                data_exists = True
                text_exists = False
                self.data = self.token_list[1:]
                self.text = []
            elif self.token_list[0][2][0].get("directive") == "text":
                self.text = self.token_list[1:]

        for line_number, line, line_parsed in self.token_list[1:]:
            if isinstance(line_parsed[0], str):
                continue
            line_parsed[0].get("directive")
            if line_parsed[0].get("directive") == "data":
                if not data_exists:
                    data_exists = True
                    index = self.text.index((line_number, line, line_parsed))
                    self.data = self.text[index + 1 :]
                    self.text = self.text[:index]
                else:
                    raise ParserDirectiveException(line_number=line_number, line=line)
            elif line_parsed[0].get("directive") == "text":
                if not text_exists:
                    text_exists = True
                    index = self.data.index((line_number, line, line_parsed))
                    self.text = self.data[index + 1 :]
                    self.data = self.data[:index]
                else:
                    raise ParserDirectiveException(line_number=line_number, line=line)
            elif line_parsed.get("directive") is not None:
                raise ParserDirectiveException(line_number=line_number, line=line)

    def _add_label_mapping(self, label: str, value: int, line_number: int, line: str):
        """Add label (variable) value mapping to self.labels. Raise an error if the label, ... already exists.

        Args:
            name (str): Label/Variable to be added.
            value (int): The value to which the label should be mapped.
            line_number (int): The line number in which the label gets declared.
            line (str): The line in which the label gets declared.

        Raises:
            DuplicateNamingException: An error gets raised if the label, ... already exists, since this is most likely unwanted.
        """
        if label in self.labels:
            raise DuplicateLabelException(
                line_number=line_number, line=line, label=label
            )
        self.labels[label] = value
