from dataclasses import dataclass


@dataclass
class ParserException(Exception):
    """Base class for all exceptions that occur during parsing."""

    line_number: int
    line: str


@dataclass
class ParserSyntaxException(ParserException):
    """A syntax exception that can be raised if the tokenization fails."""

    def __repr__(self) -> str:
        return f"There was a syntax error in line {self.line_number}: {self.line}"


@dataclass
class ParserLabelException(ParserException):
    """An excpetion that can be raised if an instruction refers to an unknown label."""

    label: str

    def __repr__(self) -> str:
        return f"Label '{self.label}' does not exist in line {self.line_number}: {self.line}"


@dataclass
class ParserOddImmediateException(ParserException):
    """An exception that can be raised when an immediate value has to be even, because it will be used to modify the program counter."""

    def __repr__(self) -> str:
        return f"Immediate has to be even in line {self.line_number}: {self.line}"


@dataclass
class DuplicateLabelException(ParserException):
    """An exception that can be raised when a label/variable has been declared twice."""

    label: str

    def __repr__(self) -> str:
        return f"Label '{self.label}' in line {self.line_number}: '{self.line}' has already been declared before."
