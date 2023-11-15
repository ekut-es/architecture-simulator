from __future__ import annotations
from typing import TYPE_CHECKING
import pyparsing as pp
from fixedint import MutableUInt16

from .toy_instructions import AddressTypeInstruction, instruction_map
from ..parser_exceptions import (
    ParserSyntaxException,
    ParserLabelException,
    DuplicateLabelException,
    ParserDirectiveException,
    ParserDataSyntaxException,
    MemorySizeException,
)
from architecture_simulator.uarch.toy.SvgVisValues import SvgVisValues

if TYPE_CHECKING:
    from architecture_simulator.uarch.toy.toy_architectural_state import (
        ToyArchitecturalState,
    )


class ToyParser:
    _address_mnemonics = ["STO", "LDA", "BRZ", "ADD", "SUB", "OR", "AND", "XOR"]
    _no_address_mnemonics = ["NOT", "INC", "DEC", "ZRO", "NOP"]

    _pattern_hex_value = pp.Combine("0x" + pp.Word(pp.hexnums))
    _pattern_dec_value = pp.Word(pp.nums)

    _pattern_label = pp.Word(pp.alphas + "_", pp.alphanums + "_")

    _pattern_value = _pattern_hex_value | _pattern_dec_value

    _pattern_address_instruction = pp.oneOf(_address_mnemonics, caseless=True)(
        "mnemonic"
    ) + (_pattern_value("address") ^ _pattern_label("label"))

    _pattern_no_address_instruction = pp.oneOf(_no_address_mnemonics, caseless=True)(
        "mnemonic"
    )

    _pattern_label_declaration = _pattern_label("label") + ":"

    _directives = ["text", "data"]
    _type_directives = ["word"]

    _DOT = pp.Literal(".")
    _D_COL = pp.Literal(":").suppress()

    _pattern_directive = pp.Group(_DOT + pp.oneOf(_directives)("directive"))
    _pattern_type_directive = pp.Group(_DOT + pp.oneOf(_type_directives)("type"))

    _pattern_variable_declaration = pp.Group(
        _pattern_label("name")
        + _D_COL
        + _pattern_type_directive("type")
        + pp.delimitedList(_pattern_value, delim=",")("values")
    )

    _pattern_line = (
        _pattern_directive
        ^ _pattern_variable_declaration("variable_declaration")
        ^ _pattern_address_instruction
        ^ _pattern_no_address_instruction
        ^ _pattern_label_declaration("label_declaration")
    ) + pp.StringEnd().suppress()

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
        self._segment()
        self._process_labels()
        self._write_data()
        self._load_instructions()

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

    def _process_labels(self):
        """Takes the labels and computes the addresses for the labels from self.token_list and stores both in self.labels."""
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
            elif tokens.mnemonic:  # if it is an instruction
                program_counter += 1

    def _write_data(self) -> None:
        """Looks for data write commands in self.data. Stores the variables in self.labels and writes them to the memory of self.state."""

        self.last_address_not_used_by_data = max(self.state.memory.address_range)

        for line_number, line, line_parsed in self.data:
            if isinstance(line_parsed, str) or (
                line_parsed.get_name() != "variable_declaration"
            ):
                raise ParserDataSyntaxException(line_number=line_number, line=line)
            else:
                values_to_write = line_parsed[0].get("values")
                self.last_address_not_used_by_data -= len(values_to_write)
                write_address = self.last_address_not_used_by_data + 1
                if write_address < 0:
                    raise MemorySizeException(max(self.state.memory.address_range) + 1)
                self._add_label_mapping(
                    label=line_parsed[0].get("name"),
                    value=write_address,
                    line=line,
                    line_number=line_number,
                )
                for value in values_to_write:
                    self.state.memory.write_halfword(
                        write_address, MutableUInt16(self._value_to_int(value))
                    )
                    write_address += 1

    def _load_instructions(self):
        """Instantiates the instructions from self.token_list and writes them to the instruction memory of self.state."""
        instructions = []
        for linenumber, line, tokens in self.text:
            if not tokens.mnemonic:
                # check if a variable is beeing declared in a .text section
                if tokens.variable_declaration:
                    raise ParserDataSyntaxException(linenumber, line)
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

        # write instructions to memory and init state:
        if len(instructions) - 1 > self.last_address_not_used_by_data:
            raise MemorySizeException(max(self.state.memory.address_range) + 1)
        self.state.max_pc = len(instructions) - 1
        for addr, instr in enumerate(instructions):
            self.state.memory.write_halfword(addr, MutableUInt16(int(instr)))
        if len(instructions) >= 1:
            self.state.loaded_instruction = instructions[0]
            self.state.visualisation_values = SvgVisValues(
                pc_old=MutableUInt16(0), ram_out=MutableUInt16(int(instructions[0]))
            )

    def _value_to_int(self, address: str) -> int:
        """Convert addresses to ints. Hex addresses (starting with '0x') and decimal addresses are supported.

        Args:
            address (str): An address like '0xd9c' or '1044'.

        Returns:
            int: the corresponding integer.
        """
        if address.startswith("0x"):
            return int(address[2:], base=16)
        else:
            return int(address)

    def _add_label_mapping(self, label: str, value: int, line_number: int, line: str):
        """Add label/variable value mapping to self.labels. Raise an error if the label, ... already exists.

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
