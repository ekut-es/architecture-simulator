from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass, field

from .control_unit_signals import ControlUnitSignals
from architecture_simulator.isa.instruction_types import EmptyInstruction

if TYPE_CHECKING:
    from architecture_simulator.isa.instruction_types import RiscvInstruction
    from .stages import FlushSignal


@dataclass
class PipelineRegister:
    """The PipelineRegister superclass!
    Every PipelineRegister needs to save the instruction that is currently in this part of the pipeline!
    """

    instruction: RiscvInstruction = field(default_factory=EmptyInstruction)
    address_of_instruction: Optional[int] = None
    flush_signal: Optional[FlushSignal] = None


@dataclass
class InstructionFetchPipelineRegister(PipelineRegister):
    branch_prediction: Optional[bool] = None
    pc_plus_instruction_length: Optional[int] = None


@dataclass
class InstructionDecodePipelineRegister(PipelineRegister):
    control_unit_signals: ControlUnitSignals = field(default_factory=ControlUnitSignals)
    register_read_addr_1: Optional[int] = None
    register_read_addr_2: Optional[int] = None
    register_read_data_1: Optional[int] = None
    register_read_data_2: Optional[int] = None
    imm: Optional[int] = None
    write_register: Optional[int] = None
    branch_prediction: Optional[bool] = None
    pc_plus_instruction_length: Optional[int] = None


@dataclass
class ExecutePipelineRegister(PipelineRegister):
    control_unit_signals: ControlUnitSignals = field(default_factory=ControlUnitSignals)
    alu_in_1: Optional[int] = None
    alu_in_2: Optional[int] = None
    # alu_in_2 is one of read_data_2 and imm
    register_read_data_2: Optional[int] = None
    imm: Optional[int] = None
    result: Optional[int] = None
    write_register: Optional[int] = None
    # control signals
    comparison: Optional[bool] = None
    pc_plus_imm: Optional[int] = None
    branch_prediction: Optional[bool] = None
    pc_plus_instruction_length: Optional[int] = None


@dataclass
class MemoryAccessPipelineRegister(PipelineRegister):
    control_unit_signals: ControlUnitSignals = field(default_factory=ControlUnitSignals)
    memory_address: Optional[int] = None
    result: Optional[int] = None
    memory_write_data: Optional[int] = None
    memory_read_data: Optional[int] = None
    write_register: Optional[int] = None
    # control signals
    comparison: Optional[bool] = None
    comparison_or_jump: Optional[bool] = None
    pc_plus_imm: Optional[int] = None
    pc_plus_instruction_length: Optional[int] = None
    imm: Optional[int] = None


@dataclass
class RegisterWritebackPipelineRegister(PipelineRegister):
    control_unit_signals: ControlUnitSignals = field(default_factory=ControlUnitSignals)
    register_write_data: Optional[int] = None
    write_register: Optional[int] = None
    memory_read_data: Optional[int] = None
    alu_result: Optional[int] = None
    pc_plus_instruction_length: Optional[int] = None
    imm: Optional[int] = None
