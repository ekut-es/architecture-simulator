<!-- The memory table for data and instructions -->
<script setup>
import { computed } from "vue";

import CurrentInstructionArrow from "../CurrentInstructionArrow.vue";

import { toySettings } from "@/js/toy_settings";
import { useToySimulationStore } from "@/js/toy_simulation_store";

const simulationStore = useToySimulationStore();

// An array that we can nicely iteratve over in the template
const tableValues = computed(() => {
    let result = [];
    for (const entry of simulationStore.memoryEntries) {
        result.push({
            hexAddress: entry[0][1],
            value: entry[1][toySettings.memoryRepresentation.value],
            instruction: entry[2],
            cycle: entry[3],
            doHighlight: simulationStore.hasStarted && entry[4],
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
                        <th style="min-width: 7em">Address</th>
                        <th>Value</th>
                        <th>Instruction</th>
                    </tr>
                </thead>
                <tbody id="toy-memory-table-body">
                    <tr v-for="entry in tableValues">
                        <td>
                            <CurrentInstructionArrow v-if="entry.cycle">
                                {{ entry.cycle }}
                            </CurrentInstructionArrow>
                            {{ entry.hexAddress }}
                        </td>
                        <td :class="{ highlight: entry.doHighlight }">
                            {{ entry.value }}
                        </td>
                        <td>{{ entry.instruction }}</td>
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

#toy-memory-table-body > tr > td:nth-child(1),
#toy-memory-table-body > tr > td:nth-child(2) {
    text-align: right;
}
</style>
