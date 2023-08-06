from __future__ import annotations
from typing import TYPE_CHECKING
import pyparsing as pp
from fixedint import MutableUInt16

from .toy_instructions import AddressTypeInstruction, ToyInstruction, instruction_map
from ..parser_exceptions import ParserSyntaxException

if TYPE_CHECKING:
    from architecture_simulator.uarch.toy.toy_architectural_state import (
        ToyArchitecturalState,
    )


class ToyParser:
    _address_mnemonics = ["STO", "LDA", "BRZ", "ADD", "SUB", "OR", "AND", "XOR"]
    _no_address_mnemonics = ["NOT", "INC", "DEC", "ZRO", "NOP"]

    _pattern_hex_value = pp.Combine("$" + pp.Word(pp.hexnums))
    _pattern_dec_value = pp.Word(pp.nums)

    _pattern_value = _pattern_hex_value | _pattern_dec_value

    _pattern_address_instruction = pp.oneOf(_address_mnemonics, caseless=True)(
        "mnemonic"
    ) + _pattern_value("address")

    _pattern_no_address_instruction = pp.oneOf(_no_address_mnemonics, caseless=True)(
        "mnemonic"
    )

    _pattern_write_data = (
        ":" + _pattern_value("address") + ":" + _pattern_value("value")
    )

    _pattern_line = (
        _pattern_address_instruction
        ^ _pattern_no_address_instruction
        ^ _pattern_write_data("write_data")
    ) + pp.StringEnd().suppress()

    def parse(self, program: str, state: ToyArchitecturalState):
        """Parses the text format assembly program and loads it into the architectural state.

        Args:
            program (str): Text format Toy assembly program.
            state (ToyArchitecturalState): The architectural state into which the program should get loaded.

        Raises:
            ParserSyntaxException: Indicates a syntax error.
        """
        sanitized_program = self._sanitize(program)
        token_list = []
        for linenumber, line in sanitized_program:
            try:
                token_list.append(self._pattern_line.parse_string(line))
            except pp.ParseException:
                raise ParserSyntaxException(line_number=linenumber, line=line)
        self._load_instructions(token_list=token_list, state=state)
        self._write_data(token_list=token_list, state=state)

    def _sanitize(self, program: str) -> list[tuple[int, str]]:
        """Removes leading/trailing whitespaces, empty lines, comments. Gives each line a linenumber (starting at 1)

        Args:
            program (str): A string containing possibly multiple instructions (separated by newlines), comments, ...

        Returns:
            list[tuple[int, str]]: A list of (linenumber, instruction) where instruction does not contain any bloat.
        """
        lines = program.splitlines()
        sanitized_program: list[tuple[int, str]] = []
        for index, line in enumerate(lines):
            # remove leading/trailing whitespaces
            line = line.strip()
            # skip empty lines and lines that start with a # (comments)
            if (not line) or line.startswith("#"):
                continue
            # strip comments that start after (possible) instructions
            instruction_part = line.split("#", maxsplit=1)[0].strip()
            # append linenumber (index+1) and instruction string
            sanitized_program.append((index + 1, instruction_part))
        return sanitized_program

    def _tokens_to_instruction(self, tokens: pp.ParseResults) -> ToyInstruction:
        """Pyparsing returns parse results for each line. This function converts tokens from one line, which were created from an instruction pattern,
        into one instruction object with matching arguments.

        Args:
            tokens (pp.ParseResults): The tokens from one instruction.

        Returns:
            ToyInstruction: A matching instruction object.
        """
        mnemonic = tokens.mnemonic.upper()
        instruction_class = instruction_map[mnemonic]
        if issubclass(instruction_class, AddressTypeInstruction):
            address = self._value_to_int(tokens.address)
            return instruction_class(address=address)
        return instruction_class()

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

    def _load_instructions(
        self, token_list: list[pp.ParseResults], state: ToyArchitecturalState
    ):
        """Given a list of tokens, this function will sort out those that are from instructions
        and then instantiate those instructions are write them to the instruction memory.

        Args:
            token_list (list[pp.ParseResults]): A list of tokens.
            state (ToyArchitecturalState): The state to write the instructions to.
        """
        instructions = []
        for tokens in token_list:
            if tokens.mnemonic:
                instructions.append(self._tokens_to_instruction(tokens))
        state.instruction_memory.write_instructions(instructions)

    def _write_data(
        self, token_list: list[pp.ParseResults], state: ToyArchitecturalState
    ):
        """Given a list of tokens, this function will sort out those which are data write commands
        and then write said data to the data memory of the state.

        Args:
            token_list (list[pp.ParseResults]): A list of tokens.
            state (ToyArchitecturalState): The state to write the data to.
        """
        for tokens in token_list:
            if tokens.write_data:
                address = self._value_to_int(tokens.address) % 4096
                value = MutableUInt16(self._value_to_int(tokens.value) % (2**16))
                state.data_memory.write_halfword(address=address, value=value)
