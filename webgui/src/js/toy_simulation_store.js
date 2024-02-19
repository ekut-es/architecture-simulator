import { reactive } from "vue";
import { BaseSimulationStore } from "./base_simulation_store";

let pyodide = null;

/**
 * Sets the local pyodide variable. Needed for creating ToySimulationStores.
 * @param {PyodideInterface} newPyodide The pyodide interface to use.
 */
export function setPyodide(newPyodide) {
    pyodide = newPyodide;
}

let toySimulationStore = null;

/**
 * Returns the singleton instance of the toy simulation store.
 * @returns {ToySimulationStore} Always returns the same reactive instance of the toy simulation store.
 */
export function useToySimulationStore() {
    if (toySimulationStore === null) {
        toySimulationStore = new ToySimulationStore(pyodide);
        toySimulationStore.syncAll();
    }
    return reactive(toySimulationStore);
}

/**
 * The TOY simulation store for interacting with the toy python simulation.
 */
export class ToySimulationStore extends BaseSimulationStore {
    /**
     * @param {PyodideInterface} pyodide The pyodide interface for interacting with python.
     */
    constructor(pyodide) {
        super(pyodide, pyodide.globals.get("get_toy_simulation"));
        this.registerTableEntries = [];
        this.memoryTableEntries = [];
        /**
         * The memory entries from the last synchronization. Used for determining and highlighting
         * changed entries.
         */
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
            const hexAddress = entry[0][1];
            const newValue = entry[1][1];
            const hasChanged =
                newValue !== this.previousMemoryEntries[hexAddress];
            entry.push(hasChanged);
            newPreviousMemoryEntries[hexAddress] = newValue;
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

    /**
     * Executes a single step (a single cycle, half an instruction) of the simulation.
     */
    stepSimulation() {
        try {
            this.simulation.single_step();
        } catch (error) {
            this.updateLastPythonError();
        }
    }

    /**
     * Executes two steps (two cycles, a full instruction) of the simulation.
     */
    doubleStepSimulation() {
        try {
            this.simulation.step();
        } catch (error) {
            this.updateLastPythonError();
        }
    }
}
