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
        return f"Syntax error in line {self.line_number}"


@dataclass
class ParserLabelException(ParserException):
    """An excpetion that can be raised if an instruction refers to an unknown label."""

    label: str

    def __repr__(self) -> str:
        return f"Label '{self.label}' in line {self.line_number} does not exist."


@dataclass
class ParserOddImmediateException(ParserException):
    """An exception that can be raised when an immediate value has to be even, because it will be used to modify the program counter."""

    def __repr__(self) -> str:
        return f"Immediate in line {self.line_number} has to be even."


@dataclass
class DuplicateLabelException(ParserException):
    """An exception that can be raised when a label/variable has been declared twice."""

    label: str

    def __repr__(self) -> str:
        return f"Label '{self.label}' in line {self.line_number} has already been declared before."


@dataclass
class ParserDirectiveException(ParserException):
    """An exception that can be raised when an illegal directive is used."""

    def __repr__(self) -> str:
        return f"Illegal directive in line {self.line_number}."


@dataclass
class ParserDataSyntaxException(ParserException):
    """An exception that can be raised when syntax inside a data segment is incorrect."""

    def __repr__(self) -> str:
        return f"Syntax error in .data segment in line {self.line_number}."


@dataclass
class ParserDataDuplicateException(ParserException):
    """An exception that can be raised when a duplicate variable name is used inside a data segment."""

    name: str

    def __repr__(self) -> str:
        return f"Redefinition of variable '{self.name}' in line {self.line_number}."


@dataclass
class ParserVariableException(ParserException):
    """An exception that can be raised when a variable is used but not defined."""

    name: str

    def __repr__(self) -> str:
        return f"Variable '{self.name}' in line {self.line_number} is not defined."


@dataclass
class MemorySizeException(Exception):
    """An exception that can be raised when there is not enough memory space to write all instructions and data to memory."""

    size_in_words: int

    def __repr__(self) -> str:
        return f"There is not enough space to write all instructions and data to memory. The memory size is only {str(self.size_in_words)} words."
