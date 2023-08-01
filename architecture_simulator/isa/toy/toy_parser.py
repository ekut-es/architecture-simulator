import pyparsing as pp


class ToyParser:
    ADDRESS_MNEMONICS = ["STO", "LDA", "BRZ", "ADD", "SUB", "OR", "AND", "XOR"]
    NO_ADDRESS_MNEMONICS = ["NOT", "INC", "DEC", "ZRO", "NOP"]

    pattern_hex_address = pp.Combine("$" + pp.Word(pp.hexnums[3], exact=3))

    pattern_address_instruction = pp.oneOf(ADDRESS_MNEMONICS, caseless=True)(
        "mnemonic"
    ) + pattern_hex_address("address")

    pattern_no_address_instruction = pp.oneOf(NO_ADDRESS_MNEMONICS, caseless=True)(
        "mnemonic"
    )

    pattern_line = (
        pattern_address_instruction ^ pattern_no_address_instruction
    ) + pp.StringEnd().suppress()

    def sanitize(self, program: str) -> list[tuple[int, str]]:
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
