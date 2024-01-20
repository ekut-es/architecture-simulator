export class BaseSimulationStore {
    constructor(pyodide, simulationFactory) {
        this.simulationFactory = simulationFactory;
        this.pyodide = pyodide;
        this.simulation = simulationFactory();
        this.performanceMetricsStr = null;
        this.isDone = null;
        this.hasStarted = null;
        this.hasInstructions = null;
        this.doPause = null;
        this.isRunning = false;
        this.error = null;
    }

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
     * This also calls some getter functions from python.
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

    runSimulation() {
        this.isRunning = true;
        this.resumePerformanceTimer();
        let stopCondition = () => {
            return this.simulation.is_done() || this.doPause;
        };
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
        // temp is needed because pyodide won't let us reassign to a variable that holds a destroyed proxy
        const temp = this.simulation;
        this.simulation = this.simulationFactory();
        temp.destroy();
        this.error = null;
    }

    pauseSimulation() {
        this.doPause = true;
    }

    resumePerformanceTimer() {
        this.simulation.state.performance_metrics.resume_timer();
    }

    stopPerformanceTimer() {
        this.simulation.state.performance_metrics.stop_timer();
    }

    updateLastPythonError() {
        const getLastPythonError = this.pyodide.globals.get("get_last_error");
        this.error = this.toJsSafe(getLastPythonError());
    }

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
     * @param {String} address Address of the instruction. Will be casted to a number using Number(address),
     * so it may be a hex string starting with 0x.
     */
    instructionErrored(address) {
        return (
            this.error &&
            this.error[0] === "InstructionExecutionException" &&
            Number(address) === this.error[2]
        );
    }
}
