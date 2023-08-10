from __future__ import annotations
from typing import TYPE_CHECKING
import pyparsing as pp
from fixedint import MutableUInt16

from .toy_instructions import AddressTypeInstruction, instruction_map
from ..parser_exceptions import (
    ParserSyntaxException,
    ParserLabelException,
    DuplicateLabelException,
)

if TYPE_CHECKING:
    from architecture_simulator.uarch.toy.toy_architectural_state import (
        ToyArchitecturalState,
    )


class ToyParser:
    _address_mnemonics = ["STO", "LDA", "BRZ", "ADD", "SUB", "OR", "AND", "XOR"]
    _no_address_mnemonics = ["NOT", "INC", "DEC", "ZRO", "NOP"]

    _pattern_hex_value = pp.Combine("$" + pp.Word(pp.hexnums))
    _pattern_dec_value = pp.Word(pp.nums)

    _pattern_label = pp.Word(pp.alphas + "_", pp.alphanums + "_")

    _pattern_value = _pattern_hex_value | _pattern_dec_value

    _pattern_address_instruction = pp.oneOf(_address_mnemonics, caseless=True)(
        "mnemonic"
    ) + (_pattern_value("address") ^ _pattern_label("label"))

    _pattern_no_address_instruction = pp.oneOf(_no_address_mnemonics, caseless=True)(
        "mnemonic"
    )

    _pattern_write_data = (
        ":" + _pattern_value("address") + ":" + _pattern_value("value")
    )

    _pattern_label_declaration = _pattern_label("label") + ":"

    _pattern_variable_declaration = (
        _pattern_label("label") + "=" + _pattern_value("value")
    )

    _pattern_line = (
        _pattern_address_instruction
        ^ _pattern_no_address_instruction
        ^ _pattern_write_data("write_data")
        ^ _pattern_label_declaration("label_declaration")
        ^ _pattern_variable_declaration("variable_declaration")
    ) + pp.StringEnd().suppress()

    # def __init__(self):
    #     #self.state: ToyArchitecturalState
    #     self.program: str = ""
    #     #self.sanitized_program: list[int, str] = []
    #     self.token_list: list[int, str, pp.ParseResults] = []
    #     self.labels: dict[str, int] = {}

    def parse(self, program: str, state: ToyArchitecturalState):
        """Parses the text format assembly program and loads it into the architectural state.

        Args:
            program (str): Text format Toy assembly program.
            state (ToyArchitecturalState): The architectural state into which the program should get loaded.

        Raises:
            ParserSyntaxException: Indicates a syntax error.
        """
        self.state = state
        self.program = program
        self._sanitize()
        self._tokenize()
        self._process_labels_and_variables()
        self._load_instructions()
        self._write_data()

    def _sanitize(self):
        """Removes leading/trailing whitespaces, empty lines, comments from self.program. Gives each line a linenumber (starting at 1). Stores the result in self.sanitized_program."""
        lines = self.program.splitlines()
        self.sanitized_program: list[tuple[int, str]] = []
        for index, line in enumerate(lines):
            # remove leading/trailing whitespaces
            line = line.strip()
            # skip empty lines and lines that start with a # (comments)
            if (not line) or line.startswith("#"):
                continue
            # strip comments that start after (possible) instructions
            instruction_part = line.split("#", maxsplit=1)[0].strip()
            # append linenumber (index+1) and instruction string
            self.sanitized_program.append((index + 1, instruction_part))

    def _tokenize(self):
        """Turns self.sanitized_program into tokens and stores them (together with the line numbers and the original line) in self.token_list."""
        self.token_list: list[tuple[int, str, pp.ParseResults]] = []
        for linenumber, line in self.sanitized_program:
            try:
                self.token_list.append(
                    (linenumber, line, self._pattern_line.parse_string(line))
                )
            except pp.ParseException:
                raise ParserSyntaxException(line_number=linenumber, line=line)

    def _process_labels_and_variables(self):
        """Takes the variables and computes the addresses for the labels from self.token_list and stores both in self.labels."""
        program_counter = 0
        self.labels = {}
        for line_number, line, tokens in self.token_list:
            if tokens.get_name() == "label_declaration":
                self._add_label_mapping(
                    label=tokens.label,
                    value=program_counter,
                    line=line,
                    line_number=line_number,
                )
            elif tokens.get_name() == "variable_declaration":
                value = self._value_to_int(tokens.value)
                self._add_label_mapping(
                    label=tokens.label, value=value, line=line, line_number=line_number
                )
            elif tokens.mnemonic:  # if it is an instruction
                program_counter += 1

    def _load_instructions(self):
        """Instantiates the instructions from self.token_list and writes them to the instruction memory of self.state."""
        instructions = []
        for linenumber, line, tokens in self.token_list:
            if not tokens.mnemonic:
                # skip if the tokens dont belong to an instruction
                continue
            mnemonic = tokens.mnemonic.upper()
            instruction_class = instruction_map[mnemonic]
            if issubclass(instruction_class, AddressTypeInstruction):
                if tokens.address:
                    address = self._value_to_int(tokens.address)
                else:  # else a label is used
                    try:
                        address = self.labels[tokens.label]
                    except KeyError:
                        raise ParserLabelException(
                            line_number=linenumber, line=line, label=tokens.label
                        )
                instructions.append(instruction_class(address=address))
            else:  # else it is an instruction without an address
                instructions.append(instruction_class())
        self.state.instruction_memory.write_instructions(instructions)

    def _write_data(self):
        """Looks for data write commands in self.token_list and then write the data to the data memory of self.state if applicable."""
        for _, _, tokens in self.token_list:
            if tokens.write_data:
                address = self._value_to_int(tokens.address) % 4096
                value = MutableUInt16(self._value_to_int(tokens.value) % (2**16))
                self.state.data_memory.write_halfword(address=address, value=value)

    def _value_to_int(self, address: str) -> int:
        """Convert addresses to ints. Hex addresses (starting with '$') and decimal addresses are supported.

        Args:
            address (str): An address like '$d9c' or '1044'.

        Returns:
            int: the corresponding integer.
        """
        if address[0] == "$":
            return int(address[1:], base=16)
        else:
            return int(address)

    def _add_label_mapping(self, label: str, value: int, line_number: int, line: str):
        """Add label value mapping to self.labels. Raise an error if the label already exists.

        Args:
            label (str): Label to be added.
            value (int): The value to which the label should be mapped.
            line_number (int): The line number in which the label gets declared.
            line (str): The line in which the label gets declared.

        Raises:
            DuplicateLabelException: An error gets raised if the label already exists, since this is most likely unwanted.
        """
        if label in self.labels:
            raise DuplicateLabelException(
                line_number=line_number, line=line, label=label
            )
        self.labels[label] = value
