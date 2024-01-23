import { reactive } from "vue";

import { BaseSimulationStore } from "./base_simulation_store";
import { riscvSettings } from "./riscv_settings";

let pyodide = null;

export function setPyodide(newPyodide) {
    pyodide = newPyodide;
}

let riscvSimulationStore = null;

/**
 * Returns the singleton instance of the riscv simulation store.
 * @returns {RiscvSimulationStore} Always returns the same reactive instance of the riscv simulation store.
 */
export function useRiscvSimulationStore() {
    if (riscvSimulationStore === null) {
        riscvSimulationStore = new RiscvSimulationStore(pyodide);
        riscvSimulationStore.syncAll();
    }
    return reactive(riscvSimulationStore);
}

export class RiscvSimulationStore extends BaseSimulationStore {
    constructor(pyodide) {
        const getRiscvSimulation = pyodide.globals.get("get_riscv_simulation");
        super(pyodide, () =>
            getRiscvSimulation(
                riscvSettings.pipelineMode.value,
                riscvSettings.dataHazardDetection.value
            )
        );
        this.registerEntries = [];
        this.dataMemoryEntries = [];
        this.previousDataMemoryEntries = [];
        this.instructionMemoryEntries = [];
        this.svgDirectives = [];
    }
    /**
     * Syncs the memory table entries.
     * Also keeps track of which entries have changed.
     */
    syncDataMemoryEntries() {
        let newDataMemoryEntries = this.toJsSafe(
            this.simulation.get_data_memory_entries()
        );
        let newPreviousDataMemoryEntries = [];
        for (const entry of newDataMemoryEntries) {
            const intAddress = entry[0][0];
            const newValue = entry[1][1];
            const hasChanged =
                newValue !== this.previousDataMemoryEntries[intAddress];
            entry.push(hasChanged);
            newPreviousDataMemoryEntries[intAddress] = newValue;
        }
        this.previousDataMemoryEntries = newPreviousDataMemoryEntries;
        this.dataMemoryEntries = newDataMemoryEntries;
    }
    /**
     * Syncs the registers.
     * Also keeps track of which entries have changed.
     */
    syncRegisterEntries() {
        const newRegisterEntries = this.toJsSafe(
            this.simulation.get_register_entries()
        );
        for (let i = 0; i < newRegisterEntries.length; i++) {
            const newValue = newRegisterEntries[i][1];
            const hasChanged =
                !(i in this.registerEntries) ||
                newValue !== this.registerEntries[i][0][1];
            newRegisterEntries[i] = [newRegisterEntries[i], hasChanged];
        }
        this.registerEntries = newRegisterEntries;
    }
    /**
     * Syncs the instruction memory entries.
     */
    syncInstructionMemoryEntries() {
        this.instructionMemoryEntries = this.toJsSafe(
            this.simulation.get_instruction_memory_entries()
        );
    }
    /**
     * Syncs the svg directives.
     */
    syncSvgDirectives() {
        if (riscvSettings.pipelineMode.value === "five_stage_pipeline") {
            this.svgDirectives = this.toJsSafe(
                this.simulation.get_riscv_five_stage_svg_update_values()
            );
        } else if (
            riscvSettings.pipelineMode.value == "single_stage_pipeline"
        ) {
            this.svgDirectives = this.toJsSafe(
                this.simulation.get_riscv_single_stage_svg_update_values()
            );
        }
    }
    syncAll() {
        this.syncRegisterEntries();
        this.syncDataMemoryEntries();
        this.syncInstructionMemoryEntries();
        this.syncSvgDirectives();
        super.syncAll();
    }
}
