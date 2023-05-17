import pyparsing as pp

from .instruction_types import Instruction
from .rv32i_instructions import instruction_map
from . import instruction_types as instruction_types


class RiscvParser:
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
    ).ignore(pp.Char("#") + pp.rest_of_line())

    def parse_assembly(self, assembly: str) -> pp.ParseResults:
        """Turn assembly code into parse results.

        Args:
            assembly (str): Text assembly which may contain labels and comments.

        Returns:
            pp.ParseResults: Parse results.
        """
        return self.riscv_bnf.parse_string(assembly)

    def compute_labels(self, parse_result: pp.ParseResults, start_address: int) -> dict:
        """Compute the addresses for the labels.
        Args:
            parse_result (pp.ParseResults): Parsed assembly which may contain labels
            start_address (int): address of the first instruction.

        Returns:
            dict: addresses for the labels.
        """
        labels = {}
        instruction_address = start_address
        for i_parsed in parse_result:
            if isinstance(i_parsed, str):
                labels.update({i_parsed: instruction_address})
            else:
                instruction_address += 4
        return labels

    def parse_res_to_instructions(
        self, parse_result: pp.ParseResults, start_address: int
    ) -> list[Instruction]:
        """Turn parse results into instructions.

        Args:
            parse_result (pp.ParseResults): parsed assembly which may contain labels.

        Returns:
            list[Instruction]: executable list of instructions
        """
        instructions: list[Instruction] = []
        labels = self.compute_labels(parse_result, start_address)
        address_count: int = start_address

        for instruction_parsed in parse_result:
            if isinstance(instruction_parsed, str):
                continue
            instruction_class = instruction_map[instruction_parsed.mnemonic.lower()]
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
                    imm_val = int(instruction_parsed.imm) // 2
                else:
                    imm_val = (labels[instruction_parsed.label] - address_count) // 2

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
                    imm_val = int(instruction_parsed.imm) // 2
                else:
                    imm_val = (labels[instruction_parsed.label] - address_count) // 2

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
            # TODO: If instructions with length != 4 Bytes are supported the Instruction Type needs to be checked
            address_count += 4
        return instructions
