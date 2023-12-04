class ToySimulation extends Simulation {
    constructor(pythonSimulation, domNodes) {
        super(pythonSimulation, domNodes);
        /**@type {Number} The selected representation mode for the registers. 0: bin, 1: udec, 2: hex, 3: sdec.*/
        this.regRepresentationMode = 1;
        /**@type {Number} The selected representation mode for the memory. 0: bin, 1: udec, 2: hex, 3: sdec.*/
        this.memRepresentationMode = 1;
        /**@type {?} The values of the memory from the last cycle.*/
        this.previousMemoryValues = [];

        // Insert everything into the DOM. The SVG will cause a UI update once it has finished loading.
        this.domNodes = { ...this.domNodes, ...toyGetMainColumn() };
        this.domNodes.textEditorSeparator.after(this.domNodes.mainColumn);
        this.domNodes.doubleStepButton = toyGetDoubleStepButton();
        this.domNodes.stepButton.after(this.domNodes.doubleStepButton);
        const registerRepresentation = getRepresentationsSettingsRow(
            "Registers",
            "register-representation",
            (mode) => {
                this.regRepresentationMode = mode;
                this.updateUI();
            },
            this.regRepresentationMode
        );
        const memoryRepresentation = getRepresentationsSettingsRow(
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

    getIsaName() {
        return "TOY";
    }

    getDocumentation() {
        return toyDocumentation;
    }

    supportsVisualization() {
        return true;
    }

    getPathToVisualization() {
        return "img/toy_structure.svg";
    }

    reset(pythonSimulation) {
        this.previousMemoryValues = [];
        super.reset(pythonSimulation);
    }

    removeContentFromDOM() {
        this.domNodes.mainColumn.remove();
        this.domNodes.doubleStepButton.remove();
        super.removeContentFromDOM();
    }

    setOutputFieldContent(str) {
        this.domNodes.outputField.innerText = str;
    }

    /**
     * Function for the double step button.
     * Executes two cycles of the simulation.
     * Should only be called if the next cycle to be executed is the first cycle of the current instruction,
     * otherwise it will create an error.
     * Sets this.error accordingly and updates the UI.
     * Does start and stop the timer for the performance metrics to meassure execution time.
     * Will not parse the input before stepping.
     */
    doubleStep() {
        this.pythonSimulation.get_performance_metrics().resume_timer();
        this.executeDoubleStep();
        this.pythonSimulation.get_performance_metrics().stop_timer();
        this.updateUI();
    }

    /**
     * Executes two cycles of the simulation.
     * Should only be called if the next cycle to be executed is the first cycle of the current instruction,
     * otherwise it will create an error.
     * Sets this.error accordingly.
     * Does not start and stop the timer for the performance metrics.
     * Will not update the UI.
     * Will not parse the input before stepping.
     */
    executeDoubleStep() {
        try {
            this.pythonSimulation.step();
        } catch (error) {
            this.error = String(error);
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
        if (this.visualizationLoaded) {
            this.updateVisualization();
        }
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
     * Updates the values in the register table.
     */
    updateRegisters() {
        const registers = this.pythonSimulation.get_register_representations();
        const regmode = this.regRepresentationMode;
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
            values.destroy();
            entry.destroy();
        }
        valueRepresentations.destroy();
    }

    updateVisualization() {
        const updateValues = this.pythonSimulation.get_toy_svg_update_values();
        for (let i = 0; i < updateValues.length; i++) {
            const update = updateValues.get(i);
            const id = update.get(0);
            const action = update.get(1);
            const value = update.get(2);
            switch (action) {
                case "highlight":
                    this.toySvgHighlight(id, value);
                    break;
                case "write":
                    this.toySvgSetText(id, value);
                    break;
                case "show":
                    this.toySvgShow(id, value);
                    break;
            }
            update.destroy();
        }
        updateValues.destroy();
    }

    /**
     * Sets the fill color of an element.
     * @param {string} id target id.
     * @param {string} color hex color string.
     */
    toySvgHighlight(id, color) {
        this.domNodes.visualization
            .querySelector("#" + id)
            .setAttribute("style", "fill: " + color);
    }

    /**
     * Sets the text content of an element.
     * @param {string} id target id.
     * @param {string} text text to set as the content of the element.
     */
    toySvgSetText(id, text) {
        this.domNodes.visualization.querySelector("#" + id).textContent = text;
    }

    /**
     * Shows or hides an element.
     * @param {string} id target id.
     * @param {boolean} doShow Whether to show the element (display: block). Else it will be hidden (display: none)
     */
    toySvgShow(id, doShow) {
        const display = doShow ? "block" : "none";
        this.domNodes.visualization.querySelector("#" + id).style.display =
            display;
    }
}
