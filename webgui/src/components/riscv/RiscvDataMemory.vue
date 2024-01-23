<!-- Data memory table for Riscv. Will probably be replaced by RiscvUnifiedMemory.vue -->
<script setup>
import { computed } from 'vue';

import { useRiscvSimulationStore } from '@/js/riscv_simulation_store';
import { riscvSettings } from '@/js/riscv_settings';

const simulationStore = useRiscvSimulationStore();

const tableValues = computed(() => {
    const result = [];
    for (const entry of simulationStore.dataMemoryEntries) {
        result.push({
            hexAdress: entry[0][1],
            value: entry[1][riscvSettings.memoryRepresentation.value],
            doHighlight: simulationStore.hasStarted && entry[2]
        });
    }
    return result;
});
</script>

<template>
    <div>
        <span class="archsim-text-element-heading">Memory</span>
        <table class="table table-sm table-hover table-bordered archsim-mono-table mb-0">
            <thead>
                <tr>
                    <th>Address</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody id="riscv-memory-table-body">
                <tr v-for="entry of tableValues">
                    <td> {{ entry.hexAdress }} </td>
                    <td :class="{ highlight: entry.doHighlight }"> {{ entry.value }} </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<style scoped>
#riscv-memory-table-body>tr>td:nth-child(1),
#riscv-memory-table-body>tr>td:nth-child(2) {
    text-align: right;
}

.highlight {
    background-color: var(--highlight-color) !important;
}
</style>
