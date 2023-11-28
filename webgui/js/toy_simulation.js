class ToySimulation {
    /**
     * @param {pyProxy} pythonSimulation pyProxy of a ToySimulation.
     * @param {object} domNodes Object holding all the relevant nodes from the default page.
     */
    constructor(pythonSimulation, domNodes) {
        /**@type {pyProxy} A pyProxy of the ToySimulation object.*/
        this.pythonSimulation = pythonSimulation;
        /**@type {object} An object holding all relevant DOM Nodes.*/
        this.domNodes = domNodes;

        /**@type {Number} The selected representation mode for the registers. 0: bin, 1: udec, 2: hex, 3: sdec.*/
        this.regRepresentationMode = 1;
        /**@type {Number} The selected representation mode for the memory. 0: bin, 1: udec, 2: hex, 3: sdec.*/
        this.memRepresentationMode = 1;
        /**@type {?} The values of the memory from the last cycle.*/
        this.previousMemoryValues = [];
        /**@type {boolean} Whether the editor content has been changed since the last time it was parsed.*/
        this.hasUnparsedChanges = true;
        /**@type {boolean} Whether the user has clicked the run button and the simulation is still running. Not to be confused with this.pythonSimulation.has_started*/
        this.isRunning = false;
        /**@type {boolean} Indicates that the simulation should be paused if it is currently running.*/
        this.doPause = false;
        /**@type {str} The last error message. Will be empty if there was no error.*/
        this.error = "";

        this.insertContentIntoDOM();
        /**@type{Function} Debounces (triggers) auto parsing.*/
        this.debouncedAutoParsing = this.getDebouncedAutoParsing();
        editor.on("change", () => {
            this.hasUnparsedChanges = true;
            this.debouncedAutoParsing();
            this.updateUI();
        });
        this.parseInput();
        this.updateUI();
    }

    /**
     * Resets the internal state. Uses the given pythonSimulation. Parses the input and updates the UI.
     *
     * @param pythonSimulation pyProxy of a ToySimution Object
     */
    reset(pythonSimulation) {
        this.pythonSimulation = pythonSimulation;
        this.previousMemoryValues = [];
        this.error = "";
        this.parseInput();
        this.updateUI();
    }

    /**
     * Parses and loads the content of the input field into the simulation.
     * Sets the error attribute accordingly.
     *
     * @returns {boolean} Whether parsing the input was successful
     */
    parseInput() {
        const input = editor.getValue(); // TODO: Maybe put static elements into an object that gets handed over to the simulation
        this.hasUnparsedChanges = false;
        try {
            this.pythonSimulation.load_program(input);
            this.error = "";
            return true;
        } catch (err) {
            this.error = String(err);
            return false;
        }
    }

    /**
     * Returns a debounce function for the auto parsing timer.
     *
     * @param {number} timeout Time after which the input should be parsed.
     * @returns {function} Auto parsing debounce function. Does update the UI after parsing.
     */
    getDebouncedAutoParsing(timeout = 500) {
        let timer;
        return () => {
            clearTimeout(timer);
            timer = setTimeout(() => {
                this.parseInput();
                this.updateUI();
            }, timeout);
        };
    }

    /**
     * Executes a single cycle of the simulation.
     * Sets this.error accordingly and updates the UI unless specified otherwise.
     * Will not parse the input before stepping.
     *
     * @param {bool} updateUI Whether to update the UI or not.
     */
    step(updateUI = true) {
        try {
            this.pythonSimulation.single_step();
        } catch (error) {
            this.error = String(error);
        }
        if (updateUI) {
            this.updateUI();
        }
    }

    /**
     * Executes two cycles of the simulation.
     * Should only be called if the next cycle to be executed is the first cycle of the current instruction,
     * otherwise it will create an error.
     * Sets this.error accordingly and updates the UI.
     * Will not parse the input before stepping.
     */
    doubleStep() {
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
        const hasInstructions = this.pythonSimulation.has_instructions();
        const hasStarted = this.pythonSimulation.has_started;
        const hasFinished = this.pythonSimulation.is_done();
        const doubleStepAllowed = this.pythonSimulation.next_cycle == "1";

        const stepButton = this.domNodes.stepButton;
        const doubleStepButton = this.domNodes.doubleStepButton;
        const pauseButton = this.domNodes.pauseButton;
        const runButton = this.domNodes.runButton;
        const resetButton = this.domNodes.resetButton;

        // If there are unparsed changes, do not update the tables and disable all buttons
        if (this.hasUnparsedChanges) {
            stepButton.disabled = true;
            doubleStepButton.disabled = true;
            runButton.disabled = true;
            resetButton.disabled = true;
            pauseButton.disabled = true;
            return;
        }

        // No changes since the last parsing
        this.updateRegisters();
        this.updateMemoryTable();
        if (this.error !== "") {
            stepButton.disabled = true;
            doubleStepButton.disabled = true;
            runButton.disabled = true;
            resetButton.disabled = !hasStarted;
            pauseButton.disabled = true;
            this.setOutputFieldContent(this.error);
            return;
        }

        // There was no error
        if (!hasInstructions) {
            this.setOutputFieldContent("Ready!");
            stepButton.disabled = true;
            doubleStepButton.disabled = true;
            runButton.disabled = true;
            resetButton.disabled = true;
            pauseButton.disabled = true;
            return;
        }

        // There are instructions
        if (!hasStarted) {
            editor.setOption("readOnly", false);
            this.setOutputFieldContent("Ready!");
            stepButton.disabled = false;
            doubleStepButton.disabled = false;
            runButton.disabled = false;
            resetButton.disabled = true;
            pauseButton.disabled = true;
            return;
        }

        // The simulation has already started
        this.updatePerformanceMetrics();
        editor.setOption("readOnly", true);

        if (this.isRunning) {
            stepButton.disabled = true;
            doubleStepButton.disabled = true;
            runButton.disabled = true;
            resetButton.disabled = true;
            pauseButton.disabled = false;
            return;
        }

        pauseButton.disabled = true;

        // The "run" button was not pressed
        if (hasFinished) {
            stepButton.disabled = true;
            doubleStepButton.disabled = true;
            runButton.disabled = true;
            resetButton.disabled = false;
        } else {
            stepButton.disabled = false;
            resetButton.disabled = false;
            doubleStepButton.disabled = !doubleStepAllowed;
            runButton.disabled = false;
        }
    }

    /**
     * Inserts the needed settings into the DOM. They will already have the necessary listeners added.
     */
    insertSettings() {
        const registerRepresentation = this.getRepresentationsSettingsRow(
            "Registers",
            "register-representation",
            (mode) => {
                this.regRepresentationMode = mode;
                this.updateUI();
            },
            this.regRepresentationMode
        );
        const memoryRepresentation = this.getRepresentationsSettingsRow(
            "Memory",
            "memory-representation",
            (mode) => {
                this.memRepresentationMode = mode;
                this.updateUI();
            },
            this.memRepresentationMode
        );
        this.domNodes.customSettingsContainer.appendChild(
            registerRepresentation
        );
        this.domNodes.customSettingsContainer.appendChild(memoryRepresentation);
    }

    /**
     * Generates a Node for selecting the representation (bin, udec, sdec, hex) of some setting.
     * Adds an event listener and calls the given function with the selected value (bin: 0, udec: 1, sdec: 3, hex: 2).
     * The listener will NOT cause a UI update.
     * The provided default mode will be used to check one option but it will not trigger the event listener.
     *
     * @param {string} displayName Name to display next to the buttons.
     * @param {string} id A unique id. Several ids will be generated from this base string.
     * @param {function(number):void} callback The function to call after a button was clicked.
     * @param {number} defaultMode The default representation mode.
     * @returns {Node} The Node to insert into the settings.
     */
    getRepresentationsSettingsRow(displayName, id, callback, defaultMode) {
        const row = createNode(html`<div class="row">
            <div class="col-4">
                <h3 class="fs-6">${displayName}:</h3>
            </div>
            <div id="${id}-container" class="col-8">
                <input
                    type="radio"
                    id="${id}-bin"
                    name="${id}-group"
                    value="0"
                    ${defaultMode == 0 ? "checked" : ""}
                />
                <label for="${id}-bin"> binary </label>
                <input
                    type="radio"
                    id="${id}-udec"
                    name="${id}-group"
                    value="1"
                    ${defaultMode == 1 ? "checked" : ""}
                />
                <label for="${id}-udec"> unsigned decimal </label>
                <input
                    type="radio"
                    id="${id}-sdec"
                    name="${id}-group"
                    value="3"
                    ${defaultMode == 3 ? "checked" : ""}
                />
                <label for="${id}-sdec"> signed decimal </label>
                <input
                    type="radio"
                    id="${id}-hex"
                    name="${id}-group"
                    value="2"
                    ${defaultMode == 2 ? "checked" : ""}
                />
                <label for="${id}-hex"> hexadecimal </label>
            </div>
        </div>`);
        row.querySelector(`#${id}-container`).addEventListener(
            "click",
            (event) => {
                // make sure the user actually clicked an option, not just somewhere in the container
                if (
                    event.target.matches("label") ||
                    event.target.matches("input")
                ) {
                    // the user might have clicked the label, but the value is only stored in the input
                    let selectedMode;
                    if (event.target.matches("label")) {
                        const inputId = event.target.getAttribute("for");
                        selectedMode = row.querySelector(`#${inputId}`).value;
                    } else {
                        selectedMode = event.target.value;
                    }
                    callback(Number(selectedMode));
                }
            }
        );
        return row;
    }

    /**
     * Starts calling this.step() in a loop until the simulation has finished,
     * or until this.doPause is true.
     */
    run() {
        this.isRunning = true;
        let stopCondition = () => {
            return (
                this.pythonSimulation.is_done() ||
                this.doPause ||
                this.error !== ""
            );
        };
        let stepLoop = () => {
            setTimeout(() => {
                for (let i = 0; i <= 1000; i++) {
                    this.step(false);
                }
                if (!stopCondition()) {
                    stepLoop();
                } else {
                    this.isRunning = false;
                    this.doPause = false;
                }
                this.updateUI();
            }, 25);
        };
        stepLoop();
    }

    /**
     * Sets this.pause so that this.run() will stop running the simulation.
     */
    pause() {
        if (this.isRunning) {
            this.doPause = true;
        }
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
        this.domNodes.outputField.innerText = str;
    }

    /**
     * Updates the values in the register table.
     */
    updateRegisters() {
        const registers = this.pythonSimulation.get_register_representations();
        this.domNodes.accu.innerText = registers
            .get("accu")
            .get(this.regRepresentationMode);
        this.domNodes.pc.innerText = registers
            .get("pc")
            .get(this.regRepresentationMode);
        this.domNodes.ir.innerText = registers
            .get("ir")
            .get(this.regRepresentationMode);
        registers.destroy();
    }

    /**
     * Clears the TOY memory table.
     */
    clearMemoryTable() {
        this.domNodes.memoryTableBody.innerHTML = "";
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
            const row = this.domNodes.memoryTableBody.insertRow();
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
     * Returns a Node containnig the accu and memory table and the output field.
     * The accu, pc, ir, memory table body and output field will be registered in this.domNodes.
     * @returns {Node} A Node containing the accu and memory table and the output field.
     */
    getMainColumn() {
        const column = createNode(html`<div
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
        this.domNodes.accu = column.querySelector("#toy-accu-id");
        this.domNodes.pc = column.querySelector("#toy-pc-id");
        this.domNodes.ir = column.querySelector("#toy-ir-id");
        this.domNodes.memoryTableBody = column.querySelector(
            "#toy-memory-table-body-id"
        );
        this.domNodes.outputField = column.querySelector("#output-field-id");
        return column;
    }

    /**
     * Returns a Node containing the double step button.
     * Also registers this node in this.domNodes.
     * @returns {Node} A Node containing the double step button.
     */
    getDoubleStepButton() {
        const button = createNode(html`<button
            id="button-double-step-simulation-id"
            class="btn btn-primary btn-sm control-button me-1"
            title="double step"
            onclick="simulation.doubleStep();"
        >
            <img src="img/double-step.svg" />
        </button>`);
        this.domNodes.doubleStepButton = button;
        return button;
    }

    /**
     * Inserts all of TOY's coustom elements into the DOM.
     */
    insertContentIntoDOM() {
        this.domNodes.textEditorSeparator.after(this.getMainColumn());
        this.domNodes.stepButton.after(this.getDoubleStepButton());
        this.domNodes.pageHeading.innerText = "TOY Simulator";
        document.title = "TOY Simulator";
        this.domNodes.helpModalBody.innerHTML = toyDocumentation;
        this.domNodes.helpModalHeading.textContent = "TOY";
        this.insertSettings();
    }

    /**
     * Removes all of TOY's custom elements from the DOM.
     */
    removeContentFromDOM() {
        document.getElementById("toy-main-text-container-id").remove();
        this.domNodes.doubleStepButton.remove();
        this.domNodes.helpModalBody.innerHTML = "";
        this.domNodes.helpModalHeading.textContent = "";
        this.domNodes.customSettingsContainer.innerHTML = "";
    }

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
