/**
 * Base class for all simulation stores.
 *
 * Simulation stores are there to hold the data of their python counterparts
 * and to provide the functions for interacting with their python counterparts.
 */
export class BaseSimulationStore {
    /**
     * @param {PyodideInterface} pyodide The pyodide interface that will be used for interacting with the python code.
     * @param {function} simulationFactory A getter that will create a new python simulation object.
     */
    constructor(pyodide, simulationFactory) {
        /**
         * A getter that will create a new python simulation object.
         */
        this.simulationFactory = simulationFactory;
        /**
         * The pyodide interface that will be used for interacting with the python code.
         */
        this.pyodide = pyodide;
        /**
         * A PyProxy for the current python simulation object.
         */
        this.simulation = simulationFactory();
        /**
         * The performance metrics of the simulation. Contains linebreaks.
         */
        this.performanceMetricsStr = null;
        /**
         * Whether the simulation has finished (no more instructions to execute).
         */
        this.isDone = null;
        /**
         * Whether the simulation has started (at least one cycle was executed).
         */
        this.hasStarted = null;
        /**
         * Whether the simulation has loaded any instructions.
         */
        this.hasInstructions = null;
        /**
         * Signals that the simulation should pause. Only has meaning if the simulation
         * is currently running (executing the step loop).
         */
        this.doPause = null;
        /**
         * Whether the simulation is currently running (executing the step loop).
         */
        this.isRunning = false;
        /**
         * The last unresolved error. Will be a list. See the corresponding python function for more details.
         */
        this.error = null;
    }

    /**
     * Loads/parsed the given program.
     *
     * Successfully parsing the program will clear the last error.
     *
     * @param {String} text The program to laod.
     */
    loadProgram(text) {
        try {
            this.simulation.load_program(text);
            this.error = null;
        } catch (error) {
            this.updateLastPythonError();
        }
    }

    /**
     * Syncs all values from the python Simulation to this store object.
     *
     * This also calls some getter functions from python.
     *
     * It does not include things that arent properties of the python object,
     * like the last error (this.error).
     */
    syncAll() {
        this.isDone = this.simulation.is_done();
        this.hasStarted = this.simulation.has_started;
        this.hasInstructions = this.simulation.has_instructions();
        this.performanceMetricsStr =
            this.simulation.get_performance_metrics_str();
    }

    /**
     * Runs the simulation until it has finished.
     *
     * This doesn't call the python run method of the simulation object,
     * but instead it calls step several times and syncs the UI after that.
     * setTimeout is then used to allow the UI to update and to receive user input,
     * so that the user can pause the execution.
     *
     * Instead using a webworker might be a good idea, but we don't do that yet.
     */
    runSimulation() {
        this.isRunning = true;
        this.resumePerformanceTimer();

        /**
         *
         * @returns {bool} Whether to stop. Else the step loop shall be called again.
         */
        let stopCondition = () => {
            return this.simulation.is_done() || this.doPause;
        };

        /**
         * Calls step in a loop, syncs everything and then takes a quick
         * break with setTimeout.
         */
        let stepLoop = () => {
            setTimeout(() => {
                try {
                    for (let i = 0; i < 1000; i++) {
                        this.stepSimulation();
                    }
                    if (!stopCondition()) {
                        this.syncAll();
                        stepLoop();
                    } else {
                        this.stopPerformanceTimer();
                        this.doPause = false;
                        this.isRunning = false;
                        this.syncAll();
                    }
                } catch (error) {
                    this.stopPerformanceTimer();
                    this.syncAll();
                    this.updateLastPythonError();
                }
            }, 25);
        };
        stepLoop();
    }

    /**
     * Execute a single step of the simulation.
     */
    stepSimulation() {
        try {
            this.simulation.step();
        } catch (error) {
            this.updateLastPythonError();
        }
    }

    /**
     * Reset the python simulation and all variables that will not be
     * synced with syncAll (like this.error).
     */
    resetSimulation() {
        // temp is needed because pyodide won't let us reassign to a variable that holds a destroyed proxy, apparently.
        const temp = this.simulation;
        this.simulation = this.simulationFactory();
        temp.destroy();
        this.error = null;
    }

    /**
     * Signals the simulation to pause (stop the step loop/stop running).
     */
    pauseSimulation() {
        this.doPause = true;
    }

    /**
     * Resumes the timer of the performance metrics.
     */
    resumePerformanceTimer() {
        this.simulation.state.performance_metrics.resume_timer();
    }

    /**
     * Stops the timer of the performance metrics.
     */
    stopPerformanceTimer() {
        this.simulation.state.performance_metrics.stop_timer();
    }

    /**
     * Updates `this.error` with the last python error.
     */
    updateLastPythonError() {
        const getLastPythonError = this.pyodide.globals.get("get_last_error");
        this.error = this.toJsSafe(getLastPythonError());
    }

    /**
     * Converts the given proxy to a js object that is not linked to the original
     * python object anymore. Destroys all intermediary proxies and the given proxy
     * to prevent memory leaks.
     *
     * @param {PyProxy} proxy The proxy to be converted.
     * @returns {any} The converted proxy.
     */
    toJsSafe(proxy) {
        let pyproxies = [];
        const convertedProxy = proxy.toJs({ pyproxies });
        for (let px of pyproxies) {
            px.destroy();
        }
        proxy.destroy();
        return convertedProxy;
    }

    /**
     * Return true if there was a runtime error caused by the instruction at the given address.
     *
     * @param {Number} address Address of the instruction.
     *
     * @returns {bool}
     */
    instructionErrored(address) {
        return (
            this.error &&
            this.error[0] === "InstructionExecutionException" &&
            address === this.error[2]
        );
    }
}
