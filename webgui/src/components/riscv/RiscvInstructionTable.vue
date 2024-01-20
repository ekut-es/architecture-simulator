<script setup>

import RiscvCurrentInstructionArrow from './RiscvCurrentInstructionArrow.vue';

import { useRiscvSimulationStore } from '@/js/riscv_simulation_store';
import { riscvSettings } from '@/js/riscv_settings';

const simulationStore = useRiscvSimulationStore();

</script>

<template>
    <div>
        <span class="archsim-text-element-heading">Instructions</span>
        <table class="table table-sm table-hover table-bordered archsim-mono-table mb-0">
            <thead>
                <tr>
                    <th>Address</th>
                    <th>Instruction</th>
                    <th v-if="riscvSettings.pipelineMode.value === 'five_stage_pipeline'">Stage</th>
                </tr>
            </thead>
            <tbody id="riscv-instruction-table-body">
                <template v-for="entry in simulationStore.instructionMemoryEntries">
                    <tr :class="{ 'archsim-tr-runtime-error': simulationStore.instructionErrored(entry[0]) }">
                        <td>
                            <RiscvCurrentInstructionArrow v-if="entry[2] === 'Single'" />{{ entry[0] }}
                        </td>
                        <td> {{ entry[1] }}</td>
                        <td v-if="riscvSettings.pipelineMode.value === 'five_stage_pipeline'"> <span
                                :class="['riscv-stage-indicator', 'riscv-stage-' + entry[2].toLowerCase()]"> {{ entry[2] }}
                            </span> </td>
                    </tr>
                </template>

            </tbody>
        </table>
    </div>
</template>

<style>
#riscv-instruction-table-body>tr>td:nth-child(1) {
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
