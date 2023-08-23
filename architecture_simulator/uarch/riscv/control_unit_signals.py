from typing import Optional
from dataclasses import dataclass


#
# Classes for a 5 Stage Pipeline:
#
@dataclass
class ControlUnitSignals:
    """The signals of the control unit, which is located in the ID stage! These signals are used to decide
    which input gets used, but are mostly aesthetic and constructed for the webui! Only required for the pipeline.
    """

    alu_src_1: Optional[bool] = None
    alu_src_2: Optional[bool] = None
    wb_src: Optional[int] = None
    reg_write: Optional[bool] = None
    mem_read: Optional[bool] = None
    mem_write: Optional[bool] = None
    branch: Optional[bool] = None
    jump: Optional[bool] = None
    alu_op: Optional[int] = None
    alu_to_pc: Optional[bool] = None
