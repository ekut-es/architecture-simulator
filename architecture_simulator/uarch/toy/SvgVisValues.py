from typing import Optional
from fixedint import UInt16
from architecture_simulator.util.fixedint_12 import UInt12
from dataclasses import dataclass


@dataclass
class SvgVisValues:
    accu_old: Optional[UInt16] = None  # only for first cycle
    alu_out: Optional[UInt16] = None  # only for first cycle
    jump: bool = False  # only for first cycle
    ram_out: Optional[UInt16] = None  # for both cycles
    op_code_old: Optional[int] = None  # only for second cycle
    pc_old: Optional[UInt12] = None  # only for second cycle
