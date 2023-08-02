from __future__ import annotations
from typing import TYPE_CHECKING
import pyparsing as pp
from dataclasses import dataclass

from architecture_simulator.isa.riscv.rv32i_instructions import instruction_map
from architecture_simulator.isa.riscv import instruction_types
from architecture_simulator.isa.riscv.rv32i_instructions import ECALL, EBREAK, FENCE

if TYPE_CHECKING:
    from architecture_simulator.isa.riscv.instruction_types import RiscvInstruction

# abi register names
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

reg_reg_reg_mnemonics = [
    "add",
    "sub",
    "sll",
    "slt",
    "sltu",
    "xor",
    "srl",
    "sra",
    "or",
    "and",
]

csr_mnemonics = ["csrrw", "csrrs", "csrrc"]

csr_i_mnemonics = ["csrrwi", "csrrsi", "csrrci"]

b_type_mnemonics = ["beq", "bne", "blt", "bge", "bltu", "bgeu"]

s_type_mnemonics = ["sb", "sh", "sw"]

normal_i_type_mnemonics = [
    "addi",
    "slti",
    "sltiu",
    "xori",
    "ori",
    "andi",
    "slli",
    "srli",
    "srai",
]

mem_i_type_mnemonics = ["lb", "lh", "lw", "lbu", "lhu", "jalr"]

u_type_mnemonic = ["lui", "auipc"]

# 0 to 31 for x... register names
reg_numbers = [str(i) for i in range(32)]


class RiscvParser:
    """A parser for RISC-V programs. It is capable of turning a text form program into instruction objects."""

    COMMA = pp.Literal(",").suppress()
    Paren_R = pp.Literal(")").suppress()
    Paren_L = pp.Literal("(").suppress()
    D_COL = pp.Literal(":").suppress()
    PLUS = pp.Literal("+").suppress()

    pattern_register = pp.oneOf(list(reg_mapping.keys())) | pp.Group(
        "x" + pp.oneOf(reg_numbers)
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
    pattern_r_type_instruction = pp.Group(
        pp.oneOf(reg_reg_reg_mnemonics, caseless=True)("mnemonic")
        + pattern_register("rd")
        + COMMA
        + pattern_register("rs1")
        + COMMA
        + pattern_register("rs2")
    )

    # I-Types, B-Types, S-Types
    pattern_reg_reg_imm_instruction = pp.Group(
        pp.oneOf(
            normal_i_type_mnemonics
            + mem_i_type_mnemonics
            + b_type_mnemonics
            + s_type_mnemonics,
            caseless=True,
        )("mnemonic")
        + pattern_register("reg1")
        + COMMA
        + pattern_register("reg2")
        + COMMA
        + pattern_imm("imm")
    )

    # B-Types
    pattern_b_type_instruction = pp.Group(
        pp.oneOf(b_type_mnemonics, caseless=True)("mnemonic")
        + pattern_register("reg1")
        + COMMA
        + pattern_register("reg2")
        + COMMA
        + (pattern_label + pattern_offset)
    )

    # I-Type-Memory-Instructions and S-Types
    pattern_memory_instruction = pp.Group(
        pp.oneOf(mem_i_type_mnemonics + s_type_mnemonics, caseless=True)("mnemonic")
        + pattern_register("reg1")
        + COMMA
        + pattern_imm("imm")
        + Paren_L
        + pattern_register("reg2")
        + Paren_R
    )

    # J-Types
    pattern_jal_instruction = pp.Group(
        pp.CaselessLiteral("jal")("mnemonic")
        + pattern_register("rd")
        + COMMA
        + (pattern_imm("imm") ^ (pattern_label + pattern_offset))
    )

    # U-Types
    pattern_u_type_instruction = pp.Group(
        pp.oneOf(u_type_mnemonic, caseless=True)("mnemonic")
        + pattern_register("rd")
        + COMMA
        + pattern_imm("imm")
    )

    # FENCE
    pattern_fence_instruction = pp.Group(
        pp.CaselessLiteral("fence")("mnemonic")
        + pattern_register("rd")
        + COMMA
        + pattern_register("rs1")
    )

    # CSR-Types
    pattern_reg_csr_reg_instruction = pp.Group(
        pp.oneOf(csr_mnemonics, caseless=True)("mnemonic")
        + pattern_register("rd")
        + COMMA
        + pattern_imm("csr")
        + COMMA
        + pattern_register("rs1")
    )

    # CSRI-Types
    pattern_reg_csr_imm_instruction = pp.Group(
        pp.oneOf(csr_i_mnemonics, caseless=True)("mnemonic")
        + pattern_register("rd")
        + COMMA
        + pattern_imm("csr")
        + COMMA
        + pattern_imm("uimm")
    )

    # ecall ebreak
    pattern_ecall_ebreak_instruction = (
        pp.CaselessLiteral("ecall") | pp.CaselessLiteral("ebreak")
    )("mnemonic")

    line = (
        (
            pattern_r_type_instruction
            ^ pattern_u_type_instruction
            ^ pattern_b_type_instruction
            ^ pattern_memory_instruction
            ^ pattern_reg_csr_reg_instruction
            ^ pattern_reg_csr_imm_instruction
            ^ pattern_reg_reg_imm_instruction
            ^ pattern_fence_instruction
            ^ pattern_jal_instruction
            ^ pattern_ecall_ebreak_instruction
            ^ (pattern_label + D_COL)
        )
    ) + pp.StringEnd().suppress()

    def _convert_label_or_imm(
        self,
        instruction_parsed: pp.ParseResults,
        labels: dict[str, int],
        address_count: int,
        line: str,  # for Exceptions
        line_number: int,  # for Exceptions
    ) -> int:
        # Checks if a imm or label was given
        # returns the integer value used in the construction of the instruction
        if instruction_parsed.get("imm"):
            imm_value = int(instruction_parsed.imm, base=0)
            if imm_value % 2:
                raise ParserOddImmediateException(line_number=line_number, line=line)
            else:
                return imm_value
        else:
            offset = 0
            if instruction_parsed.offset:
                offset = int(instruction_parsed.offset, base=0)
            try:
                return labels[instruction_parsed.label] + offset - address_count
            except KeyError:
                raise ParserLabelException(
                    line_number=line_number, line=line, label=instruction_parsed.label
                )

    def _convert_register_name(self, parsed_register: pp.ParseResults | str) -> int:
        """Converts a register string into a number of the correct register

        Args:
            parsed_register (pp.ParseResults | str): parse result of the register name or number. May be an ABI name or a number like x18.

        Returns:
            int: number of the register
        """
        if type(parsed_register[0]) == str:
            return reg_mapping[parsed_register[0]]
        else:
            return int(parsed_register[0][1])

    def _tokenize_assembly(
        self, assembly: str
    ) -> list[tuple[int, str, pp.ParseResults]]:
        """Turn assembly code into a list of parse results.

        Args:
            assembly (str): Text assembly which may contain labels and comments.

        Returns:
            list[tuple[int, str, pp.ParseResults]]: List of line number, original line and ParseResult.
        """
        # remove empty lines, lines that only contain white space and comment lines. Enumerate all lines before removing lines.
        enumerated_lines = [
            (index + 1, line)
            for index, line in enumerate(assembly.splitlines())
            if line.strip() and not line.strip().startswith("#")
        ]
        # remove comments from lines that also contain an instruction and strip the line
        enumerated_lines = [
            (index, line.split("#", 1)[0].strip()) for index, line in enumerated_lines
        ]
        # a line is a list of ParseResults, but there is only one element in each of those lists
        res: list[tuple[int, str, pp.ParseResults]] = []
        for index, line in enumerated_lines:
            try:
                res.append((index, line, self.line.parse_string(line)[0]))
            except pp.ParseException:
                raise ParserSyntaxException(line_number=index, line=line)
        return res

    def _compute_labels(
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

    def _tokens_to_instructions(
        self, parse_result: list[tuple[int, str, pp.ParseResults]], start_address: int
    ) -> list[RiscvInstruction]:
        """Turn parse results into instructions.

        Args:
            parse_result (list[tuple[int, str, pp.ParseResults]]): parsed assembly which may contain labels.

        Returns:
            list[Instruction]: list of executable instructions
        """
        instructions: list[RiscvInstruction] = []
        pure_parse_results = [result[2] for result in parse_result]
        labels = self._compute_labels(pure_parse_results, start_address)
        address_count: int = start_address

        for line_number, line, instruction_parsed in parse_result:
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
                        rs1=self._convert_register_name(instruction_parsed.rs1),
                        rs2=self._convert_register_name(instruction_parsed.rs2),
                        rd=self._convert_register_name(instruction_parsed.rd),
                    )
                )
            elif issubclass(instruction_class, instruction_types.ITypeInstruction):
                instructions.append(
                    instruction_class(
                        imm=int(instruction_parsed.imm, base=0),
                        # note: since I/S/B-Types use the same patterns but have different names for the registers (rs1,rs2 vs. rd,rs1),
                        # we instead use reg1 and reg2 as names
                        rs1=self._convert_register_name(instruction_parsed.reg2),
                        rd=self._convert_register_name(instruction_parsed.reg1),
                    )
                )
            elif issubclass(instruction_class, instruction_types.STypeInstruction):
                instructions.append(
                    instruction_class(
                        rs1=self._convert_register_name(instruction_parsed.reg2),
                        rs2=self._convert_register_name(instruction_parsed.reg1),
                        imm=int(instruction_parsed.imm, base=0),
                    )
                )
            elif issubclass(instruction_class, instruction_types.BTypeInstruction):
                # B-Types can use labels or numerical immediates, so convert that first
                imm_val = self._convert_label_or_imm(
                    instruction_parsed,
                    labels,
                    address_count,
                    line_number=line_number,
                    line=line,
                )

                instructions.append(
                    instruction_class(
                        rs1=self._convert_register_name(instruction_parsed.reg1),
                        rs2=self._convert_register_name(instruction_parsed.reg2),
                        imm=imm_val,
                    )
                )
            elif issubclass(instruction_class, instruction_types.UTypeInstruction):
                instructions.append(
                    instruction_class(
                        rd=self._convert_register_name(instruction_parsed.rd),
                        imm=int(instruction_parsed.imm, base=0),
                    )
                )
            elif issubclass(instruction_class, instruction_types.JTypeInstruction):
                # J-Types can use labels or numerical immediates, so convert that first
                imm_val = self._convert_label_or_imm(
                    instruction_parsed,
                    labels,
                    address_count,
                    line_number=line_number,
                    line=line,
                )

                instructions.append(
                    instruction_class(
                        rd=self._convert_register_name(instruction_parsed.rd),
                        imm=imm_val,
                    )
                )
            elif issubclass(instruction_class, instruction_types.CSRTypeInstruction):
                instructions.append(
                    instruction_class(
                        rd=self._convert_register_name(instruction_parsed.rd),
                        csr=int(instruction_parsed.csr, base=0),
                        rs1=self._convert_register_name(instruction_parsed.rs1),
                    )
                )
            elif issubclass(instruction_class, instruction_types.CSRITypeInstruction):
                # TODO: Add parser element for this type
                instructions.append(
                    instruction_class(
                        rd=self._convert_register_name(instruction_parsed.rd),
                        csr=int(instruction_parsed.csr, base=0),
                        uimm=int(instruction_parsed.uimm, base=0),
                    )
                )
            elif issubclass(instruction_class, instruction_types.FenceTypeInstruction):
                # TODO: Change me, if Fence gets implemented
                instructions.append(FENCE())
            address_count += instruction_map[instruction_parsed.mnemonic.lower()].length
        return instructions

    def parse(self, program: str, start_address: int = 0) -> list[RiscvInstruction]:
        """Turn assembly code into a list of executable instructions.

        Args:
            assembly (str): Text assembly which may contain labels and comments.

        Returns:
            list[Instructions]: List of executable instructions.
        """
        parsed = self._tokenize_assembly(program)
        return self._tokens_to_instructions(parsed, start_address=start_address)


@dataclass
class ParserException(Exception):
    """Base class for all exceptions that occur during parsing."""

    line_number: int
    line: str


@dataclass
class ParserSyntaxException(ParserException):
    """A syntax exception that can be raised if the tokenization fails."""

    def __repr__(self) -> str:
        return f"There was a syntax error in line {self.line_number}: {self.line}"


@dataclass
class ParserLabelException(ParserException):
    """An excpetion that can be raised if an instruction refers to an unknown label."""

    label: str

    def __repr__(self) -> str:
        return f"Label '{self.label}' does not exist in line {self.line_number}: {self.line}"


@dataclass
class ParserOddImmediateException(ParserException):
    """An exception that can be raised when an immediate value has to be even, because it will be used to modify the program counter."""

    def __repr__(self) -> str:
        return f"Immediate has to be even in line {self.line_number}: {self.line}"
