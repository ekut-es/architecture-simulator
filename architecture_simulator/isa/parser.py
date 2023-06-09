import pyparsing as pp
from architecture_simulator.isa.instruction_types import Instruction
from architecture_simulator.isa.rv32i_instructions import instruction_map
from architecture_simulator.isa import instruction_types as instruction_types
from architecture_simulator.isa.rv32i_instructions import ECALL, EBREAK, FENCE

reg_mapping = {
    "zero": 0,
    "ra": 1,
    "sp": 2,
    "gp": 3,
    "tp": 4,
    "t0": 5,
    "t1": 6,
    "t2": 7,
    "fp": 8,  # this is intentional
    "s0": 8,
    "s1": 9,
    "a0": 10,
    "a1": 11,
    "a2": 12,
    "a3": 13,
    "a4": 14,
    "a5": 15,
    "a6": 16,
    "a7": 17,
    "s2": 18,
    "s3": 19,
    "s4": 20,
    "s5": 21,
    "s6": 22,
    "s7": 23,
    "s8": 24,
    "s9": 25,
    "s10": 26,
    "s11": 27,
    "t3": 28,
    "t4": 29,
    "t5": 30,
    "t6": 31,
}


class RiscvParser:
    COMMA = pp.Literal(",").suppress()
    Paren_R = pp.Literal(")").suppress()
    Paren_L = pp.Literal("(").suppress()
    D_COL = pp.Literal(":").suppress()
    PLUS = pp.Literal("+").suppress()

    pattern_register = pp.Group(
        pp.one_of("x zero ra sp gp tp t s fp a") + pp.Optional(pp.Word(pp.nums))
    )

    pattern_label = pp.Word(pp.alphas + "_", pp.alphanums + "_")("label")

    pattern_imm = pp.Combine(
        pp.Optional("-")
        + (
            (
                pp.Combine("0x" + pp.Word(pp.hexnums))
                | pp.Combine("0b" + pp.Word("01"))
                | pp.Word(pp.nums)
            )
        )
    )

    pattern_offset = pp.Optional(
        PLUS + pp.Combine("0x" + pp.Word(pp.hexnums))("offset")
    )

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
        + (pattern_imm("imm") | (pattern_label + pattern_offset))
    )

    # I-Types, B-Types, S-Types
    pattern_reg_imm_reg_instruction = pp.Group(
        pp.Word(pp.alphas)("mnemonic")
        + pattern_register("reg1")
        + COMMA
        + pattern_imm("imm")
        + Paren_L
        + pattern_register("reg2")
        + Paren_R
    )

    # U-Types, J-Types, Fence
    pattern_reg_smth_instruction = pp.Group(
        pp.Word(pp.alphas)("mnemonic")
        + pattern_register("rd")
        + COMMA
        + (
            pattern_imm("imm")
            | pattern_register("rs1")
            | (pattern_label + pattern_offset)
        )
    )

    # CSR-Types
    pattern_reg_csr_reg_instruction = pp.Group(
        pp.Word(pp.alphas)("mnemonic")
        + pattern_register("rd")
        + COMMA
        + pattern_imm("csr")
        + COMMA
        + pattern_register("rs1")
    )

    # CSRI-Types
    pattern_reg_csr_imm_instruction = pp.Group(
        pp.Word(pp.alphas)("mnemonic")
        + pattern_register("rd")
        + COMMA
        + pattern_imm("csr")
        + COMMA
        + pattern_imm("uimm")
    )

    line = (
        (
            pattern_reg_reg_reg_instruction
            | pattern_reg_imm_reg_instruction
            | pattern_reg_csr_reg_instruction
            | pattern_reg_csr_imm_instruction
            | pattern_reg_reg_imm_instruction
            | pattern_reg_smth_instruction
            | (pattern_label + D_COL)
            | pp.Word(pp.alphas)("mnemonic")  # for ecall, ebreak
        )
    ) + pp.StringEnd().suppress()

    def convert_label_or_imm(
        self,
        instruction_parsed: pp.ParseResults,
        labels: dict[str, int],
        address_count: int,
    ) -> int:
        # Checks if a imm or label was given
        # returns the integer value used in the construction of the instruction
        # TODO: Throws exception if imm is uneven
        if instruction_parsed.get("imm"):
            return int(instruction_parsed.imm, base=0) // 2
        else:
            offset = 0
            if instruction_parsed.offset:
                offset = int(instruction_parsed.offset, base=0)
            return (labels[instruction_parsed.label] + offset - address_count) // 2

    def p_reg(self, parsed_register: pp.ParseResults) -> int:
        """Parses a register string into a number of the correct register

        Args:
            parsed_register (pp.ParseResults): parse result of the register name or number. May be an ABI name or a number like x18.

        Returns:
            int: number of the register
        """
        if parsed_register[0] == "x":
            return int(parsed_register[1])
        else:
            return reg_mapping["".join(parsed_register)]

    def parse_assembly(self, assembly: str) -> list[pp.ParseResults]:
        """Turn assembly code into a list of parse results.

        Args:
            assembly (str): Text assembly which may contain labels and comments.

        Returns:
            list[pp.ParseResults]: List of ParseResults, where each element is a instruction or label.
        """
        # remove empty lines, lines that only contain white space and comment lines
        lines = [
            line
            for line in assembly.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        # remove comments from linese that also contain an instruction and strip the line
        lines = [line.split("#", 1)[0].strip() for line in lines]
        # a line is a list of ParseResults, but there is only one element in each of those lists
        return [self.line.parse_string(line)[0] for line in lines]

    def compute_labels(
        self, parse_result: list[pp.ParseResults], start_address: int
    ) -> dict:
        """Compute the addresses for the labels.
        Args:
            parse_result list[pp.ParseResults]: Parsed assembly which may contain labels
            start_address (int): address of the first instruction.

        Returns:
            dict: addresses for the labels.
        """
        labels: dict[str, int] = {}
        instruction_address = start_address
        for i_parsed in parse_result:
            if (
                isinstance(i_parsed, str)
                and i_parsed != "ecall"
                and i_parsed != "ebreak"
            ):
                labels.update({i_parsed: instruction_address})
            else:
                mnemonic = (
                    i_parsed if type(i_parsed) == str else i_parsed.mnemonic
                ).lower()
                instruction_address += instruction_map[mnemonic].length
        return labels

    def parse_res_to_instructions(
        self, parse_result: list[pp.ParseResults], start_address: int
    ) -> list[Instruction]:
        """Turn parse results into instructions.

        Args:
            parse_result (list[pp.ParseResults]): parsed assembly which may contain labels.

        Returns:
            list[Instruction]: executable list of instructions
        """
        instructions: list[Instruction] = []
        labels = self.compute_labels(parse_result, start_address)
        address_count: int = start_address

        for instruction_parsed in parse_result:
            if isinstance(instruction_parsed, str):
                # skip if instruction_parsed is a label, but do not skip ecall/ebreak
                if instruction_parsed == "ecall":
                    instructions.append(ECALL(imm=0, rs1=0, rd=0))
                    address_count += ECALL.length
                if instruction_parsed == "ebreak":
                    instructions.append(EBREAK(imm=1, rs1=0, rd=0))
                    address_count += EBREAK.length
                continue
            instruction_class = instruction_map[instruction_parsed.mnemonic.lower()]
            if issubclass(instruction_class, instruction_types.RTypeInstruction):
                instructions.append(
                    instruction_class(
                        rs1=self.p_reg(instruction_parsed.rs1),
                        rs2=self.p_reg(instruction_parsed.rs2),
                        rd=self.p_reg(instruction_parsed.rd),
                    )
                )
            elif issubclass(instruction_class, instruction_types.ITypeInstruction):
                instructions.append(
                    instruction_class(
                        imm=int(instruction_parsed.imm, base=0),
                        # note: since I/S/B-Types use the same patterns but have different names for the registers (rs1,rs2 vs. rd,rs1),
                        # we instead use reg1 and reg2 as names
                        rs1=self.p_reg(instruction_parsed.reg2),
                        rd=self.p_reg(instruction_parsed.reg1),
                    )
                )
            elif issubclass(instruction_class, instruction_types.STypeInstruction):
                instructions.append(
                    instruction_class(
                        rs1=self.p_reg(instruction_parsed.reg2),
                        rs2=self.p_reg(instruction_parsed.reg1),
                        imm=int(instruction_parsed.imm, base=0),
                    )
                )
            elif issubclass(instruction_class, instruction_types.BTypeInstruction):
                # B-Types can use labels or numerical immediates, so convert that first
                imm_val = self.convert_label_or_imm(
                    instruction_parsed, labels, address_count
                )

                instructions.append(
                    instruction_class(
                        rs1=self.p_reg(instruction_parsed.reg1),
                        rs2=self.p_reg(instruction_parsed.reg2),
                        imm=imm_val,
                    )
                )
            elif issubclass(instruction_class, instruction_types.UTypeInstruction):
                instructions.append(
                    instruction_class(
                        rd=self.p_reg(instruction_parsed.rd),
                        imm=int(instruction_parsed.imm, base=0),
                    )
                )
            elif issubclass(instruction_class, instruction_types.JTypeInstruction):
                # J-Types can use labels or numerical immediates, so convert that first
                imm_val = self.convert_label_or_imm(
                    instruction_parsed, labels, address_count
                )

                instructions.append(
                    instruction_class(
                        rd=self.p_reg(instruction_parsed.rd),
                        imm=imm_val,
                    )
                )
            elif issubclass(instruction_class, instruction_types.CSRTypeInstruction):
                instructions.append(
                    instruction_class(
                        rd=self.p_reg(instruction_parsed.rd),
                        csr=int(instruction_parsed.csr, base=0),
                        rs1=self.p_reg(instruction_parsed.rs1),
                    )
                )
            elif issubclass(instruction_class, instruction_types.CSRITypeInstruction):
                # TODO: Add parser element for this type
                instructions.append(
                    instruction_class(
                        rd=self.p_reg(instruction_parsed.rd),
                        csr=int(instruction_parsed.csr, base=0),
                        uimm=int(instruction_parsed.uimm, base=0),
                    )
                )
            elif issubclass(instruction_class, instruction_types.fence):
                # TODO: Change me, if Fence gets implemented
                instructions.append(FENCE())
            address_count += instruction_map[instruction_parsed.mnemonic.lower()].length
        return instructions
