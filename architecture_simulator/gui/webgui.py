from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import archsim_js
from architecture_simulator.isa.parser_exceptions import ParserException
from architecture_simulator.simulation.riscv_simulation import RiscvSimulation
from architecture_simulator.simulation.toy_simulation import ToySimulation
from architecture_simulator.simulation.simulation import Simulation
from architecture_simulator.uarch.riscv.pipeline_registers import (
    PipelineRegister,
    InstructionFetchPipelineRegister,
    InstructionDecodePipelineRegister,
    ExecutePipelineRegister,
    MemoryAccessPipelineRegister,
    RegisterWritebackPipelineRegister,
)
from architecture_simulator.uarch.riscv.pipeline import InstructionExecutionException

simulation: Optional[Simulation] = None


@dataclass
class StateNotInitializedError(RuntimeError):
    """An error for when the architectural state (or rather the simulation) has not yet been initialized."""

    def __repr__(self):
        return "state has not been initialized."


def sim_init() -> RiscvSimulation:
    """Creates a new simulation object and updates the UI elements.

    Returns:
        RiscvSimulation: The new simulation.
    """
    global simulation
    simulation = RiscvSimulation()
    update_ui()
    return simulation


def step_sim(program: str) -> tuple[str, bool]:
    """Executes one step in the simulation. First loads the given program in case there are no instructions in the instruction memory yet. Also updates the UI elements.

    Args:
        program (str): text format assembly program.

    Raises:
        StateNotInitializedError: Throws an error if the simulation has not yet been initialized.

    Returns:
        tuple[str, bool]: tuple of (performance metrics string, whether the simulation has not ended yet)
    """
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    # parse the instr json string into a python dict
    if not simulation.has_instructions():
        try:
            simulation.load_program(program)
        except ParserException as Parser_Exception:
            archsim_js.set_output(Parser_Exception.__repr__())

    # step the simulation
    try:
        simulation_not_ended_flag = simulation.step()
        update_ui()
    except InstructionExecutionException as e:
        archsim_js.highlight_cmd_table(e.address)
        archsim_js.set_output(e.__repr__())
        simulation_not_ended_flag = False

    return (str(simulation.get_performance_metrics()), simulation_not_ended_flag)


def resume_timer():
    """Resumes the performance metrics timer.

    Raises:
        StateNotInitializedError: Throws an error if the simulation has not yet been initialized.
    """
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    simulation.get_performance_metrics().resume_timer()


def stop_timer():
    """Stops/pauses the performance metrics timer.

    Raises:
        StateNotInitializedError: Throws an error if the simulation has not yet been initialized.
    """
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    simulation.get_performance_metrics().stop_timer()


def get_performance_metrics_str() -> str:
    """Get a string representation of the performance metrics.

    Raises:
        StateNotInitializedError: Throws an error if the simulation has not yet been initialized.

    Returns:
        str: String representation of the performance metrics.
    """
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    return str(simulation.get_performance_metrics())


def reset_sim() -> Simulation:
    """Creates a new simulation for the selected ISA, sets it as the global 'simulation' and updates the UI elements.

    Raises:
        StateNotInitializedError: Throws an error if the simulation has not yet been initialized.

    Returns:
        Simulation: The new simulation.
    """
    # FIXME: Why do we check if the simulation is None? Isn't this pretty much the same as sim_init()?
    global simulation
    if simulation is None:
        raise StateNotInitializedError()
    isa = archsim_js.get_selected_isa()
    if isa == "riscv":
        pipeline_mode = archsim_js.get_pipeline_mode()
        hazard_detection = archsim_js.get_hazard_detection()
        simulation = RiscvSimulation(
            mode=pipeline_mode, detect_data_hazards=hazard_detection
        )
    elif isa == "toy":
        simulation = ToySimulation()
    update_ui()
    return simulation


def parse_input(instr: str):
    """Parse the input and load it into the simulation and updates the UI elements.

    Args:
        instr (str): text format assembly program to be loaded.

    Raises:
        StateNotInitializedError: Throws an error if the simulation has not yet been initialized.
    """
    global simulation
    if simulation is None:
        raise StateNotInitializedError()
    # reset the whole simulation because there might be things like a data section that also modify the data memory
    # so resetting the instruction memory is not enough
    simulation = reset_sim()
    archsim_js.remove_all_highlights()
    try:
        simulation.load_program(instr)
    except ParserException as Parser_Exception:
        archsim_js.set_output(Parser_Exception.__repr__())
        archsim_js.highlight(
            Parser_Exception.line_number, str=Parser_Exception.__repr__()
        )
    update_ui()


# FIXME: update_tables() does not only update tables. Put this stuff into their own functions and then make update_ui() call them all individually.
def update_ui():
    """Updates all UI elements based on the current simulation and architectural state."""
    update_tables()


# FIXME: this function is way too long. See the suggested fixes above and below.
def update_tables():
    """Updates the tables (instructions, registers and memory). Also updates the visualization.

    Raises:
        StateNotInitializedError: Throws an error if the simulation has not yet been initialized.
    """
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    # appends all the registers one at a time
    archsim_js.clear_register_table()
    archsim_js.clear_memory_table()
    archsim_js.clear_instruction_table()
    if isinstance(simulation, ToySimulation):
        # register table
        accu_representation = simulation.state.get_accu_representation()
        archsim_js.update_register_table(0, accu_representation, "ACCU")

        # instruction table
        for address, cmd in sorted(
            simulation.state.instruction_memory.instructions.items(),
            key=lambda item: item[0],
        ):
            stage = (
                "Single" if address == simulation.state.previous_program_counter else ""
            )
            archsim_js.update_instruction_table(hex(address), cmd.__repr__(), stage)

        # memory table
        representations = simulation.state.data_memory.memory_repr()
        for address, address_value in sorted(
            representations.items(),
            key=lambda item: item[0],
        ):
            archsim_js.update_memory_table(hex(address), address_value)

    elif isinstance(simulation, RiscvSimulation):
        # register table
        representations = simulation.state.register_file.reg_repr()
        for reg_i, reg_val in sorted(
            representations.items(),
            key=lambda item: item[0],
        ):
            reg_abi = simulation.state.register_file.get_abi_names(reg_i)
            archsim_js.update_register_table(reg_i, reg_val, reg_abi)  # int(reg_val)

        # memory table

        representations = simulation.state.memory.memory_wordwise_repr()
        for address, address_value in sorted(
            representations.items(),
            key=lambda item: item[0],
        ):
            archsim_js.update_memory_table(hex(address), address_value)

        # instruction table
        # find out which instructions are in which stages
        pipeline_stages_addresses = dict()
        for pipeline_register in simulation.state.pipeline.pipeline_registers:
            if pipeline_register.address_of_instruction is not None:
                pipeline_stages_addresses[
                    pipeline_register.address_of_instruction
                ] = pipeline_register
        
        # display names for the stages
        stage_mapping = {
            PipelineRegister: "Single",
            InstructionFetchPipelineRegister: "IF",
            InstructionDecodePipelineRegister: "ID",
            ExecutePipelineRegister: "EX",
            MemoryAccessPipelineRegister: "MEM",
            RegisterWritebackPipelineRegister: "WB",
        }
        # inserts all instructions into the instruction table
        for address, cmd in sorted(
            simulation.state.instruction_memory.instructions.items(),
            key=lambda item: item[0],
        ):
            if address in pipeline_stages_addresses.keys():
                # if the instruction is in one of the stages
                archsim_js.update_instruction_table(
                    hex(address),
                    cmd.__repr__(),
                    stage_mapping[pipeline_stages_addresses[address].__class__],
                )
            else:
                # if the instruction is not in one of the stages
                archsim_js.update_instruction_table(hex(address), cmd.__repr__(), "")

        # visualization
        # Invoke all the js functions which update the visuals

        # FIXME: This is a lot of code for handing the variables of a python object over to js (I think ?).
        # If that is all this does, you could simply replace everything by `vars(obj)` which returns a dict of all variables ._.

        # Update IF Stage
        try:
            IF_pipeline_register = simulation.state.pipeline.pipeline_registers[0]
            if isinstance(IF_pipeline_register, InstructionFetchPipelineRegister):
                archsim_js.update_IF_Stage(
                    IF_pipeline_register.instruction.__repr__(),
                    IF_pipeline_register.address_of_instruction,
                    IF_pipeline_register.pc_plus_instruction_length,
                )
        except:
            ...

        # Update ID Stage
        try:  # FIXME: Why is this a try statement without an except block?
            ID_pipeline_register = simulation.state.pipeline.pipeline_registers[1]
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
                    ID_pipeline_register.register_read_addr_1,
                    ID_pipeline_register.register_read_addr_2,
                    ID_pipeline_register.register_read_data_1,
                    ID_pipeline_register.register_read_data_2,
                    ID_pipeline_register.imm,
                    control_unit_signals,
                )
        except:
            ...

        # Update EX Stage
        try:
            EX_pipeline_register = simulation.state.pipeline.pipeline_registers[2]
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
                    EX_pipeline_register.alu_in_1,
                    EX_pipeline_register.alu_in_2,
                    EX_pipeline_register.register_read_data_2,
                    EX_pipeline_register.imm,
                    EX_pipeline_register.result,
                    EX_pipeline_register.comparison,
                    EX_pipeline_register.pc_plus_imm,
                    control_unit_signals,
                )
        except:
            ...

        # Update MEM Stage
        try:
            MEM_pipeline_register = simulation.state.pipeline.pipeline_registers[3]
            if isinstance(MEM_pipeline_register, MemoryAccessPipelineRegister):
                control_unit_signals = [
                    MEM_pipeline_register.control_unit_signals.alu_src_1,
                    MEM_pipeline_register.control_unit_signals.alu_src_2,
                    MEM_pipeline_register.control_unit_signals.wb_src,
                    MEM_pipeline_register.control_unit_signals.reg_write,
                    MEM_pipeline_register.control_unit_signals.mem_read,
                    MEM_pipeline_register.control_unit_signals.mem_write,
                    MEM_pipeline_register.control_unit_signals.branch,
                    MEM_pipeline_register.control_unit_signals.jump,
                    MEM_pipeline_register.control_unit_signals.alu_op,
                    MEM_pipeline_register.control_unit_signals.alu_to_pc,
                ]
                archsim_js.update_MEM_Stage(
                    MEM_pipeline_register.memory_address,
                    MEM_pipeline_register.result,
                    MEM_pipeline_register.memory_write_data,
                    MEM_pipeline_register.memory_read_data,
                    MEM_pipeline_register.comparison,
                    MEM_pipeline_register.comparison_or_jump,
                    MEM_pipeline_register.pc_plus_imm,
                    control_unit_signals,
                )
        except:
            ...

        # Update WB Stage
        try:
            WB_pipeline_register = simulation.state.pipeline.pipeline_registers[4]
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
                    WB_pipeline_register.register_write_data,
                    WB_pipeline_register.write_register,
                    WB_pipeline_register.memory_read_data,
                    WB_pipeline_register.alu_result,
                    control_unit_signals,
                )
        except:
            ...
