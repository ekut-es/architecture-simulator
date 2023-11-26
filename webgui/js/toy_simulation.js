class ToySimulation {
    constructor(pythonSimulation) {
        this.pythonSimulation = pythonSimulation;
        this.insertToyElements();
    }

    /**
     * Parses and loads the content of the input field into the simulation.
     * If there was an error during parsing, the output field content will be set to the error message.
     */
    parseInput() {
        const input = document.getElementById("input").value;
        try {
            this.pythonSimulation.load_program(input);
        } catch (err) {
            addToOutput(err);
        }
    }

    /**
     * Updates the values in the register table.
     */
    updateRegisters() {
        const registers = simulation.get_register_representations();
        document.getElementById("toy-accu-id").innerText = registers
            .get("accu")
            .get(reg_representation_mode);
        document.getElementById("toy-pc-id").innerText = registers
            .get("pc")
            .get(reg_representation_mode);
        document.getElementById("toy-ir-id").innerText = registers
            .get("ir")
            .get(reg_representation_mode);
        registers.destroy();
    }

    /**
     * Clears the TOY memory table.
     */
    toyClearMemoryTable() {
        document.getElementById("toy-memory-table-body-id").innerHTML = "";
    }

    /**
     * Updates the TOY memory table.
     */
    toyUpdateMemoryTable() {
        const valueRepresentations =
            this.pythonSimulation.state.memory.memory_repr();
        value_representations_array = Array.from(value_representations);
        const value = value_representations_array[mem_representation_mode];
        const row = document
            .getElementById("toy-memory-table-body-id")
            .insertRow();
        const cell1 = row.insertCell();
        const cell2 = row.insertCell();
        const cell3 = row.insertCell();
        cell1.innerText = address;
        cell2.innerText = value;
        cell3.innerText = instruction_representation;
        if (previous_memory[address] !== value_representations_array[1]) {
            previous_memory[address] = value_representations_array[1];
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
        value_representations.destroy();
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
        // doubleStepButton.addEventListener("click", doubleStep);
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
