class Simulation {
    /**
     * Constructor for Simulation.
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
        this.domNodes.pageHeading.innerText = this.getIsaName() + " Simulator";
        document.title = this.getIsaName() + " Simulator";
        this.domNodes.helpModalBody.innerHTML = this.getDocumentation();
        this.domNodes.helpModalHeading.textContent = this.getIsaName();

        if (this.supportsVisualization()) {
            const svgObject = createVisualization(
                this.getPathToVisualization(),
                () => {
                    this.domNodes.visualization = svgObject.contentDocument;
                    this.visualizationLoaded = true;
                    this.updateUI();
                }
            );
            this.domNodes.visualizationsContainer.append(svgObject);
            this.split = createSplit(
                this.domNodes.mainContentContainer,
                this.domNodes.textContentContainer,
                this.domNodes.visualizationsContainer
            );
        }
    }

    /**
     * @returns {str} Name of the ISA.
     */
    getIsaName() {}

    /**
     * @returns {str} Documentation for the help page.
     */
    getDocumentation() {}

    /**
     * Updates all elements in the DOM based on the object's properties.
     */
    updateUI() {}

    /**
     * Resets the entire simulation. Updates the UI. Takes a
     * pyproxy Simulation Object because we don't reset those,
     * we just create new ones.
     * @param {pyProxy} pythonSimulation python Simulation object
     */
    reset(pythonSimulation) {
        this.pythonSimulation = pythonSimulation;
        this.error = "";
        this.parseInput();
        this.updateUI();
    }

    /**
     * Removes all the ISA specific content from the DOM (undoes all the changes it made).
     */
    removeContentFromDOM() {
        this.domNodes.helpModalBody.innerHTML = "";
        this.domNodes.helpModalHeading.textContent = "";
        this.domNodes.customSettingsContainer.innerHTML = "";
        this.domNodes.visualizationsContainer.innerHTML = "";
        this.destroySplit();
    }

    /**
     * @returns {boolean} Whether the ISA supports a visualization or not.
     */
    supportsVisualization() {
        return false;
    }

    /**
     * @returns {str} The path to the visualization SVG file.
     */
    getPathToVisualization() {}

    /**
     * @param {string} str The string that the output field's content will be set to.
     */
    setOutputFieldContent(str) {}

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
        this.executeStep();
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
    executeStep() {
        try {
            this.pythonSimulation.step();
        } catch (error) {
            this.error = String(error);
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
                    this.executeStep();
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
     * Removes the splits.
     */
    destroySplit() {
        if (this.split !== null) {
            this.domNodes.mainContentContainer.classList.remove("split");
            this.split.destroy();
            this.split = null;
        }
    }
}
