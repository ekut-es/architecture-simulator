class RiscvSimulation extends Simulation {
    constructor(pythonSimulation, domNodes) {
        super(pythonSimulation, domNodes);

        /**@type {Number} The selected representation mode for the registers. 0: bin, 1: udec, 2: hex, 3: sdec.*/
        this.regRepresentationMode = 1;
        /**@type {Number} The selected representation mode for the memory. 0: bin, 1: udec, 2: hex, 3: sdec.*/
        this.memRepresentationMode = 1;
        /**@type {?} The values of the memory from the last cycle.*/
        this.previousMemoryValues = [];

        this.domNodes = {
            ...this.domNodes,
            registerTable: getRiscvRegisterTable(),
            outputField: getRiscvOutputField(),
            ...getRiscvMemoryTable(),
            ...getRiscvInstructionTable(),
        };
        this.domNodes.textEditorSeparator.after(
            this.domNodes.instructionTable,
            this.domNodes.registerTable,
            this.domNodes.memoryTable,
            this.domNodes.outputField
        );

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

    /**
     * Updates the register table.
     */
    updateRegisterTable() {
        const valueRepresentations = (representations =
            this.pythonSimulation.register_file.reg_repr());
        for (let i = 0; i <= valueRepresentations.length; i++) {
            entry = valueRepresentations.get(i);
            const row = this.domNodes.memoryTable.children.item(i);
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
            this.pythonSimulation.memory.memory_wordwise_repr();
        for (const entry of valueRepresentations) {
            const address = entry.get(0);
            const values = entry.get(1);
            const value = values.get(this.memRepresentationMode);
            const row = this.domNodes.memoryTableBody.insertRow();
            const cell1 = row.insertCell();
            const cell2 = row.insertCell();
            cell1.innerText = address;
            cell2.innerText = value;
            if (this.previousMemoryValues[address] !== values[1]) {
                this.previousMemoryValues[address] = values[1];
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
            const address = entry[0];
            const instruction = entry[1];
            const stage = entry[2];
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
        if (this.visualizationLoaded) {
            this.updateVisualization();
        }

        if (this.error !== "") {
            stepButton.disabled = true;
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

    reset(pythonSimulation) {}

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
}
