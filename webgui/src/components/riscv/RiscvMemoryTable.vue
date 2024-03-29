<!-- A table that holds both instructions and data for RISC-V -->
<script setup>
import { computed } from "vue";

import CurrentInstructionArrow from "../CurrentInstructionArrow.vue";

import { useRiscvSimulationStore } from "@/js/riscv_simulation_store";
import { riscvSettings } from "@/js/riscv_settings";

const simulationStore = useRiscvSimulationStore();

// An array that we can nicely iterate over in the template
const dataMemoryEntries = computed(() => {
    const result = [];
    for (const entry of simulationStore.dataMemoryEntries) {
        result.push({
            hexAdress: entry[0][1],
            value: entry[1][riscvSettings.memoryRepresentation.value],
            doHighlight: simulationStore.hasStarted && entry[2],
        });
    }
    return result;
});

const instructionMemoryEntries = computed(() => {
    const result = [];
    for (const entry of simulationStore.instructionMemoryEntries) {
        result.push({
            hexAddress: entry[0][1],
            value: entry[1],
            stage: entry[2],
            error: simulationStore.instructionErrored(entry[0][0]),
        });
    }
    return result;
});
</script>

<template>
    <div class="wrapper">
        <span class="archsim-text-element-heading">Memory</span>

        <div class="table-wrapper">
            <table
                class="table table-sm table-hover table-bordered archsim-mono-table mb-0"
            >
                <thead>
                    <tr>
                        <th style="min-width: 9.5em">Address</th>
                        <th style="min-width: 10em">Value</th>
                    </tr>
                </thead>
                <tbody id="riscv-uni-memory-table-body">
                    <!-- Instruction memory entries -->
                    <template v-for="entry in instructionMemoryEntries">
                        <tr
                            :class="{
                                'archsim-tr-runtime-error': entry.error,
                            }"
                        >
                            <td class="text-nowrap">
                                <!-- Mark the current instruction/stage -->
                                <template v-if="entry.stage === 'Single'">
                                    <CurrentInstructionArrow />
                                </template>
                                <template v-else>
                                    <span
                                        :class="[
                                            'riscv-stage-indicator',
                                            'riscv-stage-' +
                                                entry.stage.toLowerCase(),
                                        ]"
                                        v-if="entry.stage"
                                    >
                                        {{ entry.stage }}
                                    </span>
                                </template>
                                <!-- The actual address -->
                                {{ entry.hexAddress }}
                            </td>
                            <td>{{ entry.value }}</td>
                        </tr>
                    </template>
                    <!-- Data memory entries -->
                    <tr v-for="entry of dataMemoryEntries">
                        <td>{{ entry.hexAdress }}</td>
                        <td
                            :class="[
                                { highlight: entry.doHighlight },
                                'text-end',
                            ]"
                        >
                            {{ entry.value }}
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<style scoped>
.wrapper {
    display: flex;
    flex-direction: column;
}

.table-wrapper {
    overflow-y: auto;
}
.highlight {
    background-color: var(--highlight-color) !important;
}

.nowrap {
    white-space: nowrap;
}

#riscv-uni-memory-table-body > tr > td:nth-child(1) {
    text-align: right;
}

.riscv-stage-indicator {
    color: white;
    font-weight: 500;
    padding: 0 0.2em;
    border-radius: 0.25em;
    float: left;
}

.riscv-stage-if {
    background-color: #ffbe0b;
    color: black !important;
}

.riscv-stage-id {
    background-color: #fb5607;
}

.riscv-stage-ex {
    background-color: #ff006e;
}

.riscv-stage-mem {
    background-color: #8338ec;
}

.riscv-stage-wb {
    background-color: #3a86ff;
}
</style>
