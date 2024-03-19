from __future__ import annotations
from typing import TYPE_CHECKING
import pyparsing as pp
from fixedint import UInt16

from .toy_instructions import AddressTypeInstruction, instruction_map
from ..parser_exceptions import (
    ParserLabelException,
    ParserDataSyntaxException,
    MemorySizeException,
    DuplicateLabelException,
)
from architecture_simulator.uarch.toy.SvgVisValues import SvgVisValues
from architecture_simulator.isa.parser import Parser

if TYPE_CHECKING:
    from architecture_simulator.uarch.toy.toy_architectural_state import (
        ToyArchitecturalState,
    )


class ToyParser(Parser):
    _DOT = pp.Literal(".")
    _D_COL = pp.Literal(":").suppress()

    _address_mnemonics = ["STO", "LDA", "BRZ", "ADD", "SUB", "OR", "AND", "XOR"]
    _no_address_mnemonics = ["NOT", "INC", "DEC", "ZRO", "NOP"]

    _pattern_hex_value = pp.Combine("0x" + pp.Word(pp.hexnums))
    _pattern_dec_value = pp.Word(pp.nums)

    _pattern_label = pp.Word(pp.alphas + "_", pp.alphanums + "_")

    _pattern_value = _pattern_hex_value | _pattern_dec_value

    _pattern_label_declaration = _pattern_label("label") + _D_COL

    _pattern_address_instruction = pp.oneOf(_address_mnemonics, caseless=True)(
        "mnemonic"
    ) + (_pattern_value("address") ^ _pattern_label("label"))

    _pattern_no_address_instruction = pp.oneOf(_no_address_mnemonics, caseless=True)(
        "mnemonic"
    )

    _pattern_instruction = pp.Optional(_pattern_label_declaration)("in_line_label") + (
        _pattern_address_instruction ^ _pattern_no_address_instruction
    )

    _directives = ["text", "data"]
    _type_directives = ["word"]

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
        ^ _pattern_instruction
        ^ _pattern_label_declaration("label_declaration")
    ) + pp.StringEnd().suppress()

    def parse(self, program: str, state: ToyArchitecturalState, **kwargs):
        """Parses the text format assembly program and loads it into the architectural state.

        Args:
            program (str): Text format Toy assembly program.
            state (ToyArchitecturalState): The architectural state into which the program should get loaded.

        Raises:
            ParserSyntaxException: Indicates a syntax error.
        """
        self.state: ToyArchitecturalState = state
        self.program = program
        self._sanitize()
        self._tokenize()
        self._segment()
        self._process_labels()
        self._write_data()
        self._load_instructions()

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
                        write_address, UInt16(self._value_to_int(value))
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
            self.state.memory.write_halfword(addr, UInt16(int(instr)))
        if len(instructions) >= 1:
            self.state.loaded_instruction = instructions[0]
            self.state.visualisation_values = SvgVisValues(
                pc_old=UInt16(0), ram_out=UInt16(int(instructions[0]))
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

    def _process_labels(self):
        """Takes the labels and computes the addresses for the labels from self.token_list and stores both in self.labels."""
        program_counter = 0
        for line_number, line, tokens in self.token_list:
            if tokens.get_name() == "label_declaration":
                self._add_label_mapping(
                    label=tokens.label,
                    value=program_counter,
                    line=line,
                    line_number=line_number,
                )
                continue
            if tokens.in_line_label:
                self._add_label_mapping(
                    label=tokens.in_line_label[0],
                    value=program_counter,
                    line=line,
                    line_number=line_number,
                )
            if tokens.mnemonic:  # if it is an instruction
                program_counter += 1
