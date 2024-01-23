<!-- A table that holds both instructions and data for RISC-V -->
<script setup>

import { computed } from 'vue';

import RiscvCurrentInstructionArrow from './RiscvCurrentInstructionArrow.vue';

import { useRiscvSimulationStore } from '@/js/riscv_simulation_store';
import { riscvSettings } from '@/js/riscv_settings';

const simulationStore = useRiscvSimulationStore();

// An array that we can nicely iterate over in the template
const dataMemoryEntries = computed(() => {
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

/**
 * Whether the five stage pipeline is currently enabled.
 */
const isFiveStage = computed(() => riscvSettings.pipelineMode.value == 'five_stage_pipeline');

</script>

<template>
    <div>
        <span class="archsim-text-element-heading">Memory</span>
        <table class="table table-sm table-hover table-bordered archsim-mono-table mb-0">
            <thead>
                <tr>
                    <th style="min-width: 8.25em">Address</th>
                    <th style="min-width: 10em">Value</th>
                    <!-- An extra column to indicate the stage, but only in case of five stage pipeline -->
                    <th v-if="isFiveStage">Stage</th>
                </tr>
            </thead>
            <tbody id="riscv-uni-memory-table-body">
                <!-- Instruction memory entries -->
                <template v-for="entry in simulationStore.instructionMemoryEntries">
                    <tr :class="{ 'archsim-tr-runtime-error': simulationStore.instructionErrored(entry[0]) }">
                        <td class="text-nowrap">
                            <!-- Mark the current instruction in case of single stage -->
                            <RiscvCurrentInstructionArrow v-if="entry[2] === 'Single'"/>
                            {{ entry[0] }}
                        </td>
                        <td> {{ entry[1] }}</td>
                        <!-- Stage indicator in case of five stage pipeline -->
                        <td v-if="isFiveStage">
                            <span :class="['riscv-stage-indicator', 'riscv-stage-' + entry[2].toLowerCase()]">
                                {{ entry[2] }}
                            </span>
                        </td>
                    </tr>
                </template>
                <!-- Data memory entries -->
                <tr v-for="entry of dataMemoryEntries">
                    <td> {{ entry.hexAdress }} </td>
                    <td :class="[{ highlight: entry.doHighlight }, 'text-end']"> {{ entry.value }} </td>
                    <td v-if="isFiveStage"></td>
                </tr>

            </tbody>
        </table>
    </div>
</template>

<style scoped>
.highlight {
    background-color: var(--highlight-color) !important;
}

.nowrap {
    white-space: nowrap;
}

#riscv-uni-memory-table-body>tr>td:nth-child(1) {
    text-align: right;
}

.riscv-stage-indicator {
    color: white;
    font-weight: 500;
    padding: 0 0.2em;
    border-radius: 0.25em;
}
</style>

<style>
.riscv-stage-if {
    background-color: #ffbe0b;
    color: black;
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
