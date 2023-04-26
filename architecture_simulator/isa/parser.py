import pyparsing as pp

from .instruction_types import Instruction
from .rv32i_instructions import instruction_map


# TODO to be replaced by students with a class
def riscv_bnf():
    COMMA = pp.Literal(",").suppress()

    pattern_register = pp.Group(pp.one_of("r x") + pp.Word(pp.nums))
    pattern_reg_reg_reg_instruction = pp.Group(
        pp.Word(pp.alphas)("mnemonic")
        + pattern_register("rd")
        + COMMA
        + pattern_register("rs1")
        + COMMA
        + pattern_register("rs2")
    )

    riscv_bnf = pp.OneOrMore(pattern_reg_reg_reg_instruction) + pp.StringEnd()
    riscv_bnf.ignore(pp.Char("#") + pp.rest_of_line())

    return riscv_bnf


def riscv_parser(program: str):
    instructions: list[Instruction] = []
    instructions_parsed = riscv_bnf().parse_string(program)
    for instruction_parsed in instructions_parsed:
        if instruction_parsed.mnemonic != "":
            instruction_class = instruction_map[instruction_parsed.mnemonic.lower()]
            if (
                instruction_parsed.rd[0] == "r"
                or instruction_parsed.rs1[0] == "r"
                or instruction_parsed.rs2[0] == "r"
            ):
                # TODO: translate r notation to register number
                raise NotImplementedError()
            instructions.append(
                instruction_class(
                    rs1=int(instruction_parsed.rs1[1]),
                    rs2=int(instruction_parsed.rs2[1]),
                    rd=int(instruction_parsed.rd[1]),
                )
            )
    return instructions
