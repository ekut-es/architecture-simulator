import pyparsing as pp

from .instruction_types import Instruction
from .rv32i_instructions import instruction_map
from . import instruction_types as instruction_types


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

    pattern_memory_address = pp.Group(
        pp.Word(pp.nums)("imm") + "(" + pattern_register("rs1") + ")"
    )

    pattern_reg_reg_imm_instruction = pp.Group(
        pp.Word(pp.alphas)("mnemonic")
        + pattern_register("rd")
        + COMMA
        + pattern_register("rs1")
        + COMMA
        + pp.Word(pp.nums)("imm")
    )

    pattern_reg_memory_address = pp.Group(
        pp.Word(pp.alphas)("mnemonic")
        + pattern_register("rd")
        + COMMA
        + pattern_memory_address("memory")
    )

    pattern_reg_imm = pp.Group(
        pp.Word(pp.alphas)("mnemonic")
        + pattern_register("rd")
        + COMMA
        + pp.Word(pp.nums)("imm")
    )

    pattern_label = pp.Group(pp.Word(pp.alphas)("mnemonic") + ":")
    riscv_bnf = (
        pp.OneOrMore(
            pattern_reg_reg_reg_instruction
            | pattern_memory_address
            | pattern_reg_reg_imm_instruction
            | pattern_reg_memory_address
            | pattern_reg_imm
            | pattern_label
        )
        + pp.StringEnd()
    )
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
            if instruction_class.__base__ is instruction_types.RTypeInstruction:
                instructions.append(
                    instruction_class(
                        rs1=int("".join(instruction_parsed.rs1[1:])),
                        rs2=int("".join(instruction_parsed.rs2[1:])),
                        rd=int("".join(instruction_parsed.rd[1:])),
                    )
                )
            elif instruction_class.__base__ is instruction_types.ITypeInstruction:
                instructions.append(
                    instruction_class(
                        imm=int(instruction_parsed.imm),
                        rs1=int(instruction_parsed.rs1[1:]),
                        rd=int(instruction_parsed.rd[1:]),
                    )
                )
            elif instruction_class.__base__ is instruction_types.STypeInstruction:
                instructions.append(
                    instruction_class(
                        rs1=int(instruction_parsed.rs1[1:]),
                        rs2=int(instruction_parsed.rs2[1:]),
                        imm=int(instruction_parsed.imm),
                    )
                )
            elif instruction_class.__base__ is instruction_types.BTypeInstruction:
                instructions.append(
                    instruction_class(
                        rs1=int(instruction_parsed.rs1[1:]),
                        rs2=int(instruction_parsed.rs2[1:]),
                        imm=int(instruction_parsed.imm),
                    )
                )
            elif instruction_class.__base__ is instruction_types.UTypeInstruction:
                instructions.append(
                    instruction_class(
                        rd=int(instruction_parsed.rd[1:]),
                        imm=int(instruction_parsed.imm),
                    )
                )
            elif instruction_class.__base__ is instruction_types.JTypeInstruction:
                instructions.append(
                    instruction_class(
                        rd=int(instruction_parsed.rd[1:]),
                        imm=int(instruction_parsed.imm),
                    )
                )
            elif instruction_class.__base__ is instruction_types.CSRTypeInstruction:
                instructions.append(
                    instruction_class(
                        rd=int(instruction_parsed.rd[1:]),
                        csr=int(instruction_parsed.imm),
                        rs1=int(instruction_parsed.rs1[1:]),
                    )
                )
            elif instruction_class.__base__ is instruction_types.CSRITypeInstruction:
                instructions.append(
                    instruction_class(
                        rd=int(instruction_parsed.rd[1:]),
                        csr=int(instruction_parsed.imm),
                        uimm=int(instruction_parsed.uimm),
                    )
                )

    return instructions
