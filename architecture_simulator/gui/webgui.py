from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import archsim_js
from architecture_simulator.isa.parser import ParserException
from architecture_simulator.simulation.simulation import Simulation
from architecture_simulator.uarch.pipeline_registers import (
    PipelineRegister,
    InstructionFetchPipelineRegister,
    InstructionDecodePipelineRegister,
    ExecutePipelineRegister,
    MemoryAccessPipelineRegister,
    RegisterWritebackPipelineRegister,
)
from architecture_simulator.uarch.pipeline import InstructionExecutionException

simulation: Optional[Simulation] = None


@dataclass
class StateNotInitializedError(RuntimeError):
    def __repr__(self):
        return "state has not been initialized."


def sim_init():
    global simulation
    simulation = Simulation()
    update_ui()
    return simulation


def step_sim(instr: str):
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    # parse the instr json string into a python dict
    if simulation.state.instruction_memory.instructions == {}:
        try:
            simulation.state.instruction_memory.append_instructions(instr)
        except ParserException as Parser_Exception:
            archsim_js.set_output(Parser_Exception.__repr__())

    # step the simulation
    try:
        simulation_ended_flag = simulation.step_simulation()
        update_ui()
    except InstructionExecutionException as e:
        archsim_js.highlight_cmd_table(int(e.address / 4))
        simulation_ended_flag = False

    return (simulation.state.performance_metrics.__repr__(), simulation_ended_flag)


def resume_timer():
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    simulation.state.performance_metrics.resume_timer()


def stop_timer():
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    simulation.state.performance_metrics.stop_timer()


def get_performance_metrics():
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    return simulation.state.performance_metrics.__repr__()


# runs the simulation, takes a string as input and returns the whole simulation
# def run_sim(instr: str):
#     global simulation
#     if simulation is None:
#         raise StateNotInitializedError()

#     # reset the instruction list
#     simulation = Simulation()

#     simulation.state.instruction_memory.append_instructions(instr)
#     # run the simulation
#     simulation.run_simulation()

#     update_ui()

#     return simulation


# resets the entire simulation
def reset_sim(pipeline_mode):
    global simulation
    if simulation is None:
        raise StateNotInitializedError()
    simulation = Simulation(mode=pipeline_mode)
    update_ui()
    return simulation


def parse_input(instr: str):
    global simulation
    if simulation is None:
        raise StateNotInitializedError()
    simulation.state.instruction_memory.instructions = {}
    try:
        simulation.state.instruction_memory.append_instructions(instr)
        archsim_js.remove_all_highlights()
    except ParserException as Parser_Exception:
        archsim_js.remove_all_highlights()
        archsim_js.set_output(Parser_Exception.__repr__())
        archsim_js.highlight(
            Parser_Exception.line_number, str=Parser_Exception.__repr__()
        )
    update_ui()


def update_ui():
    update_tables()
    # update_performance_metrics()


def update_tables():
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    # appends all the registers one at a time
    archsim_js.clear_register_table()
    representations = simulation.state.register_file.reg_repr()
    for reg_i, reg_val in sorted(
        representations.items(),
        key=lambda item: item[0],
    ):
        reg_abi = simulation.state.register_file.get_abi_names(reg_i)
        archsim_js.update_register_table(reg_i, reg_val, reg_abi)  # int(reg_val)

    # appends all the memory one at a time
    archsim_js.clear_memory_table()
    representations = simulation.state.memory.memory_wordwise_repr()
    for address, address_value in sorted(
        representations.items(),
        key=lambda item: item[0],
    ):
        archsim_js.update_memory_table(hex(address), address_value)

    # appends all the instructions one at a time
    stage_mapping = {
        PipelineRegister: "Single",
        InstructionFetchPipelineRegister: "IF",
        InstructionDecodePipelineRegister: "ID",
        ExecutePipelineRegister: "EX",
        MemoryAccessPipelineRegister: "MA",
        RegisterWritebackPipelineRegister: "WB",
    }
    pipeline_stages_addresses = dict()
    for pipeline_register in simulation.pipeline.pipeline_registers:
        if pipeline_register.address_of_instruction is not None:
            pipeline_stages_addresses[
                pipeline_register.address_of_instruction
            ] = pipeline_register

    archsim_js.clear_instruction_table()
    for address, cmd in sorted(
        simulation.state.instruction_memory.instructions.items(),
        key=lambda item: item[0],
    ):
        if address in pipeline_stages_addresses.keys():
            archsim_js.update_instruction_table(
                hex(address),
                cmd.__repr__(),
                stage_mapping[pipeline_stages_addresses[address].__class__],
            )
        else:
            archsim_js.update_instruction_table(hex(address), cmd.__repr__(), "")

    # Update IF Stage
    IF_pipeline_register = simulation.pipeline.pipeline_registers[0]
    if isinstance(IF_pipeline_register, InstructionFetchPipelineRegister):
        archsim_js.update_IF_Stage(
            instruction=IF_pipeline_register.instruction,
            address_of_instruction=IF_pipeline_register.instruction,
        )

    # Update ID Stage
    try:
        ID_pipeline_register = simulation.pipeline.pipeline_registers[1]
        if isinstance(ID_pipeline_register, InstructionDecodePipelineRegister):
            control_unit_signals = [
                ID_pipeline_register.control_unit_signals.alu_src_1,
                ID_pipeline_register.control_unit_signals.alu_src_2,
                ID_pipeline_register.control_unit_signals.wb_src,
                ID_pipeline_register.control_unit_signals.reg_write,
                ID_pipeline_register.control_unit_signals.mem_read,
                ID_pipeline_register.control_unit_signals.mem_write,
                ID_pipeline_register.control_unit_signals.branch,
                ID_pipeline_register.control_unit_signals.jump,
                ID_pipeline_register.control_unit_signals.alu_op,
                ID_pipeline_register.control_unit_signals.alu_to_pc,
            ]
            archsim_js.update_ID_Stage(
                register_read_addr_1=ID_pipeline_register.register_read_addr_1,
                register_read_addr_2=ID_pipeline_register.register_read_addr_2,
                register_read_data_1=ID_pipeline_register.register_read_data_1,
                register_read_data_2=ID_pipeline_register.register_read_data_2,
                imm=ID_pipeline_register.imm,
                control_unit_signals=control_unit_signals,
            )
    except:
        ...

    # Update EX Stage
    try:
        EX_pipeline_register = simulation.pipeline.pipeline_registers[2]
        if isinstance(EX_pipeline_register, ExecutePipelineRegister):
            control_unit_signals = [
                EX_pipeline_register.control_unit_signals.alu_src_1,
                EX_pipeline_register.control_unit_signals.alu_src_2,
                EX_pipeline_register.control_unit_signals.wb_src,
                EX_pipeline_register.control_unit_signals.reg_write,
                EX_pipeline_register.control_unit_signals.mem_read,
                EX_pipeline_register.control_unit_signals.mem_write,
                EX_pipeline_register.control_unit_signals.branch,
                EX_pipeline_register.control_unit_signals.jump,
                EX_pipeline_register.control_unit_signals.alu_op,
                EX_pipeline_register.control_unit_signals.alu_to_pc,
            ]
            archsim_js.update_EX_Stage(
                alu_in_1=EX_pipeline_register.alu_in_1,
                alu_in_2=EX_pipeline_register.alu_in_2,
                register_read_data_2=EX_pipeline_register.register_read_data_2,
                imm=EX_pipeline_register.imm,
                result=EX_pipeline_register.result,
                comparison=EX_pipeline_register.comparison,
                pc_plus_imm=EX_pipeline_register.pc_plus_imm,
                control_unit_signals=control_unit_signals,
            )
    except:
        ...

    # Update MA Stage
    try:
        MA_pipeline_register = simulation.pipeline.pipeline_registers[3]
        if isinstance(MA_pipeline_register, MemoryAccessPipelineRegister):
            control_unit_signals = [
                MA_pipeline_register.control_unit_signals.alu_src_1,
                MA_pipeline_register.control_unit_signals.alu_src_2,
                MA_pipeline_register.control_unit_signals.wb_src,
                MA_pipeline_register.control_unit_signals.reg_write,
                MA_pipeline_register.control_unit_signals.mem_read,
                MA_pipeline_register.control_unit_signals.mem_write,
                MA_pipeline_register.control_unit_signals.branch,
                MA_pipeline_register.control_unit_signals.jump,
                MA_pipeline_register.control_unit_signals.alu_op,
                MA_pipeline_register.control_unit_signals.alu_to_pc,
            ]
            archsim_js.update_MA_Stage(
                memory_address=MA_pipeline_register.memory_address,
                result=MA_pipeline_register.result,
                memory_write_data=MA_pipeline_register.memory_write_data,
                memory_read_data=MA_pipeline_register.memory_read_data,
                comparison=MA_pipeline_register.comparison,
                comparison_or_jump=MA_pipeline_register.comparison_or_jump,
                pc_plus_imm=MA_pipeline_register.pc_plus_imm,
                control_unit_signals=control_unit_signals,
            )
    except:
        ...

    # Update WB Stage
    try:
        WB_pipeline_register = simulation.pipeline.pipeline_registers[4]
        if isinstance(WB_pipeline_register, RegisterWritebackPipelineRegister):
            control_unit_signals = [
                WB_pipeline_register.control_unit_signals.alu_src_1,
                WB_pipeline_register.control_unit_signals.alu_src_2,
                WB_pipeline_register.control_unit_signals.wb_src,
                WB_pipeline_register.control_unit_signals.reg_write,
                WB_pipeline_register.control_unit_signals.mem_read,
                WB_pipeline_register.control_unit_signals.mem_write,
                WB_pipeline_register.control_unit_signals.branch,
                WB_pipeline_register.control_unit_signals.jump,
                WB_pipeline_register.control_unit_signals.alu_op,
                WB_pipeline_register.control_unit_signals.alu_to_pc,
            ]
            archsim_js.update_WB_Stage(
                register_write_data=WB_pipeline_register.register_write_data,
                write_register=WB_pipeline_register.write_register,
                memory_read_data=WB_pipeline_register.memory_read_data,
                alu_result=WB_pipeline_register.alu_result,
                control_unit_signals=control_unit_signals,
            )
    except:
        ...


# #actual comment: output = performance metric repr but if parser produces error, overwrite output with error
# def update_output():
#     global simulation
#     if simulation is None:
#         raise RuntimeError("state has not been initialized.")

#     archsim_js.update_output(simulation.state.performance_metrics.__repr__())
