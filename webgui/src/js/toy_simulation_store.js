import { reactive } from "vue";
import { BaseSimulationStore } from "./base_simulation_store";

let pyodide = null;

export function setPyodide(newPyodide) {
    pyodide = newPyodide;
}

let toySimulationStore = null;

export function useToySimulationStore() {
    if (toySimulationStore === null) {
        toySimulationStore = new ToySimulationStore(pyodide);
        toySimulationStore.syncAll();
    }
    return reactive(toySimulationStore);
}

export class ToySimulationStore extends BaseSimulationStore {
    constructor(pyodide) {
        super(pyodide, pyodide.globals.get("get_toy_simulation"));
        this.registerTableEntries = [];
        this.memoryTableEntries = [];
        this.previousMemoryTableEntries = [];
        this.nextCycle = null;
        this.svgDirectives = [];
    }
    /**
     * Syncs the memory table entries.
     */
    syncMemoryTableEntries() {
        let newMemoryEntries = this.toJsSafe(
            this.simulation.get_memory_table_entries()
        );
        let newPreviousMemoryEntries = [];
        for (const entry of newMemoryEntries) {
            const intAddress = entry[0][0];
            const newValue = entry[1][1];
            const hasChanged =
                newValue !== this.previousMemoryEntries[intAddress];
            entry.push(hasChanged);
            newPreviousMemoryEntries[intAddress] = newValue;
        }
        this.previousMemoryEntries = newPreviousMemoryEntries;
        this.memoryEntries = newMemoryEntries;
    }
    /**
     * Syncs the registers.
     */
    syncRegisters() {
        this.registerTableEntries = this.toJsSafe(
            this.simulation.get_register_representations()
        );
    }
    /**
     * Syncs the svg directives.
     */
    syncSvgDirectives() {
        this.svgDirectives = this.toJsSafe(
            this.simulation.get_toy_svg_update_values()
        );
    }
    syncAll() {
        this.syncRegisters();
        this.syncMemoryTableEntries();
        this.syncSvgDirectives();
        this.nextCycle = this.simulation.next_cycle;
        super.syncAll();
    }
    stepSimulation() {
        try {
            this.simulation.single_step();
        } catch (error) {
            this.updateLastPythonError();
        }
    }
    doubleStepSimulation() {
        try {
            this.simulation.step();
        } catch (error) {
            this.updateLastPythonError();
        }
    }
}
