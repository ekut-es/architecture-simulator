<!-- The memory table for data and instructions -->
<script setup>
import { computed } from 'vue';

import ToyCurrentInstructionArrow from './ToyCurrentInstructionArrow.vue';

import { toySettings } from '@/js/toy_settings';
import { useToySimulationStore } from '@/js/toy_simulation_store';

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
            doHighlight: simulationStore.hasStarted && entry[4]
        });
    }
    return result;
});

</script>

<template>
    <div class="mb-3" id="toy-memory-wrapper">
        <span class="archsim-text-element-heading">Memory</span>
        <table id="toy-memory-table" class="table table-sm table-hover table-bordered archsim-mono-table mb-0">
            <thead>
                <tr>
                    <th>Address</th>
                    <th>Value</th>
                    <th>Instruction</th>
                </tr>
            </thead>
            <tbody id="toy-memory-table-body">
                <tr v-for="entry in tableValues">
                    <td>
                        <ToyCurrentInstructionArrow v-if="entry.cycle"> {{ entry.cycle }} </ToyCurrentInstructionArrow>
                        {{ entry.hexAddress }}
                    </td>
                    <td :class="{ highlight: entry.doHighlight }"> {{ entry.value }} </td>
                    <td> {{ entry.instruction }} </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<style scoped>
.toy-current-cycle {
    padding: 0em 0.2em;
    border-radius: 0.3em;
    float: left;
}

#toy-memory-table th:first-child {
    width: 7em;
    min-width: 7em;
}

#toy-memory-wrapper {
    flex: 1 0 min(auto, 1em);
}

#toy-memory-table-body>tr>td:nth-child(1),
#toy-memory-table-body>tr>td:nth-child(2) {
    text-align: right;
}

.highlight {
    background-color: var(--highlight-color) !important;
}
</style>
