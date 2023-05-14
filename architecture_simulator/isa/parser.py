import pyparsing as pp

from .instruction_types import Instruction
from .rv32i_instructions import instruction_map
from . import instruction_types as instruction_types


# TODO to be replaced by students with a class
def riscv_bnf():
    COMMA = pp.Literal(",").suppress()
    Paren_R = pp.Literal(")").suppress()
    Paren_L = pp.Literal("(").suppress()
    D_COL = pp.Literal(":").suppress()

    pattern_register = pp.Group(pp.one_of("r x") + pp.Word(pp.nums))

    pattern_label = pp.Word(pp.alphas)("label") + D_COL

    pattern_imm = pp.Combine(pp.Optional("-") + pp.Word(pp.nums))("imm")

    # R-Types
    pattern_reg_reg_reg_instruction = pp.Group(
        pp.Word(pp.alphas)("mnemonic")
        + pattern_register("rd")
        + COMMA
        + pattern_register("rs1")
        + COMMA
        + pattern_register("rs2")
    )

    # I-Types, B-Types, S-Types
    pattern_reg_reg_imm_instruction = pp.Group(
        pp.Word(pp.alphas)("mnemonic")
        + pattern_register("reg1")
        + COMMA
        + pattern_register("reg2")
        + COMMA
        + (pattern_imm | pp.Word(pp.alphas)("label"))
    )

    # I-Types, B-Types, S-Types
    pattern_reg_imm_reg_instruction = pp.Group(
        pp.Word(pp.alphas)("mnemonic")
        + pattern_register("reg1")
        + COMMA
        + (pattern_imm | pp.Word(pp.alphas)("label"))
        + Paren_L
        + pattern_register("reg2")
        + Paren_R
    )

    # U-Types, J-Types
    pattern_reg_imm_instruction = pp.Group(
        pp.Word(pp.alphas)("mnemonic")
        + pattern_register("rd")
        + COMMA
        + (pattern_imm | pp.Word(pp.alphas)("label"))
    )

    riscv_bnf = (
        pp.OneOrMore(
            pattern_reg_reg_reg_instruction
            | pattern_reg_imm_reg_instruction
            | pattern_reg_reg_imm_instruction
            | pattern_reg_imm_instruction
            | pattern_label
        )
        + pp.StringEnd()
    )
    riscv_bnf.ignore(pp.Char("#") + pp.rest_of_line())

    return riscv_bnf


def riscv_parser(program: str):
    instructions: list[Instruction] = []
    labels, instructions_parsed = process_labels(riscv_bnf().parse_string(program), 0)

    for instruction_number, instruction_parsed in enumerate(instructions_parsed):
        if instruction_parsed.mnemonic != "":
            instruction_class = instruction_map[instruction_parsed.mnemonic.lower()]
            # if (
            #     instruction_parsed.rd[0] == "r"
            #     or instruction_parsed.rs1[0] == "r"
            #     or instruction_parsed.rs2[0] == "r"
            # ):
            #     # TODO: translate r notation to register number
            #     raise NotImplementedError()
            if instruction_class.__base__ is instruction_types.RTypeInstruction:
                instructions.append(
                    instruction_class(
                        rs1=int(instruction_parsed.rs1[1]),
                        rs2=int(instruction_parsed.rs2[1]),
                        rd=int(instruction_parsed.rd[1]),
                    )
                )
            elif instruction_class.__base__ is instruction_types.ITypeInstruction:
                instructions.append(
                    instruction_class(
                        imm=int(instruction_parsed.imm),
                        # because an i type instruction may be written in two diffrent patterns the "reg" notation is used
                        # ex: lb x1, 33(x2) | addi x1, x2, 33
                        rs1=int(instruction_parsed.reg2[1]),
                        rd=int(instruction_parsed.reg1[1]),
                    )
                )
            elif instruction_class.__base__ is instruction_types.STypeInstruction:
                instructions.append(
                    instruction_class(
                        rs1=int(instruction_parsed.reg2[1]),
                        rs2=int(instruction_parsed.reg1[1]),
                        imm=int(instruction_parsed.imm),
                    )
                )
            elif instruction_class.__base__ is instruction_types.BTypeInstruction:
                # TODO: Throws exception if imm is uneven
                imm_val = -1
                if instruction_parsed.imm.isdigit():
                    imm_val = int(int(instruction_parsed.imm) / 2)
                else:
                    imm_val = int(
                        (labels[instruction_parsed.label] - instruction_number * 4) / 2
                    )

                instructions.append(
                    instruction_class(
                        rs1=int(instruction_parsed.reg1[1]),
                        rs2=int(instruction_parsed.reg2[1]),
                        imm=imm_val,
                    )
                )
            elif instruction_class.__base__ is instruction_types.UTypeInstruction:
                instructions.append(
                    instruction_class(
                        rd=int(instruction_parsed.rd[1]),
                        imm=int(instruction_parsed.imm),
                    )
                )
            elif instruction_class.__base__ is instruction_types.JTypeInstruction:
                # TODO: Throws exception if imm is uneven
                imm_val = -1
                if instruction_parsed.imm.isdigit():
                    imm_val = int(int(instruction_parsed.imm) / 2)
                else:
                    imm_val = int(
                        (labels[instruction_parsed.label] - instruction_number * 4) / 2
                    )

                instructions.append(
                    instruction_class(
                        rd=int(instruction_parsed.rd[1]),
                        imm=imm_val,
                    )
                )
            elif instruction_class.__base__ is instruction_types.CSRTypeInstruction:
                instructions.append(
                    instruction_class(
                        rd=int(instruction_parsed.reg1[1]),
                        csr=int(instruction_parsed.imm),
                        rs1=int(instruction_parsed.reg2[1]),
                    )
                )
            elif instruction_class.__base__ is instruction_types.CSRITypeInstruction:
                # TODO: Add parser element for this type
                instructions.append(
                    instruction_class(
                        rd=int(instruction_parsed.rd[1]),
                        csr=int(instruction_parsed.imm),
                        uimm=int(instruction_parsed.uimm),
                    )
                )

    return instructions


def process_labels(
    input: pp.ParseResults, start_address: int
) -> tuple[dict[str, int], list[pp.ParseResults]]:
    """Takes results from parser and calculates all label addresses and returns a list containing only instructions

    Args:
        input (pp.ParseResults): Result from pyparser
        start_address (int): address of first instruction

    Returns:
        tuple[dict[str, int], list[pp.ParseResults]]: dict containing the addresses for the labels and a list of the instructions
    """
    labels = {}
    instruction_address = start_address
    instructions: list[pp.ParseResults] = []
    for i_parsed in input:
        if isinstance(i_parsed, str):
            labels.update({i_parsed: instruction_address})
        else:
            instructions.append(i_parsed)
            instruction_address += 4
    return (labels, instructions)
