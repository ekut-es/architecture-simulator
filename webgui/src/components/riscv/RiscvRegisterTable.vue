<script setup>
import { computed } from 'vue';

import { useRiscvSimulationStore } from '@/js/riscv_simulation_store';
import { riscvSettings } from '@/js/riscv_settings';

const simulationStore = useRiscvSimulationStore();

const abiNames = ["zero", "ra", "sp", "gp", "tp", "t0", "t1", "t2", "s0/fp", "s1", "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11", "t3", "t4", "t5", "t6"];

const tableValues = computed(() => {
    const result = [];
    for (let i = 0; i < 32; i++) {
        const entry = simulationStore.registerEntries[i];
        result.push({
            abiName: abiNames[i],
            index: "x" + String(i),
            value: entry[0][riscvSettings.registerRepresentation.value],
            doHighlight: entry[1] && simulationStore.hasStarted
        });
    }
    return result;
});

</script>

<template>
    <div>
        <span class="archsim-text-element-heading">Registers</span>
        <table class="table table-sm table-hover table-bordered archsim-mono-table mb-0">
            <thead>
                <tr>
                    <th colspan="2">Register</th>
                    <th style="min-width: 5em;">Value</th>
                </tr>
            </thead>
            <tbody id="riscv-register-table-body">
                <tr v-for="entry of tableValues">
                    <td> {{ entry.abiName }} </td>
                    <td> {{ entry.index }}</td>
                    <td :class="{ highlight: entry.doHighlight }"> {{ entry.value }}</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<style scoped>
.highlight {
    background-color: var(--highlight-color) !important;
}

#riscv-register-table-body>tr>td:nth-child(2),
#riscv-register-table-body>tr>td:nth-child(3) {
    text-align: right;
}
</style>
