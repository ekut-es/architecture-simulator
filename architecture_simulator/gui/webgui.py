from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import archsim_js
import pyodide.ffi  # type: ignore
from architecture_simulator.settings.settings import Settings
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
from architecture_simulator.isa.toy.toy_instructions import ToyInstruction
from architecture_simulator.gui.toy_svg_directives import get_toy_svg_directives

simulation: Optional[Simulation] = None
first_refresh: bool = True


@dataclass
class StateNotInitializedError(RuntimeError):
    """An error for when the architectural state (or rather the simulation) has not yet been initialized."""

    def __repr__(self):
        return "state has not been initialized."


def load_settings() -> str:
    """Loads the settings JSON using Python, to avoid local JS import errors.

    Returns:
        str: The settings JSON.
    """
    settings_string = Settings().get_JSON()
    return settings_string


def sim_init() -> RiscvSimulation:
    """Creates a new simulation object and updates the UI elements.

    Returns:
        RiscvSimulation: The new simulation.
    """
    global simulation
    global first_refresh
    first_refresh = True
    simulation = RiscvSimulation()
    update_ui()
    return simulation


def step_sim(program: str, is_run_simulation: bool) -> tuple[str, bool, bool]:
    """Executes one step in the simulation. First loads the given program in case there are no instructions in the instruction memory yet. Also updates the UI elements.

    Args:
        program (str): text format assembly program.
        is_run_simulation (bool): whether the simulation is currently in play mode

    Raises:
        StateNotInitializedError: Throws an error if the simulation has not yet been initialized.

    Returns:
        tuple[str, bool, bool]: tuple of (performance metrics string, whether the simulation has not ended yet, whether there was an exception)
    """
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    # Variable to tell js whether there was an exception
    exception_flag = False

    # parse the instr json string into a python dict
    if not simulation.has_instructions():
        try:
            simulation.load_program(program)
        except ParserException as Parser_Exception:
            archsim_js.set_output(Parser_Exception.__repr__())
            exception_flag = True

    # step the simulation
    try:
        simulation_not_ended_flag = simulation.step()
        if not is_run_simulation:
            update_ui()
    except InstructionExecutionException as e:
        archsim_js.highlight_cmd_table(e.address)
        archsim_js.set_output(e.__repr__())
        simulation_not_ended_flag = False
        exception_flag = True

    return (
        str(simulation.get_performance_metrics()),
        simulation_not_ended_flag,
        exception_flag,
    )


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
    global first_refresh
    if simulation is None:
        raise StateNotInitializedError()
    # reset the whole simulation because there might be things like a data section that also modify the data memory
    # so resetting the instruction memory is not enough
    simulation = reset_sim()
    selected_isa = archsim_js.get_selected_isa()
    if selected_isa == "riscv":
        archsim_js.remove_all_highlights()
    try:
        simulation.load_program(instr)
        if not first_refresh:
            archsim_js.set_output(Settings().get()["default_no_error_output"])
        first_refresh = False
    except ParserException as Parser_Exception:
        archsim_js.set_output(Parser_Exception.__repr__())
        if selected_isa == "riscv":
            archsim_js.highlight(
                Parser_Exception.line_number, str=Parser_Exception.__repr__()
            )
    update_ui()


def update_ui():
    """Updates all UI elements based on the current simulation and architectural state."""
    selected_isa = archsim_js.get_selected_isa()
    if selected_isa == "riscv":
        update_tables()
        if archsim_js.get_riscv_visualization_loaded():
            update_IF_Stage()
            update_ID_Stage()
            update_EX_Stage()
            update_MEM_Stage()
            update_WB_Stage()
            update_visualization()
    elif selected_isa == "toy":
        update_toy_tables()
        if archsim_js.get_toy_visualization_loaded():
            update_toy_visualization()


def update_toy_visualization():
    global simulation
    if simulation is None:
        raise StateNotInitializedError()
    if isinstance(simulation, ToySimulation):
        archsim_js.update_toy_visualization(get_toy_svg_update_values(simulation))


def update_toy_tables():
    """Updates the accu and the memory table for toy"""
    if isinstance(simulation, ToySimulation):
        # accu
        accu_representation = simulation.state.get_accu_representation()
        archsim_js.toyUpdateAccu(accu_representation)

        # memory table
        archsim_js.toyClearMemoryTable()
        representations = simulation.state.memory.memory_repr()
        for address, value_representations in sorted(representations.items()):
            if address <= simulation.state.max_pc:
                instruction_representation = str(
                    ToyInstruction.from_integer(int(value_representations[1]))
                )
            else:
                instruction_representation = "-"
            is_current_instruction = (
                simulation.state.address_of_current_instruction is not None
                and address == simulation.state.address_of_current_instruction
            )
            archsim_js.toyUpdateMemoryTable(
                "0x{:03X}".format(address),
                value_representations,
                instruction_representation,
                is_current_instruction,
            )


def update_tables():
    """Updates the tables (instructions, registers and memory).

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

    if isinstance(simulation, RiscvSimulation):
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


def update_IF_Stage():
    """
    Updates the IF Stage of the visualization and all elements withing this stage.
    To do this, the archsim.js function update_IF_Stage is called with all relevant arguments.

    Raises:
        StateNotInitializedError: Throws an error if the simulation has not yet been initialized.
    """
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    if not isinstance(simulation, RiscvSimulation):
        return

    try:
        IF_pipeline_register = simulation.state.pipeline.pipeline_registers[0]
        # parameters = vars(IF_pipeline_register)
        if isinstance(IF_pipeline_register, InstructionFetchPipelineRegister):
            parameters = {
                "mnemonic": IF_pipeline_register.instruction.mnemonic,
                "instruction": IF_pipeline_register.instruction.__repr__(),
                "address_of_instruction": IF_pipeline_register.address_of_instruction,
                "PC": simulation.state.program_counter,
                "pc_plus_instruction_length": IF_pipeline_register.pc_plus_instruction_length,
                "i-length": IF_pipeline_register.instruction.length,
            }
            parameters_js = pyodide.ffi.to_js(parameters)
            archsim_js.update_IF_Stage(parameters_js)
        # this case only applies if the Pipeline Register is flushed
        elif isinstance(IF_pipeline_register, PipelineRegister):
            parameters_2 = vars(IF_pipeline_register)
            parameters = dict()
            parameters["PC"] = simulation.state.program_counter
            parameters["mnemonic"] = parameters_2["instruction"].mnemonic
            parameters_js = pyodide.ffi.to_js(parameters)
            archsim_js.update_IF_Stage(parameters_js)
    except:
        ...


def update_ID_Stage():
    """
    Updates the ID Stage of the visualization and all elements withing this stage.
    To do this, the archsim.js function update_ID_Stage is called with all relevant arguments.

    Raises:
        StateNotInitializedError: Throws an error if the simulation has not yet been initialized.
    """
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    if not isinstance(simulation, RiscvSimulation):
        return

    try:
        ID_pipeline_register = simulation.state.pipeline.pipeline_registers[1]
        if isinstance(ID_pipeline_register, InstructionDecodePipelineRegister):
            control_unit_signals = vars(ID_pipeline_register.control_unit_signals)
            parameters = vars(ID_pipeline_register)
            parameters["mnemonic"] = ID_pipeline_register.instruction.mnemonic
            parameters_js = pyodide.ffi.to_js(parameters)
            control_unit_signals_js = pyodide.ffi.to_js(control_unit_signals)
            archsim_js.update_ID_Stage(
                parameters_js,
                control_unit_signals_js,
            )
        # this case only applies if the Pipeline Register is flushed or reset
        elif isinstance(ID_pipeline_register, PipelineRegister):
            parameters = vars(ID_pipeline_register)
            control_unit_signals = dict()
            parameters["mnemonic"] = ID_pipeline_register.instruction.mnemonic
            parameters_js = pyodide.ffi.to_js(parameters)
            control_unit_signals_js = pyodide.ffi.to_js(control_unit_signals)
            archsim_js.update_ID_Stage(
                parameters_js,
                control_unit_signals_js,
            )
    except:
        ...


def update_EX_Stage():
    """
    Updates the EX Stage of the visualization and all elements withing this stage.
    To do this, the archsim.js function update_EX_Stage is called with all relevant arguments.

    Raises:
    StateNotInitializedError: Throws an error if the simulation has not yet been initialized.
    """
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    if not isinstance(simulation, RiscvSimulation):
        return

    try:
        EX_pipeline_register = simulation.state.pipeline.pipeline_registers[2]
        if isinstance(EX_pipeline_register, ExecutePipelineRegister):
            control_unit_signals = vars(EX_pipeline_register.control_unit_signals)
            parameters = vars(EX_pipeline_register)
            parameters["mnemonic"] = EX_pipeline_register.instruction.mnemonic
            parameters_js = pyodide.ffi.to_js(parameters)
            control_unit_signals_js = pyodide.ffi.to_js(control_unit_signals)
            archsim_js.update_EX_Stage(parameters_js, control_unit_signals_js)
        # this case only applies if the Pipeline Register is flushed or reset
        elif isinstance(EX_pipeline_register, PipelineRegister):
            parameters = vars(EX_pipeline_register)
            control_unit_signals = dict()
            parameters["mnemonic"] = EX_pipeline_register.instruction.mnemonic
            parameters_js = pyodide.ffi.to_js(parameters)
            control_unit_signals_js = pyodide.ffi.to_js(control_unit_signals)
            archsim_js.update_EX_Stage(parameters_js, control_unit_signals_js)
    except:
        ...


def update_MEM_Stage():
    """
    Updates the MEM Stage of the visualization and all elements withing this stage.
    To do this, the archsim.js function update_MEM_Stage is called with all relevant arguments.

    Raises:
    StateNotInitializedError: Throws an error if the simulation has not yet been initialized.
    """
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    if not isinstance(simulation, RiscvSimulation):
        return

    try:
        MEM_pipeline_register = simulation.state.pipeline.pipeline_registers[3]
        if isinstance(MEM_pipeline_register, MemoryAccessPipelineRegister):
            control_unit_signals = vars(MEM_pipeline_register.control_unit_signals)
            parameters = vars(MEM_pipeline_register)
            parameters["mnemonic"] = MEM_pipeline_register.instruction.mnemonic
            parameters_js = pyodide.ffi.to_js(parameters)
            control_unit_signals_js = pyodide.ffi.to_js(control_unit_signals)
            archsim_js.update_MEM_Stage(
                parameters_js,
                control_unit_signals_js,
            )
        # this case only applies if the Pipeline Register is flushed or reset
        elif isinstance(MEM_pipeline_register, PipelineRegister):
            parameters = vars(MEM_pipeline_register)
            control_unit_signals = dict()
            parameters["mnemonic"] = MEM_pipeline_register.instruction.mnemonic
            parameters_js = pyodide.ffi.to_js(parameters)
            control_unit_signals_js = pyodide.ffi.to_js(control_unit_signals)
            archsim_js.update_MEM_Stage(
                parameters_js,
                control_unit_signals_js,
            )
    except:
        ...


def update_WB_Stage():
    """Update WB Stage:
    Updates the WB Stage of the visualization and all elements withing this stage.
    To do this, the archsim.js function update_WB_Stage is called with all relevant arguments.

    Raises:
    StateNotInitializedError: Throws an error if the simulation has not yet been initialized.
    """
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    if not isinstance(simulation, RiscvSimulation):
        return

    try:
        WB_pipeline_register = simulation.state.pipeline.pipeline_registers[4]
        if isinstance(WB_pipeline_register, RegisterWritebackPipelineRegister):
            control_unit_signals = vars(WB_pipeline_register.control_unit_signals)
            parameters = vars(WB_pipeline_register)
            parameters["mnemonic"] = WB_pipeline_register.instruction.mnemonic
            parameters_js = pyodide.ffi.to_js(parameters)
            control_unit_signals_js = pyodide.ffi.to_js(control_unit_signals)
            archsim_js.update_WB_Stage(
                parameters_js,
                control_unit_signals_js,
            )
        # this case only applies if the Pipeline Register is flushed or reset
        elif isinstance(WB_pipeline_register, PipelineRegister):
            parameters = vars(WB_pipeline_register)
            control_unit_signals = dict()
            parameters["mnemonic"] = WB_pipeline_register.instruction.mnemonic
            parameters_js = pyodide.ffi.to_js(parameters)
            control_unit_signals_js = pyodide.ffi.to_js(control_unit_signals)
            archsim_js.update_WB_Stage(
                parameters_js,
                control_unit_signals_js,
            )
    except:
        ...


def update_visualization():
    """
    Updates visualization elements that need information from more than one stage.

    Raises:
    StateNotInitializedError: Throws an error if the simulation has not yet been initialized.
    """
    global simulation
    if simulation is None:
        raise StateNotInitializedError()

    if not isinstance(simulation, RiscvSimulation):
        return

    if len(simulation.state.pipeline.pipeline_registers) > 1:
        IF_pipeline_register = simulation.state.pipeline.pipeline_registers[0]
        MEM_pipeline_register = simulation.state.pipeline.pipeline_registers[3]
        if isinstance(
            IF_pipeline_register, InstructionFetchPipelineRegister
        ) and isinstance(MEM_pipeline_register, MemoryAccessPipelineRegister):
            pc_plus_imm_or_pc_plus_instruction_length = (
                MEM_pipeline_register.pc_plus_imm
                if MEM_pipeline_register.comparison_or_jump
                else IF_pipeline_register.pc_plus_instruction_length
            )
        elif isinstance(IF_pipeline_register, PipelineRegister) and isinstance(
            MEM_pipeline_register, MemoryAccessPipelineRegister
        ):
            pc_plus_imm_or_pc_plus_instruction_length = (
                MEM_pipeline_register.pc_plus_imm
                if MEM_pipeline_register.comparison_or_jump
                else None
            )
        else:
            pc_plus_imm_or_pc_plus_instruction_length = None
        if pc_plus_imm_or_pc_plus_instruction_length is not None and isinstance(
            MEM_pipeline_register, MemoryAccessPipelineRegister
        ):
            pc_plus_imm_or_pc_plus_instruction_length_or_ALU_result = (
                MEM_pipeline_register.result
                if MEM_pipeline_register.control_unit_signals.alu_to_pc
                else pc_plus_imm_or_pc_plus_instruction_length
            )
        elif isinstance(MEM_pipeline_register, MemoryAccessPipelineRegister):
            pc_plus_imm_or_pc_plus_instruction_length_or_ALU_result = (
                MEM_pipeline_register.result
                if MEM_pipeline_register.control_unit_signals.alu_to_pc
                else None
            )

        else:
            pc_plus_imm_or_pc_plus_instruction_length_or_ALU_result = None

        archsim_js.update_visualization(
            pc_plus_imm_or_pc_plus_instruction_length,
            pc_plus_imm_or_pc_plus_instruction_length_or_ALU_result,
        )


from architecture_simulator.isa.toy.toy_micro_program import MicroProgram
from architecture_simulator.isa.toy.toy_instructions import (
    ToyInstruction,
    ZRO,
    LDA,
    STO,
)


def get_toy_svg_update_values(sim: ToySimulation) -> list[tuple[str, str, str | bool]]:
    """Take a Toy simulation and return all information needed to update the svg.

    Args:
        sim (ToySimulation): ToySimulation object

    Returns:
        list[tuple[str, str, str | bool]]: each tuple is [svg-id, what update function to use, argument for update function (str | bool)].
            They can be one of ("<id>","highlight", <bool>), ("<id>", "write", "<content>"), ("<id>", "show", <bool>)
    """

    result = get_toy_svg_directives()
    loaded_instruction = sim.state.loaded_instruction
    visualisation_values = sim.state.visualisation_values
    control_unit_values: list[bool]

    if sim.next_cycle == 2:
        if loaded_instruction is not None:
            control_unit_values = MicroProgram.get_mp_values(type(loaded_instruction))
        else:
            control_unit_values = [False for i in range(12)]
    else:
        control_unit_values = MicroProgram.second_half_micro_program

    # Arrows:
    result["path-accu-pc-accu-is-zero"][1] = visualisation_values.jump
    result["path-accu-alu"][1] = visualisation_values.alu_out is not None and not type(
        loaded_instruction
    ) in [LDA, ZRO]
    result["path-alu-junction"][1] = visualisation_values.alu_out is not None
    result["path-junction-accu"][1] = control_unit_values[5]  # 5 -> SET[ACCU]
    result["path-junction-ram"][1] = control_unit_values[0]  # 0 -> WRITE[RAM]
    result["path-opcode-control-unit"][1] = True
    result["path-instaddress-junction"][1] = (
        visualisation_values.ram_out is not None
        or visualisation_values.jump
        or isinstance(loaded_instruction, STO)
    ) and not control_unit_values[4]
    result["path-junction-pc"][1] = visualisation_values.jump
    result["path-junction-multiplexer"][1] = (
        visualisation_values.ram_out is not None or isinstance(loaded_instruction, STO)
    ) and not control_unit_values[
        4
    ]  # 4 -> SET[IR]
    result["path-pc-multiplexer"][1] = control_unit_values[4]  # 4 -> SET[IR]
    result["path-multiplexer-ram"][
        1
    ] = visualisation_values.ram_out is not None or isinstance(loaded_instruction, STO)
    result["path-ram-junction"][1] = visualisation_values.ram_out is not None
    result["path-junction-alu"][1] = (
        visualisation_values.ram_out is not None
        and visualisation_values.alu_out is not None
    )
    result["path-junction-ir"][1] = control_unit_values[4]  # 4 -> SET[IR]

    # Text:
    if loaded_instruction is not None:
        result["text-mnemonic"][1] = loaded_instruction.mnemonic
        result["text-opcode"][1] = str(loaded_instruction.op_code_value())
        result["text-address"][1] = str(loaded_instruction.address_section_value())
    result["text-program-counter"][1] = str(sim.state.program_counter)
    alu_out = visualisation_values.alu_out
    ram_out = visualisation_values.ram_out
    result["text-alu-out"][1] = str(alu_out) if alu_out is not None else ""
    result["group-alu-out"][1] = alu_out is not None
    result["text-ram-out"][1] = str(ram_out) if ram_out is not None else ""
    result["text-accu"][1] = str(sim.state.accu)

    # Textblocks over Arrows:
    old_opcode = visualisation_values.op_code_old
    result["group-old-opcode-and-mnemonic"][1] = old_opcode is not None
    if old_opcode is not None:  # do not remove is not None
        result["text-old-opcode-and-mnemonic"][1] = (
            str(old_opcode)
            + " "
            + ToyInstruction.from_integer(old_opcode << 12).mnemonic
        )
    old_pc = visualisation_values.pc_old
    result["group-old-pc"][1] = old_pc is not None
    if old_pc is not None:  # do not remove is not None
        result["text-old-pc"][1] = str(old_pc)
    old_accu = visualisation_values.accu_old
    result["group-old-accu"][1] = old_accu is not None
    if old_accu is not None:  # do not remove is not None
        result["text-old-accu"][1] = str(old_accu)

    # Control Unit:
    control_unit_names = [
        "write-ram",
        "inc-pc",
        "set-pc",
        "addr-ir",
        "set-ir",
        "set-accu",
        "alucin",
        "alumode",
        "alu3",
        "alu2",
        "alu1",
        "alu0",
    ]
    for name, value in zip(control_unit_names, control_unit_values):
        result["path-control-unit-" + name][1] = value
        result["text-" + name][1] = value
    return [(key, value[0], value[1]) for key, value in result.items()]


def toy_get_next_cycle():
    """
    Returns:
        int: 1 or 2, depending on which cycle has to be executed next
    """
    if isinstance(simulation, ToySimulation):
        return simulation.next_cycle


def toy_single_step(program: str):
    if isinstance(simulation, ToySimulation):
        # Variable to tell js whether there was an exception
        exception_flag = False

        # parse the instr json string into a python dict
        if not simulation.has_instructions():
            try:
                simulation.load_program(program)
            except ParserException as Parser_Exception:
                archsim_js.set_output(Parser_Exception.__repr__())
                exception_flag = True

        # step the simulation
        if simulation.next_cycle == 1:
            simulation.first_cycle_step()
        else:
            simulation.second_cycle_step()
        simulation_not_ended_flag = not simulation.is_done()
        update_ui()

        return (
            str(simulation.get_performance_metrics()),
            simulation_not_ended_flag,
            exception_flag,
        )
