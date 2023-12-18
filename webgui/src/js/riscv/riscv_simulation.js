import {
    getRiscvDataHazardSettings,
    getRiscvInstructionTable,
    getRiscvMemoryTable,
    getRiscvOutputField,
    getRiscvRegisterTable,
} from "./riscv_components";
import { riscvDocumentation } from "./riscv_documentation";
import { getRadioSettingsRow, getRepresentationsSettingsRow } from "../util";
import { Simulation } from "../simulation";
import { setEditorReadOnly } from "../editor";
import riscvSvgPath from "/src/img/riscv_pipeline.svg";

export class RiscvSimulation extends Simulation {
    constructor(domNodes, getRiscvPythonSimulation, getLastPythonError) {
        super(domNodes, getLastPythonError);
        /**@type {Number} The selected representation mode for the registers. 0: bin, 1: udec, 2: hex, 3: sdec.*/
        this.regRepresentationMode = 1;
        /**@type {Number} The selected representation mode for the memory. 0: bin, 1: udec, 2: hex, 3: sdec.*/
        this.memRepresentationMode = 1;
        /**@type {?} The values of the memory from the last cycle.*/
        this.previousMemoryValues = [];
        /**@type {string} The mode of the pipeline (either "single_stage_pipeline" or "five_stage_pipeline") */
        this.pipelineMode = "single_stage_pipeline";
        /**@type {boolean} Whether to enable data hazard detection in the five stage pipeline*/
        this.dataHazardDetection = true;

        this.getRiscvPythonSimulation = getRiscvPythonSimulation;
        this.pythonSimulation = this.getNewPythonSimulation();

        this.previous_pc = 0;

        this.domNodes = {
            ...this.domNodes,
            outputField: getRiscvOutputField(),
            ...getRiscvRegisterTable(),
            ...getRiscvMemoryTable(),
            ...getRiscvInstructionTable(),
        };
        this.domNodes.textEditorSeparator.after(
            this.domNodes.instructionTableContainer,
            this.domNodes.registerTableContainer,
            this.domNodes.memoryTableContainer,
            this.domNodes.outputField
        );

        const registerRepresentation = getRepresentationsSettingsRow(
            "Registers",
            "register-representation",
            (mode) => {
                this.regRepresentationMode = Number(mode);
                this.updateUI();
            },
            String(this.regRepresentationMode)
        );
        const memoryRepresentation = getRepresentationsSettingsRow(
            "Memory",
            "memory-representation",
            (mode) => {
                this.memRepresentationMode = Number(mode);
                this.updateUI();
            },
            String(this.memRepresentationMode)
        );
        const pipelineModeSelector = getRadioSettingsRow(
            "Pipeline Mode",
            ["Single Stage", "Five Stage"],
            ["single_stage_pipeline", "five_stage_pipeline"],
            "pipeline-mode-selector",
            (mode) => {
                this.switchPipelineMode(mode);
            },
            this.pipelineMode
        );
        this.domNodes.customSettingsContainer.appendChild(
            registerRepresentation
        );
        this.domNodes.customSettingsContainer.appendChild(memoryRepresentation);
        this.domNodes.customSettingsContainer.appendChild(pipelineModeSelector);

        this.parseInput();
        if (this.pipelineMode === "five_stage_pipeline") {
            this.activateVisualization();
        } else {
            this.updateUI();
        }
    }

    getNewPythonSimulation() {
        return this.getRiscvPythonSimulation(
            this.pipelineMode,
            this.dataHazardDetection
        );
    }

    getPathToVisualization() {
        return riscvSvgPath;
    }

    /**
     * Switches the pipeline mode.
     * Resets the simulation, parses the input and updates the UI.
     * Adds a setting for enabling and disabling data hazard detection.
     * @param {string} mode pipeline mode ("five_stage_pipeline" or "single_stage_pipeline")
     */
    switchPipelineMode(mode) {
        this.pipelineMode = mode;
        if (mode !== "five_stage_pipeline") {
            this.deactivateVisualization();
            this.domNodes.dataHazardDetectionSettings.remove();
            delete this.domNodes.dataHazardDetectionSettings;
        }
        this.reset();
        if (mode === "five_stage_pipeline") {
            this.activateVisualization();
            this.domNodes.dataHazardDetectionSettings =
                getRiscvDataHazardSettings(
                    this.dataHazardDetection,
                    (doEnable) => this.switchDataHazardDetection(doEnable)
                );
            this.domNodes.customSettingsContainer.appendChild(
                this.domNodes.dataHazardDetectionSettings
            );
        }
    }

    /**
     * Enables or disables data hazard detection (only relevant for five stage pipeline).
     * Resets the simulation, parses the input and updates the UI.
     * @param {boolean} doEnable Whether to enable data hazard detection or not
     */
    switchDataHazardDetection(doEnable) {
        this.dataHazardDetection = doEnable;
        this.reset();
    }

    /**
     * Updates the register table.
     */
    updateRegisterTable() {
        const valueRepresentations =
            this.pythonSimulation.state.register_file.reg_repr();
        for (let i = 0; i < valueRepresentations.length; i++) {
            let entry = valueRepresentations.get(i);
            const row = this.domNodes.registerTableBody.children.item(i);
            const cell = row.children.item(2);
            cell.innerText = entry.get(this.regRepresentationMode);
            entry.destroy();
        }
        valueRepresentations.destroy();
    }

    /**
     * Updates the memory table.
     */
    updateMemoryTable() {
        this.clearMemoryTable();
        const valueRepresentations =
            this.pythonSimulation.get_data_memory_repr();
        for (const entry of valueRepresentations) {
            const address = entry.get(0);
            const values = entry.get(1);
            const value = values.get(this.memRepresentationMode);
            const row = this.domNodes.memoryTableBody.insertRow();
            const cell1 = row.insertCell();
            const cell2 = row.insertCell();
            cell1.innerText = address;
            cell2.innerText = value;
            if (this.previousMemoryValues[address] !== values.get(1)) {
                this.previousMemoryValues[address] = values.get(1);
                cell2.classList.add("highlight");
            }
            values.destroy();
            entry.destroy();
        }
        valueRepresentations.destroy();
    }

    /**
     * Clears the RISC-V memory table.
     */
    clearMemoryTable() {
        this.domNodes.memoryTableBody.innerHTML = "";
    }

    /**
     * Updates the instruction table.
     */
    updateInstructionTable() {
        this.clearInstructionTable();
        const valueRepresentations =
            this.pythonSimulation.get_instruction_memory_repr();
        for (const entry of valueRepresentations) {
            const address = entry.get(0);
            const instruction = entry.get(1);
            const stage = entry.get(2);
            const row = this.domNodes.instructionTableBody.insertRow();
            const cell1 = row.insertCell();
            const cell2 = row.insertCell();
            const cell3 = row.insertCell();
            cell1.innerText = address;
            cell2.innerText = instruction;
            cell3.innerText = stage == "Single" ? "<-" : stage;
            entry.destroy();
        }
        valueRepresentations.destroy();
    }

    /**
     * Clears the instruction table.
     */
    clearInstructionTable() {
        this.domNodes.instructionTableBody.innerHTML = "";
    }

    getIsaName() {
        return "RISC-V";
    }

    getDocumentation() {
        return riscvDocumentation;
    }

    updateUI() {
        const hasInstructions = this.pythonSimulation.has_instructions();
        const hasStarted = this.pythonSimulation.has_started;
        const hasFinished = this.pythonSimulation.is_done();

        const stepButton = this.domNodes.stepButton;
        const pauseButton = this.domNodes.pauseButton;
        const runButton = this.domNodes.runButton;
        const resetButton = this.domNodes.resetButton;

        // If there are unparsed changes, do not update the tables and disable all buttons
        if (this.hasUnparsedChanges) {
            stepButton.disabled = true;
            runButton.disabled = true;
            resetButton.disabled = true;
            pauseButton.disabled = true;
            return;
        }

        // No changes since the last parsing
        this.updateRegisterTable();
        this.updateMemoryTable();
        this.updateInstructionTable();
        // this.removeEditorHighlights(); // TODO
        if (this.visualizationLoaded) {
            this.updateVisualization();
        }

        if (this.error !== null) {
            stepButton.disabled = true;
            runButton.disabled = true;
            resetButton.disabled = !hasStarted;
            pauseButton.disabled = true;
            const errorType = this.error.get(0);
            const errorMessage = this.error.get(1);
            switch (errorType) {
                case "ParserException": {
                    const line = this.error.get(2);
                    //this.highlightEditorLine(line, errorMessage); // TODO Bring back line highlights
                    break;
                }
                case "InstructionExecutionException": {
                    const address = this.error.get(2);
                    this.highlightInstructionTableRow(address);
                    this.setOutputFieldContent(errorMessage);
                    break;
                }
                default: {
                    this.setOutputFieldContent(errorMessage);
                    break;
                }
            }
            return;
        }

        // There was no error
        if (!hasInstructions) {
            this.setOutputFieldContent("Ready!");
            stepButton.disabled = true;
            runButton.disabled = true;
            resetButton.disabled = true;
            pauseButton.disabled = true;
            return;
        }

        // There are instructions
        if (!hasStarted) {
            setEditorReadOnly(false);
            this.setOutputFieldContent("Ready!");
            stepButton.disabled = false;
            runButton.disabled = false;
            resetButton.disabled = true;
            pauseButton.disabled = true;
            return;
        }

        // The simulation has already started
        this.updatePerformanceMetrics();
        setEditorReadOnly(true);

        if (this.isRunning) {
            stepButton.disabled = true;
            runButton.disabled = true;
            resetButton.disabled = true;
            pauseButton.disabled = false;
            return;
        }

        pauseButton.disabled = true;

        // The "run" button was not pressed
        if (hasFinished) {
            stepButton.disabled = true;
            runButton.disabled = true;
            resetButton.disabled = false;
        } else {
            stepButton.disabled = false;
            resetButton.disabled = false;
            runButton.disabled = false;
        }
    }

    reset() {
        this.previousMemoryValues = [];
        this.pythonSimulation.destroy();
        this.pythonSimulation = this.getNewPythonSimulation();
        super.reset();
    }

    supportsVisualization() {
        return false;
    }

    setOutputFieldContent(str) {
        this.domNodes.outputField.innerText = str;
    }

    /**
     * Removes all of RISC-V's custom elements from the DOM.
     */
    removeContentFromDOM() {
        document.getElementById("riscv-register-table-container").remove();
        document.getElementById("riscv-memory-table-container").remove();
        document.getElementById("riscv-instruction-table-container").remove();
        document.getElementById("riscv-output-container").remove();
        super.removeContentFromDOM();
    }

    highlightInstructionTableRow(address) {
        const tbody = this.domNodes.instructionTableBody;
        for (let position = 0; position < tbody.rows.length; position++) {
            const row = tbody.rows[position];
            if (Number(row.cells[0].innerHTML) == address) {
                for (let cell of row.cells) {
                    cell.classList.add("highlight");
                }
            }
        }
    }

    // TODO: Replace all the code below.

    updateVisualization() {
        this.update_IF_Stage();
        this.update_ID_Stage();
        this.update_EX_Stage();
        this.update_MEM_Stage();
        this.update_WB_Stage();
        this.update_other_visualization_stuff();
    }

    update_IF_Stage() {
        const parameters = this.pythonSimulation.update_IF_Stage();
        const mnemonic = parameters.get("mnemonic");
        const instruction = parameters.get("instruction");
        const address_of_instruction = parameters.get("address_of_instruction");
        const pc = parameters.get("PC");
        const pc_plus_instruction_length = parameters.get(
            "pc_plus_instruction_length"
        );
        const i_length = parameters.get("i-length");
        // Update the mnemonic
        this.set_svg_text_complex_middle_align("Fetch", mnemonic);
        // Update Instr[31-0]
        this.set_svg_text_complex_right_align(
            "InstructionMemoryInstrText",
            instruction
        );
        if (instruction != "" && instruction != undefined) {
            this.set_svg_colour("InstructionMemory", "blue");
        } else {
            this.set_svg_colour("InstructionMemory", "black");
        }

        // Updates the Read Adress in the instr memory, it is a value if the reset is not pressed, otherwise undefined
        this.set_svg_text_complex_left_align(
            "InstructionReadAddressText",
            address_of_instruction
        );

        // Updates the PC value:
        this.set_svg_text_complex_middle_align("PC", this.previous_pc);
        this.previous_pc = pc;
        if (Number.isInteger(address_of_instruction)) {
            this.set_svg_colour("FetchPCOut", "blue");
        } else {
            this.set_svg_colour("FetchPCOut", "black");
        }

        // Updates the result of the Adder that adds pc and instr lenght
        this.set_svg_text_complex_middle_align(
            "FetchAddOutText",
            pc_plus_instruction_length
        );
        if (Number.isInteger(pc_plus_instruction_length)) {
            this.set_svg_colour("FetchAddOut", "blue");
        } else {
            this.set_svg_colour("FetchAddOut", "black");
        }

        this.set_svg_text_complex_middle_align("I-LengthText", i_length);
        if (Number.isInteger(i_length)) {
            this.set_svg_colour("FetchI-Length", "blue");
        } else {
            this.set_svg_colour("FetchI-Length", "black");
        }
        parameters.destroy();
    }

    update_ID_Stage() {
        const idData = this.pythonSimulation.update_ID_Stage();
        const parameters = idData.get(0);
        const control_unit_signals = idData.get(1);
        const mnemonic = parameters.get("mnemonic");
        const register_read_addr_1 = parameters.get("register_read_addr_1");
        const register_read_addr_2 = parameters.get("register_read_addr_2");
        const register_read_data_1 = parameters.get("register_read_data_1");
        const register_read_data_2 = parameters.get("register_read_data_2");
        const imm = parameters.get("imm");
        const write_register = parameters.get("write_register");
        const pc_plus_instruction_length = parameters.get(
            "pc_plus_instruction_length"
        );
        const address_of_instruction = parameters.get("address_of_instruction");

        this.set_svg_text_complex_middle_align("Decode", mnemonic);

        this.set_svg_text_complex_left_align(
            "RegisterFileReadAddress1Text",
            register_read_addr_1
        );
        if (Number.isInteger(register_read_addr_1)) {
            this.set_svg_colour("DecodeInstructionMemory1", "blue");
        } else {
            this.set_svg_colour("DecodeInstructionMemory1", "black");
        }

        this.set_svg_text_complex_left_align(
            "RegisterFileReadAddress2Text",
            register_read_addr_2
        );
        if (Number.isInteger(register_read_addr_2)) {
            this.set_svg_colour("DecodeInstructionMemory2", "blue");
        } else {
            this.set_svg_colour("DecodeInstructionMemory2", "black");
        }

        this.set_svg_text_complex_right_align(
            "RegisterFileReadData1Text",
            register_read_data_1
        );
        if (Number.isInteger(register_read_data_1)) {
            this.set_svg_colour("RegisterFileReadData1", "blue");
        } else {
            this.set_svg_colour("RegisterFileReadData1", "black");
        }

        this.set_svg_text_complex_right_align(
            "RegisterFileReadData2Text",
            register_read_data_2
        );
        if (Number.isInteger(register_read_data_2)) {
            this.set_svg_colour("RegisterFileReadData2", "blue");
        } else {
            this.set_svg_colour("RegisterFileReadData2", "black");
        }

        this.set_svg_text_complex_middle_align("ImmGenText", imm);
        if (Number.isInteger(imm)) {
            this.set_svg_colour("ImmGenOut", "blue");
        } else {
            this.set_svg_colour("ImmGenOut", "black");
        }
        if (Number.isInteger(imm)) {
            this.set_svg_colour("DecodeInstructionMemory3", "blue");
        } else {
            this.set_svg_colour("DecodeInstructionMemory3", "black");
        }

        this.set_svg_text_complex_middle_align(
            "DecodeInstructionMemory4Text",
            write_register
        );
        if (Number.isInteger(write_register)) {
            this.set_svg_colour("DecodeInstructionMemory4", "blue");
        } else {
            this.set_svg_colour("DecodeInstructionMemory4", "black");
        }

        this.set_svg_text_complex_middle_align(
            "DecodeFetchAddOutText",
            pc_plus_instruction_length
        );
        if (Number.isInteger(pc_plus_instruction_length)) {
            this.set_svg_colour("DecodeFetchAddOut", "blue");
        } else {
            this.set_svg_colour("DecodeFetchAddOut", "black");
        }

        this.set_svg_text_complex_middle_align(
            "DecodeUpperFetchPCOutText",
            address_of_instruction
        );
        this.set_svg_text_complex_middle_align(
            "DecodeLowerFetchPCOutText",
            address_of_instruction
        );
        if (Number.isInteger(address_of_instruction)) {
            this.set_svg_colour("DecodeUpperFetchPCOut", "blue");
            this.set_svg_colour("DecodeLowerFetchPCOut", "blue");
            this.set_svg_colour("DecodeInstructionMemory", "blue");
        } else {
            this.set_svg_colour("DecodeUpperFetchPCOut", "black");
            this.set_svg_colour("DecodeLowerFetchPCOut", "black");
            this.set_svg_colour("DecodeInstructionMemory", "black");
        }
        parameters.destroy();
        control_unit_signals.destroy();
        idData.destroy();
    }

    update_EX_Stage() {
        const exData = this.pythonSimulation.update_EX_Stage();
        const parameters = exData.get(0);
        const control_unit_signals = exData.get(1);
        const mnemonic = parameters.get("mnemonic");
        const alu_in_1 = parameters.get("alu_in_1");
        const alu_in_2 = parameters.get("alu_in_2");
        const register_read_data_1 = parameters.get("register_read_data_1");
        const register_read_data_2 = parameters.get("register_read_data_2");
        const imm = parameters.get("imm");
        const result = parameters.get("result");
        const write_register = parameters.get("write_register");
        const comparison = parameters.get("comparison");
        const pc_plus_imm = parameters.get("pc_plus_imm");
        const pc_plus_instruction_length = parameters.get(
            "pc_plus_instruction_length"
        );
        const address_of_instruction = parameters.get("address_of_instruction");
        const alu_src_1 = control_unit_signals.get("alu_src_1");
        const alu_src_2 = control_unit_signals.get("alu_src_2");
        const alu_op = control_unit_signals.get("alu_op");

        this.set_svg_text_complex_middle_align("Execute", mnemonic);

        this.set_svg_text_complex_middle_align(
            "ExecuteRightMuxOutText",
            alu_in_1
        );
        if (Number.isInteger(alu_in_1)) {
            this.set_svg_colour("ExecuteRightMuxOut", "blue");
        } else {
            this.set_svg_colour("ExecuteRightMuxOut", "black");
        }

        this.set_svg_text_complex_middle_align(
            "ExecuteLeftMuxOutText",
            alu_in_2
        );
        if (Number.isInteger(alu_in_2)) {
            this.set_svg_colour("ExecuteLeftMuxOut", "blue");
        } else {
            this.set_svg_colour("ExecuteLeftMuxOut", "black");
        }

        if (Number.isInteger(register_read_data_1)) {
            this.set_svg_colour("ExecuteRegisterFileReadData1", "blue");
        } else {
            this.set_svg_colour("ExecuteRegisterFileReadData1", "black");
        }

        this.set_svg_text_complex_middle_align(
            "ExecuteRegisterFileReadData2Text2",
            register_read_data_2
        );
        if (Number.isInteger(register_read_data_2)) {
            this.set_svg_colour("ExecuteRegisterFileReadData2", "blue");
        } else {
            this.set_svg_colour("ExecuteRegisterFileReadData2", "black");
        }

        this.set_svg_text_complex_middle_align("ExecuteImmGenText1", imm);
        this.set_svg_text_complex_middle_align("ExecuteImmGenText3", imm);
        if (Number.isInteger(imm)) {
            this.set_svg_colour("ExecuteImmGen", "blue");
        } else {
            this.set_svg_colour("ExecuteImmGen", "black");
        }

        this.set_svg_text_complex_left_align("ALUResultText", result);
        if (Number.isInteger(result)) {
            this.set_svg_colour("ExecuteAluResult", "blue");
        } else {
            this.set_svg_colour("ExecuteAluResult", "black");
        }

        this.set_svg_text_complex_middle_align(
            "ExecuteInstructionMemory4Text",
            write_register
        );
        if (Number.isInteger(write_register)) {
            this.set_svg_colour("ExecuteInstructionMemory4", "blue");
        } else {
            this.set_svg_colour("ExecuteInstructionMemory4", "black");
        }

        this.set_svg_text_complex_middle_align("ExecuteAddText", pc_plus_imm);
        if (Number.isInteger(pc_plus_imm)) {
            this.set_svg_colour("ExecuteAdd", "blue");
        } else {
            this.set_svg_colour("ExecuteAdd", "black");
        }

        this.set_svg_text_complex_middle_align(
            "ExecuteFetchAddOutText",
            pc_plus_instruction_length
        );
        if (Number.isInteger(pc_plus_instruction_length)) {
            this.set_svg_colour("ExecuteFetchAddOut", "blue");
        } else {
            this.set_svg_colour("ExecuteFetchAddOut", "black");
        }

        this.set_svg_text_complex_middle_align(
            "ExecuteUpperFetchPCOutText",
            address_of_instruction
        );
        if (Number.isInteger(address_of_instruction)) {
            this.set_svg_colour("ExecuteUpperFetchPCOut", "blue");
            this.set_svg_colour("ExecuteLowerFetchPCOut", "blue");
        } else {
            this.set_svg_colour("ExecuteUpperFetchPCOut", "black");
            this.set_svg_colour("ExecuteLowerFetchPCOut", "black");
        }

        if (comparison == true) {
            this.set_svg_colour("ALUComparison", "green");
        } else {
            this.set_svg_colour("ALUComparison", "black");
        }

        if (alu_src_1 == true) {
            this.set_svg_colour("ControlUnitLeftRight3", "green");
        } else {
            this.set_svg_colour("ControlUnitLeftRight3", "black");
        }

        if (alu_src_2 == true) {
            this.set_svg_colour("ControlUnitLeftRight4", "green");
        } else {
            this.set_svg_colour("ControlUnitLeftRight4", "black");
        }

        if (Number.isInteger(alu_op)) {
            this.set_svg_colour("AluControl", "blue");
        } else {
            this.set_svg_colour("AluControl", "black");
        }
        parameters.destroy();
        control_unit_signals.destroy();
        exData.destroy();
    }

    update_MEM_Stage() {
        const memData = this.pythonSimulation.update_MEM_Stage();
        const parameters = memData.get(0);
        const control_unit_signals = memData.get(1);
        const mnemonic = parameters.get("mnemonic");
        const memory_address = parameters.get("memory_address");
        const result = parameters.get("result");
        const memory_write_data = parameters.get("memory_write_data");
        const memory_read_data = parameters.get("memory_read_data");
        const write_register = parameters.get("write_register");
        const comparison = parameters.get("comparison");
        const comparison_or_jump = parameters.get("comparison_or_jump");
        const pc_plus_imm = parameters.get("pc_plus_imm");
        const pc_plus_instruction_length = parameters.get(
            "pc_plus_instruction_length"
        );
        const imm = parameters.get("imm");
        const jump = control_unit_signals.get("jump");
        const alu_to_pc = control_unit_signals.get("alu_to_pc");

        this.set_svg_text_complex_middle_align("Memory", mnemonic);

        this.set_svg_text_complex_left_align(
            "DataMemoryAddressText",
            memory_address
        );
        this.set_svg_text_complex_middle_align(
            "MemoryExecuteAluResultText",
            result
        );
        this.set_svg_text_complex_middle_align(
            "MemoryExecuteAluResultText2",
            result
        );
        if (Number.isInteger(result) && Number.isInteger(memory_address)) {
            this.set_svg_colour("MemoryExecuteAluResult", "blue");
        } else {
            this.set_svg_colour("MemoryExecuteAluResult", "black");
        }

        this.set_svg_text_complex_left_align(
            "DataMemoryWriteDataText",
            memory_write_data
        );
        if (Number.isInteger(memory_write_data)) {
            this.set_svg_colour("MemoryRegisterFileReadData2", "blue");
        } else {
            this.set_svg_colour("MemoryRegisterFileReadData2", "black");
        }

        this.set_svg_text_complex_right_align(
            "DataMemoryReadDataText",
            memory_read_data
        );
        if (Number.isInteger(memory_read_data)) {
            this.set_svg_colour("DataMemoryReadData", "blue");
        } else {
            this.set_svg_colour("DataMemoryReadData", "black");
        }

        this.set_svg_text_complex_middle_align(
            "MemoryInstructionMemory4Text",
            write_register
        );
        if (Number.isInteger(write_register)) {
            this.set_svg_colour("MemoryInstructionMemory4", "blue");
        } else {
            this.set_svg_colour("MemoryInstructionMemory4", "black");
        }

        if (comparison == true) {
            this.set_svg_colour("MemoryALUComparison", "green");
        } else {
            this.set_svg_colour("MemoryALUComparison", "black");
        }

        if (comparison_or_jump == true) {
            this.set_svg_colour("MemoryJumpOut", "green");
        } else {
            this.set_svg_colour("MemoryJumpOut", "black");
        }

        this.set_svg_text_complex_middle_align(
            "MemoryExecuteAddOutText",
            pc_plus_imm
        );
        if (Number.isInteger(pc_plus_imm)) {
            this.set_svg_colour("MemoryExecuteAddOut", "blue");
        } else {
            this.set_svg_colour("MemoryExecuteAddOut", "black");
        }

        this.set_svg_text_complex_middle_align(
            "MemoryFetchAddOutText",
            pc_plus_instruction_length
        );
        if (Number.isInteger(pc_plus_instruction_length)) {
            this.set_svg_colour("MemoryFetchAddOut", "blue");
        } else {
            this.set_svg_colour("MemoryFetchAddOut", "black");
        }

        this.set_svg_text_complex_middle_align("MemoryImmGenText", imm);
        if (Number.isInteger(imm)) {
            this.set_svg_colour("MemoryImmGen", "blue");
        } else {
            this.set_svg_colour("MemoryImmGen", "black");
        }

        if (jump == true) {
            this.set_svg_colour("ControlUnitLeftRight", "green");
        } else {
            this.set_svg_colour("ControlUnitLeftRight", "black");
        }

        if (alu_to_pc == true) {
            this.set_svg_colour("ControlUnitLeft", "green");
        } else {
            this.set_svg_colour("ControlUnitLeft", "black");
        }
        parameters.destroy();
        control_unit_signals.destroy();
        memData.destroy();
    }

    update_WB_Stage() {
        const wbData = this.pythonSimulation.update_WB_Stage();
        const parameters = wbData.get(0);
        const control_unit_signals = wbData.get(1);
        const mnemonic = parameters.get("mnemonic");
        const register_write_data = parameters.get("register_write_data");
        const write_register = parameters.get("write_register");
        const memory_read_data = parameters.get("memory_read_data");
        const alu_result = parameters.get("alu_result");
        const pc_plus_instruction_length = parameters.get(
            "pc_plus_instruction_length"
        );
        const imm = parameters.get("imm");
        const wbsrc = control_unit_signals.get("wb_src");

        this.set_svg_text_complex_middle_align("WriteBack", mnemonic);

        this.set_svg_text_complex_left_align(
            "RegisterFileWriteDataText",
            register_write_data
        );
        if (Number.isInteger(register_write_data)) {
            this.set_svg_colour("WriteBackMuxOut", "blue");
        } else {
            this.set_svg_colour("WriteBackMuxOut", "black");
        }

        this.set_svg_text_complex_left_align(
            "RegisterFileWriteRegisterText",
            write_register
        );
        if (Number.isInteger(write_register)) {
            this.set_svg_colour("WriteBackInstructionMemory4", "blue");
        } else {
            this.set_svg_colour("WriteBackInstructionMemory4", "black");
        }

        this.set_svg_text_complex_middle_align(
            "WriteBackDataMemoryReadDataText",
            memory_read_data
        );
        if (Number.isInteger(memory_read_data)) {
            this.set_svg_colour("WriteBackDataMemoryReadData", "blue");
        } else {
            this.set_svg_colour("WriteBackDataMemoryReadData", "black");
        }

        this.set_svg_text_complex_middle_align(
            "WriteBackExecuteAluResultText",
            alu_result
        );
        if (Number.isInteger(alu_result)) {
            this.set_svg_colour("WriteBackExecuteAluResult", "blue");
        } else {
            this.set_svg_colour("WriteBackExecuteAluResult", "black");
        }

        this.set_svg_text_complex_middle_align(
            "WriteBackFetchAddOutText",
            pc_plus_instruction_length
        );
        if (Number.isInteger(pc_plus_instruction_length)) {
            this.set_svg_colour("WriteBackFetchAddOut", "blue");
        } else {
            this.set_svg_colour("WriteBackFetchAddOut", "black");
        }

        this.set_svg_text_complex_middle_align("WriteBackImmGenText", imm);
        if (Number.isInteger(imm)) {
            this.set_svg_colour("WriteBackImmGen", "blue");
        } else {
            this.set_svg_colour("WriteBackImmGen", "black");
        }

        this.set_svg_text_complex_middle_align("wbsrc", wbsrc);
        if (Number.isInteger(wbsrc)) {
            this.set_svg_colour("ControlUnitLeftRight2", "blue");
        } else {
            this.set_svg_colour("ControlUnitLeftRight2", "black");
        }
        parameters.destroy();
        control_unit_signals.destroy();
        wbData.destroy();
    }

    update_other_visualization_stuff() {
        const otherData =
            this.pythonSimulation.get_other_visualization_updates();
        if (otherData === undefined) {
            return;
        }
        const pc_plus_imm_or_pc_plus_instruction_length = otherData.get(0);
        const pc_plus_imm_or_pc_plus_instruction_length_or_ALU_result =
            otherData.get(1);
        this.set_svg_text_complex_middle_align(
            "FetchRightMuxOutText",
            pc_plus_imm_or_pc_plus_instruction_length
        );
        this.set_svg_text_complex_middle_align(
            "FetchLeftMuxOutText",
            pc_plus_imm_or_pc_plus_instruction_length_or_ALU_result
        );
        if (Number.isInteger(pc_plus_imm_or_pc_plus_instruction_length)) {
            this.set_svg_colour("FetchRightMuxOut", "blue");
        } else {
            this.set_svg_colour("FetchRightMuxOut", "black");
        }

        if (
            Number.isInteger(
                pc_plus_imm_or_pc_plus_instruction_length_or_ALU_result
            )
        ) {
            this.set_svg_colour("path2453-0-7-7-9", "blue");
            this.set_svg_colour("path2453-2-5-7-0-7-5-1-0-4", "blue");
            this.set_svg_colour("path2453-2-5-7-0-7-6-2-29", "blue");
        } else {
            this.set_svg_colour("path2453-0-7-7-9", "black");
            this.set_svg_colour("path2453-2-5-7-0-7-5-1-0-4", "black");
            this.set_svg_colour("path2453-2-5-7-0-7-6-2-29", "black");
        }
        otherData.destroy();
    }

    /**set_svg_text_complex_right_align
     *
     * @param {string} id -- The id of the element where the text should be set
     * @param {string} str -- The text the element given by id should have, the text is right aligned
     */
    set_svg_text_complex_right_align(id, str) {
        const pipeline_svg = this.domNodes.visualization;
        pipeline_svg.getElementById(id).firstChild.nextSibling.style.fontSize =
            "15px";
        pipeline_svg.getElementById(id).firstChild.nextSibling.textContent =
            str;
        pipeline_svg
            .getElementById(id)
            .firstChild.nextSibling.setAttribute("text-anchor", "end");
    }

    /**set_svg_text_complex_right_align
     *
     * @param {string} id -- The id of the element where the text should be set
     * @param {string} str -- The text the element given by id should have, the text is left aligned
     */
    set_svg_text_complex_left_align(id, str) {
        const pipeline_svg = this.domNodes.visualization;
        pipeline_svg.getElementById(id).firstChild.nextSibling.style.fontSize =
            "15px";
        pipeline_svg.getElementById(id).firstChild.nextSibling.textContent =
            str;
        pipeline_svg
            .getElementById(id)
            .firstChild.nextSibling.setAttribute("text-anchor", "start");
    }

    /**set_svg_text_complex_right_align
     *
     * @param {string} id -- The id of the element where the text should be set
     * @param {string} str -- The text the element given by id should have, the text is middle aligned
     */
    set_svg_text_complex_middle_align(id, str) {
        const pipeline_svg = this.domNodes.visualization;
        pipeline_svg.getElementById(id).firstChild.nextSibling.style.fontSize =
            "15px";
        pipeline_svg.getElementById(id).firstChild.nextSibling.textContent =
            str;
        pipeline_svg
            .getElementById(id)
            .firstChild.nextSibling.setAttribute("text-anchor", "middle");
    }

    /**
     *
     * @param {string} id -- The id of the element where the colour should be set
     * @param {string} str -- The colour the element and all its childnodes should have
     */
    set_svg_colour(id, str) {
        const pipeline_svg = this.domNodes.visualization;
        const Child_Nodes = pipeline_svg.getElementById(id).childNodes;
        if (Child_Nodes.length > 0) {
            for (let i = 0; i < Child_Nodes.length; i++) {
                this.set_svg_colour(Child_Nodes[i].id, str);
            }
        } else {
            pipeline_svg.getElementById(id).style.stroke = str;
            this.set_svg_marker_color(id, str);
        }
    }

    /**
     * Sets the color of the marker on the given path if it has one (multiple markers will probably not work).
     * @param {string} id id of the path that might have marker-start or marker-end
     * @param {string} str color name (either black, blue or green)
     */
    set_svg_marker_color(id, str) {
        const pipeline_svg = this.domNodes.visualization;
        // the marker is part of the style attribute
        var styleAttribute = pipeline_svg
            .getElementById(id)
            .getAttribute("style");
        // marker must contain 'Triangle_XXXXXX' where X is a hexnum. Can be followed or prepended by other characters.
        var marker_regex = /Triangle_[0-9a-fA-F]{6}/;
        var result = marker_regex.exec(styleAttribute);
        if (result != null) {
            // get the hex value for that color
            var hexColor = this.strToHexColor(str);
            var newMarker = "Triangle_" + hexColor;
            // create the new style string where the new color is used
            var newStyleAttribute = styleAttribute.replace(
                marker_regex,
                newMarker
            );
            pipeline_svg
                .getElementById(id)
                .setAttribute("style", newStyleAttribute);
        }
    }

    /**
     * Turns color names into hex values.
     * @param {str} str name of the color - must be either black, blue or green.
     * @returns {Number} the corresponding hex value for that color.
     */
    strToHexColor(str) {
        if (str === "black") {
            return "000000";
        }
        if (str === "blue") {
            return "0000FF";
        }
        if (str === "green") {
            return "008000";
        }
        console.log("color not supported");
        return "000000";
    }
}
