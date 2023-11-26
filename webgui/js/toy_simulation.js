class ToySimulation {
    constructor(pythonSimulation) {
        this.pythonSimulation = pythonSimulation;
        this.insertToyElements();
        this.outputField = document.getElementById("output-field-id");
        this.previousMemoryValues = [];
        this.regRepresentationMode = 1; // TODO: Make this user-selectable
        this.memRepresentationMode = 1;
    }

    reset(pythonSimulation) {
        this.pythonSimulation = pythonSimulation;
        this.previousMemoryValues = [];
        this.updateUI();
    }

    /**
     * Parses and loads the content of the input field into the simulation.
     * If there was an error during parsing, the output field content will be set to the error message.
     *
     * @returns {boolean} Whether parsing the input was successful
     */
    parseInput() {
        const input = editor.getValue(); // TODO: Maybe put static elements into an object that gets handed over to the simulation
        try {
            this.pythonSimulation.load_program(input);
            return true;
        } catch (err) {
            this.setOutputFieldContent(err);
            return false;
        }
    }

    /**
     * Executes a single cycle of the simulation.
     * Errors will be printed to the output field.
     */
    step() {
        if (!this.pythonSimulation.has_started) {
            if (!this.parseInput()) {
                return;
            }
        }
        try {
            this.pythonSimulation.single_step();
            this.updateUI();
        } catch (error) {
            this.setOutputFieldContent(error);
        }
    }

    /**
     * Executes two cycles of the simulation.
     * Should only be called if the next cycle to be executed is the first cycle of the current instruction,
     * otherwise it will print an error to the output field.
     */
    doubleStep() {
        if (!this.pythonSimulation.has_started) {
            // TODO: Duplicate code
            if (!this.parseInput()) {
                return;
            }
        }
        try {
            this.pythonSimulation.step();
            this.updateUI();
        } catch (error) {
            this.setOutputFieldContent(error);
        }
    }

    /**
     * Updates all UI elements.
     */
    updateUI() {
        this.updateRegisters();
        this.updateMemoryTable();
        this.updatePerformanceMetrics();
    }

    run() {
        throw Error("Not implemented.");
    }

    pause() {
        throw Error("Not implemented.");
    }

    /**
     * Sets the content of the output field to the current performance metrics.
     */
    updatePerformanceMetrics() {
        this.setOutputFieldContent(
            this.pythonSimulation.get_performance_metrics()
        );
    }

    /**
     * @param {string} str The string that the output field's content will be set to.
     */
    setOutputFieldContent(str) {
        this.outputField.innerText = str;
    }

    /**
     * Updates the values in the register table.
     */
    updateRegisters() {
        const registers = this.pythonSimulation.get_register_representations();
        document.getElementById("toy-accu-id").innerText = registers
            .get("accu")
            .get(this.regRepresentationMode);
        document.getElementById("toy-pc-id").innerText = registers
            .get("pc")
            .get(this.regRepresentationMode);
        document.getElementById("toy-ir-id").innerText = registers
            .get("ir")
            .get(this.regRepresentationMode);
        registers.destroy();
    }

    /**
     * Clears the TOY memory table.
     */
    clearMemoryTable() {
        document.getElementById("toy-memory-table-body-id").innerHTML = "";
    }

    /**
     * Clears and updates the TOY memory table.
     */
    updateMemoryTable() {
        this.clearMemoryTable();
        const valueRepresentations =
            this.pythonSimulation.get_memory_table_entries();
        for (const entry of valueRepresentations) {
            const address = entry.get(0);
            const values = entry.get(1);
            const value = values.get(this.memRepresentationMode);
            const instructionRepresentation = entry.get(2);
            const cycle = entry.get(3);
            const row = document
                .getElementById("toy-memory-table-body-id")
                .insertRow();
            const cell1 = row.insertCell();
            const cell2 = row.insertCell();
            const cell3 = row.insertCell();
            cell1.innerText = address;
            cell2.innerText = value;
            cell3.innerText = instructionRepresentation;
            if (this.previousMemoryValues[address] !== values[1]) {
                this.previousMemoryValues[address] = values[1];
                cell2.classList.add("highlight");
            }
            if (cycle !== "") {
                cell1.innerHTML = html`<span
                        class="toy-current-cycle text-light bg-dark"
                        title="cycle ${cycle}"
                        >${cycle + instructionArrow}</span
                    >
                    ${cell1.innerHTML}`;
            }
        }
        valueRepresentations.destroy();
    }

    /**
     * @returns {Node} A Node containing the TOY accu and memory table.
     */
    getMemoryAndAccuColumn() {
        return createNode(html`<div
            id="toy-main-text-container-id"
            class="d-flex flex-column"
        >
            <div class="mb-3" id="toy-registers-wrapper">
                <span class="text-element-heading">Registers</span>
                <table
                    class="table table-sm table-hover table-bordered mono-table mb-0"
                    id="toy-register-table"
                >
                    <tr>
                        <td>ACCU</td>
                        <td id="toy-accu-id">0</td>
                    </tr>
                    <tr>
                        <td>PC</td>
                        <td id="toy-pc-id"></td>
                    </tr>
                    <tr>
                        <td>IR</td>
                        <td id="toy-ir-id"></td>
                    </tr>
                </table>
            </div>
            <div class="mb-3" id="toy-memory-wrapper">
                <span class="text-element-heading">Memory</span>
                <table
                    id="toy-memory-table-id"
                    class="table table-sm table-hover table-bordered mono-table mb-0"
                >
                    <thead>
                        <tr>
                            <th>Address</th>
                            <th>Value</th>
                            <th>Instruction</th>
                        </tr>
                    </thead>
                    <tbody id="toy-memory-table-body-id"></tbody>
                </table>
            </div>
            <div id="toy-output-wrapper">
                <span class="text-element-heading">Output</span>
                <div
                    id="output-field-id"
                    class="flex-shrink-0 archsim-default-border"
                ></div>
            </div>
        </div>`);
    }

    /**
     * @returns {Node} A Node containing the double step button.
     */
    getDoubleStepButton() {
        return createNode(html`<button
            id="button-double-step-simulation-id"
            class="btn btn-primary btn-sm control-button me-1"
            title="double step"
            onclick="simulation.doubleStep();"
        >
            <img src="img/double-step.svg" />
        </button>`);
    }

    /**
     * Inserts all of TOY's coustom elements into the DOM.
     */
    insertToyElements() {
        document
            .getElementById("text-editor-separator")
            .after(this.getMemoryAndAccuColumn());
        const doubleStepButton = this.getDoubleStepButton();
        document
            .getElementById("button-step-simulation-id")
            .after(doubleStepButton);
        document.getElementById("page-heading-id").innerText = "TOY Simulator";
        document.title = "TOY Simulator";
    }

    /**
     * Removes all of TOY's custom elements from the DOM.
     */
    destroyToyElements() {
        document.getElementById("toy-main-text-container-id").remove();
        document.getElementById("button-double-step-simulation-id").remove();
    }

    // /**
    //  * Executes the first cycle step and the second cycle step.
    //  */
    // doubleStep() {
    //     is_run_simulation = false;
    //     manual_run = true;
    //     editor.save();
    //     disable_editor();
    //     evaluatePython_step_sim();
    //     enable_run();
    //     disable_pause();
    //     enable_step();
    // }

    // /**
    //  * Disables the double step button.
    //  */
    // disable_double_step() {
    //     document.getElementById(
    //         "button-double-step-simulation-id"
    //     ).disabled = true;
    // }

    // /**
    //  * Enables the double step button.
    //  */
    // enable_double_step() {
    //     document.getElementById(
    //         "button-double-step-simulation-id"
    //     ).disabled = false;
    // }

    /**
     * Sets the fill color of an element.
     * @param {string} id target id.
     * @param {string} color hex color string.
     */
    toySvgHighlight(id, color) {
        const svg =
            document.getElementById("toy-visualization").contentDocument;
        svg.getElementById(id).setAttribute("style", "fill: " + color);
    }

    /**
     * Sets the text content of an element.
     * @param {string} id target id.
     * @param {string} text text to set as the content of the element.
     */
    toySvgSetText(id, text) {
        const svg =
            document.getElementById("toy-visualization").contentDocument;
        svg.getElementById(id).textContent = text;
    }

    /**
     * Shows or hides an element.
     * @param {string} id target id.
     * @param {boolean} doShow Whether to show the element (display: block). Else it will be hidden (display: none)
     */
    toySvgShow(id, doShow) {
        const display = doShow ? "block" : "none";
        const svg =
            document.getElementById("toy-visualization").contentDocument;
        svg.getElementById(id).style.display = display;
    }
}
