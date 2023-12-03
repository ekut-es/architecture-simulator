class ToySimulation {
    /**
     * Constructor for ToySimulation. Creates all the HTML Nodes and adds the needed event listeners.
     * @param {pyProxy} pythonSimulation pyProxy of a ToySimulation.
     * @param {object} domNodes Object holding all the relevant nodes from the default page.
     */
    constructor(pythonSimulation, domNodes) {
        /**@type {pyProxy} A pyProxy of the ToySimulation object.*/
        this.pythonSimulation = pythonSimulation;
        /**@type {object} An object holding all relevant DOM Nodes.*/
        this.domNodes = domNodes;

        /**@type {boolean} Whether the SVG element has finished loading.*/
        this.visualizationLoaded = false;
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
        /**SplitsJS object*/
        this.split = null;

        this.parseInput();
        /**@type{Function} Debounces (triggers) auto parsing.*/
        this.debouncedAutoParsing = this.getDebouncedAutoParsing();
        editor.on("change", () => {
            this.hasUnparsedChanges = true;
            this.debouncedAutoParsing();
            this.updateUI();
        });
        // Insert everything into the DOM. The SVG will cause a UI update once it has finished loading.
        this.domNodes = { ...this.domNodes, ...toyGetMainColumn() };
        this.domNodes.textEditorSeparator.after(this.domNodes.mainColumn);
        this.domNodes.doubleStepButton = toyGetDoubleStepButton();
        this.domNodes.stepButton.after(this.domNodes.doubleStepButton);
        this.domNodes.pageHeading.innerText = "TOY Simulator";
        document.title = "TOY Simulator";
        this.domNodes.helpModalBody.innerHTML = toyDocumentation;
        this.domNodes.helpModalHeading.textContent = "TOY";
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
        // Note: The constructor doesn't update the UI itself but the svg will once it has loaded
        const toySvgObject = toyGetVisualization(() => {
            this.domNodes.toyVisualization = toySvgObject.contentDocument;
            this.visualizationLoaded = true;
            this.updateUI();
        });
        this.domNodes.visualizationsContainer.append(toySvgObject);
        this.split = createSplit(
            this.domNodes.mainContentContainer,
            this.domNodes.textContentContainer,
            this.domNodes.visualizationsContainer
        );
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
        const input = editor.getValue(); // TODO: Replace by this.domNodes
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
     * Function for the step button.
     * Executes a single cycle of the simulation.
     * Sets this.error accordingly and updates the UI.
     * Does start and stop the timer for the performance metrics to meassure execution time.
     * Will not parse the input before stepping.
     */
    step() {
        this.pythonSimulation.get_performance_metrics().resume_timer();
        this.executeSingleStep();
        this.pythonSimulation.get_performance_metrics().stop_timer();
        this.updateUI();
    }

    /**
     * Executes a single cycle of the simulation.
     * Sets this.error accordingly.
     * Does not start and stop the timer for the performance metrics.
     * Will not update the UI.
     * Will not parse the input before stepping.
     */
    executeSingleStep() {
        try {
            this.pythonSimulation.single_step();
        } catch (error) {
            this.error = String(error);
        }
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
     * Starts calling this.step() in a loop until the simulation has finished,
     * or until this.doPause is true.
     */
    run() {
        this.isRunning = true;
        this.pythonSimulation.get_performance_metrics().resume_timer();
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
                    this.executeSingleStep();
                }
                if (!stopCondition()) {
                    stepLoop();
                } else {
                    this.isRunning = false;
                    this.doPause = false;
                    this.pythonSimulation
                        .get_performance_metrics()
                        .stop_timer();
                }
                this.updateUI();
            }, 25);
        };
        this.updateUI();
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
     * Removes all of TOY's custom elements from the DOM.
     */
    removeContentFromDOM() {
        document.getElementById("toy-main-text-container").remove();
        this.domNodes.doubleStepButton.remove();
        this.domNodes.helpModalBody.innerHTML = "";
        this.domNodes.helpModalHeading.textContent = "";
        this.domNodes.customSettingsContainer.innerHTML = "";
        this.domNodes.visualizationsContainer.innerHTML = "";
        this.destroySplit();
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
        this.domNodes.toyVisualization
            .querySelector("#" + id)
            .setAttribute("style", "fill: " + color);
    }

    /**
     * Sets the text content of an element.
     * @param {string} id target id.
     * @param {string} text text to set as the content of the element.
     */
    toySvgSetText(id, text) {
        this.domNodes.toyVisualization.querySelector("#" + id).textContent =
            text;
    }

    /**
     * Shows or hides an element.
     * @param {string} id target id.
     * @param {boolean} doShow Whether to show the element (display: block). Else it will be hidden (display: none)
     */
    toySvgShow(id, doShow) {
        const display = doShow ? "block" : "none";
        this.domNodes.toyVisualization.querySelector("#" + id).style.display =
            display;
    }

    /**
     * Removes the splits.
     */
    destroySplit() {
        if (this.split !== null) {
            this.domNodes.classList.remove("split");
            this.split.destroy();
            this.split = null;
        }
    }
}
