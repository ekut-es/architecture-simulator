import { ArchsimSplit, createVisualization } from "./util.js";
import { setEditorReadOnly, setEditorOnChangeListener } from "./editor.js";

export class Simulation {
    /**
     * Constructor for Simulation.
     * @param {object} domNodes Object holding all the relevant nodes from the default page.
     */
    constructor(domNodes, getLastPythonError) {
        /**@type {pyProxy} A pyProxy of the ToySimulation object.*/
        this.pythonSimulation = null;
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
        /**@type {pyProxy} The latest error.*/
        this.error = null;
        /**Object for managing the splitjs instance**/
        this.split = new ArchsimSplit();

        this.getLastPythonError = getLastPythonError;

        /**@type{Function} Debounces (triggers) auto parsing.*/
        this.debouncedAutoParsing = this.getDebouncedAutoParsing();
        setEditorReadOnly(false);
        setEditorOnChangeListener(() => {
            this.hasUnparsedChanges = true;
            this.debouncedAutoParsing();
            this.updateUI();
        });
        this.domNodes.pageHeading.innerText = this.getIsaName() + " Simulator";
        document.title = this.getIsaName() + " Simulator";
        this.domNodes.helpModalBody.innerHTML = this.getDocumentation();
        this.domNodes.helpModalHeading.textContent = this.getIsaName();
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
     * Should be implemented by all subclasses.
     * Resets the entire simulation.
     * You should also call this.resetBase(pythonSimulation).
     * You will need to create the pythonSimulation on you own if you need one (see js/initialize_simulators.js).
     */
    resetCustom() {}

    /**
     * Resets the entire simulation. Updates the UI.
     */
    reset() {
        this.error = null;
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
        this.split.destroySplit();
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
     * Activates the visualization and inserts it into the DOM.
     * this.getPathToVisualization must be implemented for this to work.
     * Will also create a Split. Calls updateUI once the visualization has finished loading.
     * Also sets this.visualizationLoaded = true one it has loaded.
     */
    activateVisualization() {
        const svgObject = createVisualization(
            this.getPathToVisualization(),
            () => {
                this.domNodes.visualization = svgObject.contentDocument;
                this.visualizationLoaded = true;
                this.updateUI();
            }
        );
        this.domNodes.visualizationsContainer.append(svgObject);
        this.split.createSplit(
            this.domNodes.mainContentContainer,
            this.domNodes.textContentContainer,
            this.domNodes.visualizationsContainer
        );
    }

    /**
     * Removes the split, deactivates the visualization, removes it from the DOM.
     * Also sets this.visualizationLoaded = false and calls this.updateUI().
     */
    deactivateVisualization() {
        this.domNodes.visualizationsContainer.innerHTML = "";
        this.split.destroySplit();
        delete this.domNodes.visualization;
        this.visualizationLoaded = false;
        this.updateUI();
    }

    /**
     * Parses and loads the content of the input field into the simulation.
     * Sets the error attribute accordingly.
     *
     * @returns {boolean} Whether parsing the input was successful
     */
    parseInput() {
        const input = this.domNodes.editor.state.doc.toString();
        this.hasUnparsedChanges = false;
        try {
            this.pythonSimulation.load_program(input);
            this.error = null;
            return true;
        } catch (err) {
            this.error = this.getLastPythonError();
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
            this.error = this.getLastPythonError();
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
                this.error !== null
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
     * Highlights a line in the text editor and displays an error message as a hint.
     * Can be used to display parser exceptions.
     *
     * @param {number} position - line number (starting at 1).
     * @param {string} errorMessage - string to display.
     */
    // highlightEditorLine(position, errorMessage) {
    //     this.domNodes.editor.addLineClass(position - 1, "background", "highlight");
    //     this.domNodes.editor.refresh();
    //     const error_description = {
    //         hint: function () {
    //             return {
    //                 from: position,
    //                 to: position,
    //                 list: [errorMessage, ""],
    //             };
    //         },
    //         customKeys: {
    //             Up: function (cm, handle) {
    //                 CodeMirror.commands.goLineUp(cm);
    //                 handle.close();
    //             },
    //             Down: function (cm, handle) {
    //                 CodeMirror.commands.goLineDown(cm);
    //                 handle.close();
    //             },
    //         },
    //     };
    //     this.domNodes.editor.showHint(error_description);
    // }

    /**
     * Removes all highlights from the editor.
     */
    // removeEditorHighlights() {
    //     for (let line of this.domNodes.editor.state.doc.iterLines) {
    //         this.domNodes.editor.removeLineClass(i, "background", "highlight");
    //     }
    //     this.domNodes.editor.refresh();
    //     this.domNodes.editor.closeHint();
    // }
}
