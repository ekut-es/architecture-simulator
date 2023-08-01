import pyparsing as pp

from ..parser import ParserSyntaxException
from .toy_instructions import AddressTypeInstruction, ToyInstruction, instruction_map


class ToyParser:
    ADDRESS_MNEMONICS = ["STO", "LDA", "BRZ", "ADD", "SUB", "OR", "AND", "XOR"]
    NO_ADDRESS_MNEMONICS = ["NOT", "INC", "DEC", "ZRO", "NOP"]

    pattern_hex_address = pp.Combine("$" + pp.Word(pp.hexnums, exact=3))

    pattern_address_instruction = pp.oneOf(ADDRESS_MNEMONICS, caseless=True)(
        "mnemonic"
    ) + pattern_hex_address("address")

    pattern_no_address_instruction = pp.oneOf(NO_ADDRESS_MNEMONICS, caseless=True)(
        "mnemonic"
    )

    pattern_line = (
        pattern_address_instruction ^ pattern_no_address_instruction
    ) + pp.StringEnd().suppress()

    def _sanitize(self, program: str) -> list[tuple[int, str]]:
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

    def parse(self, program: str) -> list[ToyInstruction]:
        sanitized_program = self._sanitize(program)
        instructions = []
        for linenumber, line in sanitized_program:
            try:
                tokens = self.pattern_line.parse_string(line)
                instructions.append(self._tokens_to_instruction(tokens))
            except pp.ParseException:
                raise ParserSyntaxException(line_number=linenumber, line=line)
        return instructions

    def _tokens_to_instruction(self, tokens: pp.ParseResults) -> ToyInstruction:
        mnemonic = tokens.mnemonic.upper()
        instruction_class = instruction_map[mnemonic]
        if issubclass(instruction_class, AddressTypeInstruction):
            address = self.address_to_int(tokens.address)
            return instruction_class(address=address)
        return instruction_class()

    def address_to_int(self, address: str) -> int:
        return int(address[1:], base=16)
