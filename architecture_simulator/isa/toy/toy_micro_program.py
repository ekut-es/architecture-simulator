from __future__ import annotations
from typing import Type
from architecture_simulator.isa.toy.toy_instructions import (
    ToyInstruction,
    STO,
    LDA,
    BRZ,
    ADD,
    SUB,
    OR,
    AND,
    XOR,
    NOT,
    INC,
    DEC,
    ZRO,
    NOP,
)


def int_to_bool_list(num: int) -> list[bool]:
    return [bool((num >> (11 - i)) & 1) for i in range(12)]


class MicroProgram:
    _signal_names: list[str] = [
        "write[ram]",
        "inc[pc]",
        "set[pc]",
        "addr=ir",
        "set[ir]",
        "set[accu]",
        "aluinc",
        "alumode",
        "alu3",
        "alu2",
        "alu1",
        "alu0",
    ]

    _instr_mp_mapping: dict[Type[ToyInstruction], int] = {
        STO: 0b100100011111,
        LDA: 0b000101011010,
        BRZ: 0b001100000000,
        ADD: 0b000101001001,
        SUB: 0b000101100110,
        OR: 0b000101011110,
        AND: 0b000101011011,
        XOR: 0b000101010110,
        NOT: 0b000001010000,
        INC: 0b000001100000,
        DEC: 0b000001001111,
        ZRO: 0b000001010011,
        NOP: 0b000000000000,
    }

    _instr_bool_list_mapping: dict[Type[ToyInstruction], list[bool]] = dict(
        [(key, int_to_bool_list(val)) for (key, val) in _instr_mp_mapping.items()]
    )

    second_half_micro_program = [bool(i) for i in [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]]

    @classmethod
    def get_mp_values(self, instr: Type[ToyInstruction]):
        """
        Returns all micro program values for the instruction.
        """
        return self._instr_bool_list_mapping[instr]

    @classmethod
    def get_mp_var_value(self, instr: Type[ToyInstruction], signal_name: str) -> bool:
        """
        Returns the value of a signal_variable of the micro program.
        """
        return self._instr_bool_list_mapping[instr][
            self._signal_names.index(signal_name)
        ]
