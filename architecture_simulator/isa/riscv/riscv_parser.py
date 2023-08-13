from __future__ import annotations
from typing import TYPE_CHECKING
import pyparsing as pp
from dataclasses import dataclass
import fixedint

from architecture_simulator.isa.riscv.rv32i_instructions import instruction_map
import architecture_simulator.isa.riscv.instruction_types as instruction_types
from architecture_simulator.isa.riscv.rv32i_instructions import ECALL, EBREAK, FENCE

if TYPE_CHECKING:
    from architecture_simulator.isa.riscv.instruction_types import RiscvInstruction
    from architecture_simulator.uarch.riscv.riscv_architectural_state import (
        RiscvArchitecturalState,
    )


class RiscvParser:
    """A parser for RISC-V programs. It is capable of turning a text form program into instruction objects."""

    _directives = ["text", "data"]
    _type_directives = ["byte", "half", "word"]

    # abi register names
    _reg_mapping = {
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

    _reg_reg_reg_mnemonics = [
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

    _normal_i_type_mnemonics = [
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

    _mem_i_type_mnemonics = ["lb", "lh", "lw", "lbu", "lhu", "jalr"]

    _mem_pseudo_mnemonics = ["la"]

    _u_type_mnemonics = ["lui", "auipc"]

    _csr_mnemonics = ["csrrw", "csrrs", "csrrc"]

    _csr_i_mnemonics = ["csrrwi", "csrrsi", "csrrci"]

    _b_type_mnemonics = ["beq", "bne", "blt", "bge", "bltu", "bgeu"]

    _s_type_mnemonics = ["sb", "sh", "sw"]

    # 0 to 31 for x... register names
    _reg_numbers = [str(i) for i in range(32)]

    _DOT = pp.Literal(".")
    _COMMA = pp.Literal(",").suppress()
    _Paren_R = pp.Literal(")").suppress()
    _Paren_L = pp.Literal("(").suppress()
    _Bracket_R = pp.Literal("]").suppress()
    _Bracket_L = pp.Literal("[").suppress()
    _D_COL = pp.Literal(":").suppress()
    _PLUS = pp.Literal("+").suppress()

    _pattern_directive = pp.Group(_DOT + pp.oneOf(_directives)("directive"))

    _pattern_type_directive = pp.Group(_DOT + pp.oneOf(_type_directives)("type"))

    _pattern_register = pp.oneOf(list(_reg_mapping.keys())) | pp.Group(
        "x" + pp.oneOf(_reg_numbers)
    )

    _pattern_label = pp.Word(pp.alphas + "_", pp.alphanums + "_")("label")

    _pattern_imm = pp.Combine(
        pp.Optional("-")
        + (
            (
                pp.Combine("0x" + pp.Word(pp.hexnums))
                | pp.Combine("0b" + pp.Word("01"))
                | pp.Word(pp.nums)
            )
        )
    )

    _pattern_offset = pp.Optional(
        _PLUS + pp.Combine("0x" + pp.Word(pp.hexnums))("offset")
    )

    _pattern_index = pp.Combine(_Bracket_L + pp.Word(pp.nums) + _Bracket_R)

    _pattern_variable = pp.Combine(
        _pattern_label("name") + pp.Optional(_pattern_index)("index")
    )

    _pattern_variable_declaration = pp.Group(
        _pattern_label("name")
        + _D_COL
        + _pattern_type_directive("type")
        + pp.delimitedList(_pattern_imm, delim=",")("values")
    )

    # R-Types
    _pattern_r_type_instruction = pp.Group(
        pp.oneOf(_reg_reg_reg_mnemonics, caseless=True)("mnemonic")
        + _pattern_register("rd")
        + _COMMA
        + _pattern_register("rs1")
        + _COMMA
        + _pattern_register("rs2")
    )

    # I-Types, B-Types, S-Types
    _pattern_reg_reg_imm_instruction = pp.Group(
        pp.oneOf(
            _normal_i_type_mnemonics
            + _mem_i_type_mnemonics
            + _b_type_mnemonics
            + _s_type_mnemonics,
            caseless=True,
        )("mnemonic")
        + _pattern_register("reg1")
        + _COMMA
        + _pattern_register("reg2")
        + _COMMA
        + _pattern_imm("imm")
    )

    # B-Types
    _pattern_b_type_instruction = pp.Group(
        pp.oneOf(_b_type_mnemonics, caseless=True)("mnemonic")
        + _pattern_register("reg1")
        + _COMMA
        + _pattern_register("reg2")
        + _COMMA
        + (_pattern_label + _pattern_offset)
    )

    # I-Type-Memory-Instructions and S-Types
    _pattern_memory_instruction = pp.Group(
        pp.oneOf(_mem_i_type_mnemonics + _s_type_mnemonics, caseless=True)("mnemonic")
        + _pattern_register("reg1")
        + _COMMA
        + _pattern_imm("imm")
        + _Paren_L
        + _pattern_register("reg2")
        + _Paren_R
    )

    # Pseudo-I-Type-Memory-Instructions and la
    _pattern_memory_pseudo_instruction = pp.Group(
        pp.oneOf(_mem_i_type_mnemonics + _mem_pseudo_mnemonics, caseless=True)(
            "mnemonic"
        )
        + _pattern_register("reg1")
        + _COMMA
        + _pattern_variable("variable")
    )

    # Pseudo-S-Types
    _pattern_s_pseudo_instruction = pp.Group(
        pp.oneOf(_s_type_mnemonics, caseless=True)("mnemonic")
        + _pattern_register("reg1")
        + _COMMA
        + _pattern_variable("variable")
        + _COMMA
        + _pattern_register("reg2")
    )

    # J-Types
    _pattern_jal_instruction = pp.Group(
        pp.CaselessLiteral("jal")("mnemonic")
        + _pattern_register("rd")
        + _COMMA
        + (_pattern_imm("imm") ^ (_pattern_label + _pattern_offset))
    )

    # U-Types
    _pattern_u_type_instruction = pp.Group(
        pp.oneOf(_u_type_mnemonics, caseless=True)("mnemonic")
        + _pattern_register("rd")
        + _COMMA
        + _pattern_imm("imm")
    )

    # FENCE
    _pattern_fence_instruction = pp.Group(
        pp.CaselessLiteral("fence")("mnemonic")
        + _pattern_register("rd")
        + _COMMA
        + _pattern_register("rs1")
    )

    # CSR-Types
    _pattern_reg_csr_reg_instruction = pp.Group(
        pp.oneOf(_csr_mnemonics, caseless=True)("mnemonic")
        + _pattern_register("rd")
        + _COMMA
        + _pattern_imm("csr")
        + _COMMA
        + _pattern_register("rs1")
    )

    # CSRI-Types
    _pattern_reg_csr_imm_instruction = pp.Group(
        pp.oneOf(_csr_i_mnemonics, caseless=True)("mnemonic")
        + _pattern_register("rd")
        + _COMMA
        + _pattern_imm("csr")
        + _COMMA
        + _pattern_imm("uimm")
    )

    # ecall ebreak
    _pattern_ecall_ebreak_instruction = (
        pp.CaselessLiteral("ecall") | pp.CaselessLiteral("ebreak")
    )("mnemonic")

    # nop
    _pattern_nop_instruction = pp.CaselessLiteral("nop")("mnemonic")

    # li
    _pattern_li_instruction = pp.Group(
        pp.CaselessLiteral("li")("mnemonic")
        + _pattern_register("rd")
        + _COMMA
        + _pattern_imm("imm")
    )

    _pattern_line = (
        (
            _pattern_directive
            ^ _pattern_variable_declaration("variable_declaration")
            ^ _pattern_r_type_instruction
            ^ _pattern_u_type_instruction
            ^ _pattern_b_type_instruction
            ^ _pattern_memory_instruction
            ^ _pattern_memory_pseudo_instruction
            ^ _pattern_s_pseudo_instruction
            ^ _pattern_reg_csr_reg_instruction
            ^ _pattern_reg_csr_imm_instruction
            ^ _pattern_reg_reg_imm_instruction
            ^ _pattern_fence_instruction
            ^ _pattern_jal_instruction
            ^ _pattern_ecall_ebreak_instruction
            ^ _pattern_nop_instruction
            ^ _pattern_li_instruction
            ^ (_pattern_label + _D_COL)("label_declaration")
        )
    ) + pp.StringEnd().suppress()

    def parse(
        self, program: str, state: RiscvArchitecturalState, start_address: int = 0
    ) -> None:
        """Parses the text format assembly program and loads it into the architectural state.

        Args:
            program (str): Text format RISC-V assembly program.
            state (RiscvArchitecturalState): The architectural state into which the program should get loaded.
        """

        self.state = state
        self.program = program
        self.start_address = (
            state.instruction_memory.address_range.start
            if start_address == 0
            else start_address
        )
        self._sanitize()
        self._tokenize()
        self._segment()
        self._write_data()
        self._process_pseudo_instructions()
        self._process_labels()
        self._write_instructions()

    def _sanitize(self) -> None:
        """Removes leading/trailing whitespace, empty lines, comments from self.program. Gives each line a line number (starting at 1). Stores the result in self.sanitized_program."""

        # remove empty lines, lines that only contain white space and comment lines. Enumerate all lines before removing lines.
        self.sanitized_program = [
            (index + 1, line)
            for index, line in enumerate(self.program.splitlines())
            if line.strip() and not line.strip().startswith("#")
        ]
        # remove comments from lines that also contain an instruction and strip the line
        self.sanitized_program = [
            (index, line.split("#", 1)[0].strip())
            for index, line in self.sanitized_program
        ]

    def _tokenize(self) -> None:
        """Turns self.sanitized_program into tokens and stores them in self.token_list (together with the line numbers and the original line)."""
        self.token_list: list[tuple[int, str, pp.ParseResults]] = []
        for line_number, line in self.sanitized_program:
            try:
                self.token_list.append(
                    (line_number, line, self._pattern_line.parseString(line)[0])
                )
            except pp.ParseException:
                raise ParserSyntaxException(line_number=line_number, line=line)

    def _segment(self) -> None:
        """Determines the segments of the program (data and text) and stores them in self.data and self.text."""

        self.data: list[tuple[int, str, pp.ParseResults]] = []
        self.text: list[tuple[int, str, pp.ParseResults]] = []

        data_exists = False
        text_exists = True
        self.text = self.token_list

        # first line is segment directive
        if not isinstance(self.token_list[0][2], str):
            if self.token_list[0][2].get("directive") == "data":
                data_exists = True
                text_exists = False
                self.data = self.token_list[1:]
                self.text = []
            elif self.token_list[0][2].get("directive") == "text":
                self.text = self.token_list[1:]

        for line_number, line, line_parsed in self.token_list[1:]:
            if isinstance(line_parsed, str):
                continue
            if line_parsed.get("directive") == "data":
                if not data_exists:
                    data_exists = True
                    index = self.text.index((line_number, line, line_parsed))
                    self.data = self.text[index + 1 :]
                    self.text = self.text[:index]
                else:
                    raise ParserDirectiveException(line_number=line_number, line=line)
            elif line_parsed.get("directive") == "text":
                if not text_exists:
                    text_exists = True
                    index = self.data.index((line_number, line, line_parsed))
                    self.text = self.data[index + 1 :]
                    self.data = self.data[:index]
                else:
                    raise ParserDirectiveException(line_number=line_number, line=line)
            elif line_parsed.get("directive") is not None:
                raise ParserDirectiveException(line_number=line_number, line=line)

    def _write_data(self) -> None:
        """Looks for data write commands in self.data. Stores the variables in self.variables and writes them to the memory of self.state."""

        # variables are stored as (name: (address, byte_length))
        self.variables: dict[str, tuple[int, int]] = {}
        address_counter = self.state.memory.min_bytes

        for line_number, line, line_parsed in self.data:
            if isinstance(line_parsed, str) or (
                line_parsed.get_name() != "variable_declaration"
            ):
                raise ParserDataSyntaxException(line_number=line_number, line=line)
            else:
                if line_parsed.name in self.variables:
                    raise ParserDataDuplicateException(
                        name=line_parsed.name, line_number=line_number, line=line
                    )
                if line_parsed.type.type == "byte":
                    self.variables.update(
                        {line_parsed.get("name"): (address_counter, 1)}
                    )
                    for val in line_parsed.get("values"):
                        self.state.memory.write_byte(
                            address_counter, fixedint.MutableUInt8(int(val, base=0))
                        )
                        address_counter += 1
                elif line_parsed.type.type == "half":
                    self.variables.update(
                        {line_parsed.get("name"): (address_counter, 2)}
                    )
                    for val in line_parsed.get("values"):
                        self.state.memory.write_halfword(
                            address_counter, fixedint.MutableUInt16(int(val, base=0))
                        )
                        address_counter += 2
                elif line_parsed.type.type == "word":
                    self.variables.update(
                        {line_parsed.get("name"): (address_counter, 4)}
                    )
                    for val in line_parsed.get("values"):
                        self.state.memory.write_word(
                            address_counter, fixedint.MutableUInt32(int(val, base=0))
                        )
                        address_counter += 4

    def _process_pseudo_instructions(self) -> None:
        """Converts pseudo instructions in self.text into regular instructions, and variables into addresses."""

        for line_number, line, line_parsed in self.text:
            index = self.text.index((line_number, line, line_parsed))
            if line_parsed == "nop":
                self.text[index] = (
                    line_number,
                    line,
                    self._pattern_line.parse_string("addi x0, x0, 0")[0],
                )
            elif (
                not isinstance(line_parsed, str)
                and line_parsed.get("mnemonic") is not None
            ):
                mnemonic = line_parsed.get("mnemonic").lower()
                if mnemonic == "li":
                    register_name = (
                        line_parsed.rd[0]
                        if type(line_parsed.rd[0]) == str
                        else "x" + line_parsed.rd[0][1]
                    )
                    imm = int(line_parsed.imm, base=0)
                    lui_imm = int(fixedint.MutableUInt32(imm)) >> 12
                    # get the 12 first bits
                    addi_imm = int(fixedint.MutableUInt32(imm)) & 0xFFF
                    # compensate addi sign extension
                    if addi_imm > 2047 or addi_imm < -2048:
                        lui_imm += 1
                    # insert lui, addi into self.text if imm is outside of 12 bit range
                    if imm > 2047 or imm < -2048:
                        self.text[index] = (
                            line_number,
                            line,
                            self._pattern_line.parse_string(
                                f"lui {register_name}, {lui_imm}"
                            )[0],
                        )
                        self.text.insert(
                            index + 1,
                            (
                                line_number,
                                line,
                                self._pattern_line.parse_string(
                                    f"addi {register_name}, {register_name}, {addi_imm}"
                                )[0],
                            ),
                        )
                    else:
                        # insert just addi into self.text, overwrite register content (x0+imm)
                        self.text[index] = (
                            line_number,
                            line,
                            self._pattern_line.parse_string(
                                f"addi {register_name}, x0, {imm}"
                            )[0],
                        )
                elif (
                    mnemonic in self._mem_i_type_mnemonics
                    or mnemonic in self._mem_pseudo_mnemonics
                ):
                    if line_parsed.get("variable"):
                        if line_parsed.get("variable").name not in self.variables:
                            raise ParserVariableException(
                                line_number=line_number,
                                line=line,
                                name=line_parsed.get("variable").name,
                            )
                        register_name = (
                            line_parsed.reg1[0]
                            if type(line_parsed.reg1[0]) == str
                            else "x" + line_parsed.reg1[0][1]
                        )
                        # determine array index (size*index)
                        array_index = (self.variables[line_parsed.variable.name][1]) * (
                            int(line_parsed.variable.index)
                            if line_parsed.variable.index
                            else 0
                        )
                        # address with array offset
                        address = (
                            self.variables[line_parsed.variable.name][0] + array_index
                        )
                        lui_imm = int(fixedint.MutableUInt32(address)) >> 12
                        # get the 12 first bits
                        addi_imm = int(fixedint.MutableUInt32(address)) & 0xFFF
                        # compensate addi sign extension
                        if addi_imm > 2047 or addi_imm < -2048:
                            lui_imm += 1
                        # insert lui, addi into self.text
                        self.text[index] = (
                            line_number,
                            line,
                            self._pattern_line.parse_string(
                                f"lui {register_name}, {lui_imm}"
                            )[0],
                        )
                        self.text.insert(
                            index + 1,
                            (
                                line_number,
                                line,
                                self._pattern_line.parse_string(
                                    f"addi {register_name}, {register_name}, {addi_imm}"
                                )[0],
                            ),
                        )
                        # if instruction is pseudo lb/lh/lw/lbu/lhu
                        if mnemonic in self._mem_i_type_mnemonics:
                            # insert "unpseudoified" version
                            self.text.insert(
                                index + 2,
                                (
                                    line_number,
                                    line,
                                    self._pattern_line.parse_string(
                                        f"{mnemonic} {register_name}, 0({register_name})"
                                    )[0],
                                ),
                            )
                elif mnemonic in self._s_type_mnemonics and line_parsed.get("variable"):
                    if line_parsed.get("variable").name not in self.variables:
                        raise ParserVariableException(
                            line_number=line_number,
                            line=line,
                            name=line_parsed.get("variable").name,
                        )
                    register_name = (
                        line_parsed.reg1[0]
                        if type(line_parsed.reg1[0]) == str
                        else "x" + line_parsed.reg1[0][1]
                    )
                    address_register_name = (
                        line_parsed.reg2[0]
                        if type(line_parsed.reg2[0]) == str
                        else "x" + line_parsed.reg2[0][1]
                    )
                    # determine array index (size*index)
                    array_index = (self.variables[line_parsed.variable.name][1]) * (
                        int(line_parsed.variable.index)
                        if line_parsed.variable.index
                        else 0
                    )
                    # address with array offset
                    address = self.variables[line_parsed.variable.name][0] + array_index
                    lui_imm = int(fixedint.MutableUInt32(address)) >> 12
                    # get the 12 first bits
                    addi_imm = int(fixedint.MutableUInt32(address)) & 0xFFF
                    # compensate addi sign extension
                    if addi_imm > 2047 or addi_imm < -2048:
                        lui_imm += 1
                    # insert lui, addi into self.text
                    self.text[index] = (
                        line_number,
                        line,
                        self._pattern_line.parse_string(
                            f"lui {address_register_name}, {lui_imm}"
                        )[0],
                    )
                    self.text.insert(
                        index + 1,
                        (
                            line_number,
                            line,
                            self._pattern_line.parse_string(
                                f"addi {address_register_name}, {address_register_name}, {addi_imm}"
                            )[0],
                        ),
                    )
                    # insert "unpseudoified" version of sb/sh/sw
                    self.text.insert(
                        index + 2,
                        (
                            line_number,
                            line,
                            self._pattern_line.parse_string(
                                f"{mnemonic} {register_name}, 0({address_register_name})"
                            )[0],
                        ),
                    )

    def _process_labels(self) -> None:
        """Computes the addresses of all labels in the text segment and stores them in self.labels"""
        self.labels: dict[str, int] = {}
        instruction_address = self.start_address
        for line_number, line, line_parsed in self.text:
            if (
                isinstance(line_parsed, str)
                and line_parsed != "ecall"
                and line_parsed != "ebreak"
            ):
                self.labels.update({line_parsed: instruction_address})
            else:
                mnemonic = (
                    line_parsed if type(line_parsed) == str else line_parsed.mnemonic
                )
                if mnemonic is not None and mnemonic.lower() in instruction_map:
                    instruction_address += instruction_map[mnemonic.lower()].length

    def _write_instructions(self) -> None:
        """Instantiates the instructions from self.text and writes them to the instruction memory of self.state."""

        instructions: list[RiscvInstruction] = []
        address_count: int = self.start_address

        for line_number, line, line_parsed in self.text:
            if isinstance(line_parsed, str):
                # skip if instruction_parsed is a label, but do not skip ecall/ebreak
                if line_parsed == "ecall":
                    instructions.append(ECALL(imm=0, rs1=0, rd=0))
                    address_count += ECALL.length
                if line_parsed == "ebreak":
                    instructions.append(EBREAK(imm=1, rs1=0, rd=0))
                    address_count += EBREAK.length
                continue
            if (
                line_parsed.mnemonic is None
                or line_parsed.mnemonic.lower() not in instruction_map
            ):
                raise ParserSyntaxException(line_number=line_number, line=line)
            instruction_class = instruction_map[line_parsed.mnemonic.lower()]
            if issubclass(instruction_class, instruction_types.RTypeInstruction):
                instructions.append(
                    instruction_class(
                        rs1=self._convert_register_name(line_parsed.rs1),
                        rs2=self._convert_register_name(line_parsed.rs2),
                        rd=self._convert_register_name(line_parsed.rd),
                    )
                )
            elif issubclass(instruction_class, instruction_types.ITypeInstruction):
                instructions.append(
                    instruction_class(
                        imm=int(line_parsed.imm, base=0),
                        # note: since I/S/B-Types use the same patterns but have different names for the registers (rs1,rs2 vs. rd,rs1),
                        # we instead use reg1 and reg2 as names
                        rs1=self._convert_register_name(line_parsed.reg2),
                        rd=self._convert_register_name(line_parsed.reg1),
                    )
                )
            elif issubclass(instruction_class, instruction_types.STypeInstruction):
                instructions.append(
                    instruction_class(
                        rs1=self._convert_register_name(line_parsed.reg2),
                        rs2=self._convert_register_name(line_parsed.reg1),
                        imm=int(line_parsed.imm, base=0),
                    )
                )
            elif issubclass(instruction_class, instruction_types.BTypeInstruction):
                # B-Types can use labels or numerical immediates, so convert that first
                imm_val = self._convert_label_or_imm(
                    line_parsed,
                    self.labels,
                    address_count,
                    line_number=line_number,
                    line=line,
                )

                instructions.append(
                    instruction_class(
                        rs1=self._convert_register_name(line_parsed.reg1),
                        rs2=self._convert_register_name(line_parsed.reg2),
                        imm=imm_val,
                    )
                )
            elif issubclass(instruction_class, instruction_types.UTypeInstruction):
                instructions.append(
                    instruction_class(
                        rd=self._convert_register_name(line_parsed.rd),
                        imm=int(line_parsed.imm, base=0),
                    )
                )
            elif issubclass(instruction_class, instruction_types.JTypeInstruction):
                # J-Types can use labels or numerical immediates, so convert that first
                imm_val = self._convert_label_or_imm(
                    line_parsed,
                    self.labels,
                    address_count,
                    line_number=line_number,
                    line=line,
                )

                instructions.append(
                    instruction_class(
                        rd=self._convert_register_name(line_parsed.rd),
                        imm=imm_val,
                    )
                )
            elif issubclass(instruction_class, instruction_types.CSRTypeInstruction):
                instructions.append(
                    instruction_class(
                        rd=self._convert_register_name(line_parsed.rd),
                        csr=int(line_parsed.csr, base=0),
                        rs1=self._convert_register_name(line_parsed.rs1),
                    )
                )
            elif issubclass(instruction_class, instruction_types.CSRITypeInstruction):
                # TODO: Add parser element for this type
                instructions.append(
                    instruction_class(
                        rd=self._convert_register_name(line_parsed.rd),
                        csr=int(line_parsed.csr, base=0),
                        uimm=int(line_parsed.uimm, base=0),
                    )
                )
            elif issubclass(instruction_class, instruction_types.FenceTypeInstruction):
                # TODO: Change me, if Fence gets implemented
                instructions.append(FENCE())
            address_count += instruction_map[line_parsed.mnemonic.lower()].length

        self.state.instruction_memory.write_instructions(instructions)

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
            return self._reg_mapping[parsed_register[0]]
        else:
            return int(parsed_register[0][1])


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


@dataclass
class ParserDirectiveException(ParserException):
    """An exception that can be raised when an illegal directive is used."""

    def __repr__(self) -> str:
        return f"Illegal directive in line {self.line_number}: {self.line}"


@dataclass
class ParserDataSyntaxException(ParserException):
    """An exception that can be raised when syntax inside a data segment is incorrect."""

    def __repr__(self) -> str:
        return f"Syntax error in .data segment in line {self.line_number}: {self.line}"


@dataclass
class ParserDataDuplicateException(ParserException):
    """An exception that can be raised when a duplicate variable name is used inside a data segment."""

    name: str

    def __repr__(self) -> str:
        return f"Redefinition of variable {self.name} in line {self.line_number}: {self.line}"


@dataclass
class ParserVariableException(ParserException):
    """An exception that can be raised when a variable is used but not defined."""

    name: str

    def __repr__(self) -> str:
        return f"Variable {self.name} is not defined in line {self.line_number}: {self.line}"
