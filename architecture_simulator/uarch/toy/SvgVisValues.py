from typing import Optional
from fixedint import MutableUInt16
from dataclasses import dataclass


@dataclass
class SvgVisValues:
    accu_old: Optional[MutableUInt16] = None  # only for first cycle
    alu_out: Optional[MutableUInt16] = None  # only for first cycle
    jump: bool = False  # only for first cycle
    ram_out: Optional[MutableUInt16] = None  # for both cycles
    op_code_old: Optional[int] = None  # only for second cycle
    pc_old: Optional[MutableUInt16] = None  # only for second cycle
