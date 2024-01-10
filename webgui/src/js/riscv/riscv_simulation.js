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
import { showLinterError, clearLinterError } from "../editor";

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
        clearLinterError();
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
                    showLinterError(line, errorMessage);
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

    updateVisualization() {
        const updateValues =
            this.pythonSimulation.get_riscv_five_stage_svg_update_values();
        for (let i = 0; i < updateValues.length; i++) {
            const update = updateValues.get(i);
            const id = update.get(0);
            const action = update.get(1);
            const value = update.get(2);
            switch (action) {
                case "highlight":
                    this.set_svg_colour(id, value);
                    break;
                case "write-left":
                    this.set_svg_text_complex_left_align(id, value);
                    break;
                case "write-center":
                    this.set_svg_text_complex_middle_align(id, value);
                    break;
                case "write-right":
                    this.set_svg_text_complex_right_align(id, value);
                    break;
            }
            update.destroy();
        }
        updateValues.destroy();
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
    set_svg_colour(id, colour) {
        const pipeline_svg = this.domNodes.visualization;
        const Child_Nodes = pipeline_svg.getElementById(id).childNodes;
        if (Child_Nodes.length > 0) {
            for (let i = 0; i < Child_Nodes.length; i++) {
                this.set_svg_colour(Child_Nodes[i].id, colour);
            }
        } else {
            pipeline_svg.getElementById(id).style.stroke = colour;
            this.set_svg_marker_color(id, colour);
        }
    }

    /**
     * Sets the color of the marker on the given path if it has one (multiple markers will probably not work).
     * @param {string} id id of the path that might have marker-start or marker-end
     * @param {string} str color name (either black, blue or green)
     */
    set_svg_marker_color(id, colour) {
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
            var hexColor = colour;
            var newMarker = "Triangle_" + hexColor.substring(1);
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
}
