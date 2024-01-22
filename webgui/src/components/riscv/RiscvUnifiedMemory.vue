<script setup>

import { computed } from 'vue';

import RiscvCurrentInstructionArrow from './RiscvCurrentInstructionArrow.vue';

import { useRiscvSimulationStore } from '@/js/riscv_simulation_store';
import { riscvSettings } from '@/js/riscv_settings';

const simulationStore = useRiscvSimulationStore();

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

const isSingleStage = computed(() => riscvSettings.pipelineMode.value == 'single_stage_pipeline');
const isFiveStage = computed(() => riscvSettings.pipelineMode.value == 'five_stage_pipeline');

</script>

<template>
    <div>
        <span class="archsim-text-element-heading">Memory</span>
        <table class="table table-sm table-hover table-bordered archsim-mono-table mb-0">
            <thead>
                <tr>
                    <th>Address</th>
                    <th>Value</th>
                    <th v-if="isFiveStage">Stage</th>
                </tr>
            </thead>
            <tbody id="riscv-uni-memory-table-body">
                <template v-for="entry in simulationStore.instructionMemoryEntries">
                    <tr :class="{ 'archsim-tr-runtime-error': simulationStore.instructionErrored(entry[0]) }">
                        <td class="nowrap">
                            <RiscvCurrentInstructionArrow v-if="isSingleStage" :class="{hidden: entry[2] !== 'Single' }"/>
                            {{ entry[0] }}
                        </td>
                        <td> {{ entry[1] }}</td>
                        <td v-if="isFiveStage">
                            <span :class="['riscv-stage-indicator', 'riscv-stage-' + entry[2].toLowerCase()]">
                                {{ entry[2] }}
                            </span>
                        </td>
                    </tr>
                </template>
                <tr v-for="entry of dataMemoryEntries">
                    <td> {{ entry.hexAdress }} </td>
                    <td :class="{ highlight: entry.doHighlight }"> {{ entry.value }} </td>
                    <td></td>
                </tr>

            </tbody>
        </table>
    </div>
</template>

<style>
.hidden {
    visibility: hidden;
}

.nowrap {
    white-space: nowrap;
}

#riscv-uni-memory-table-body>tr>td:nth-child(1),
#riscv-uni-memory-table-body>tr>td:nth-child(2) {
    text-align: right;
}

.riscv-stage-indicator {
    color: white;
    font-weight: 500;
    padding: 0 0.2em;
    border-radius: 0.25em;
}

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
