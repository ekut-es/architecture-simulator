<script setup>
import { onUnmounted, ref } from 'vue';

import RiscvControlBar from './RiscvControlBar.vue';
import RiscvMemoryTable from './RiscvMemoryTable.vue';
import RiscvRegisterTable from './RiscvRegisterTable.vue';
import RiscvInstructionTable from './RiscvInstructionTable.vue';
import CodeEditor from '../CodeEditor.vue';
import RiscvOutputField from './RiscvOutputField.vue';
import RiscvVisualization from './RiscvVisualization.vue';
// import SvgVisualization from '../SvgVisualization.vue';

import { useRiscvSimulationStore } from '@/js/riscv_simulation_store';
import fiveStageVisualizationPath from "/src/img/riscv_five_stage_pipeline.svg";
import singleStageVisualizationPath from "/src/img/riscv_single_stage_pipeline.svg";
import { riscvSettings } from '@/js/riscv_settings';
import { onMounted, watch } from 'vue';
import { ArchsimSplit } from '@/js/archsim-split';

const simulationStore = useRiscvSimulationStore();

const mainContentContainer = ref(null);
const textContentContainer = ref(null);
const visualizationsContainer = ref(null);

let split = null;

onMounted(() => {
    split = new ArchsimSplit(mainContentContainer.value, textContentContainer.value, visualizationsContainer.value);
    split.createSplit();
});

onUnmounted(() => {
    split.destroyObject();
})

</script>

<template>
    <RiscvControlBar />

    <div ref="mainContentContainer" id="riscv-main-content-container">
        <div ref="textContentContainer" class="d-flex justify-content-between" id="riscv-text-content-container">
            <CodeEditor :simulation-store="simulationStore" isa-name="riscv" />
            <RiscvInstructionTable />
            <RiscvRegisterTable />
            <RiscvMemoryTable />
            <RiscvOutputField />
        </div>
        <div ref="visualizationsContainer" id="riscv-visualizations-container">
            <RiscvVisualization v-if="riscvSettings.pipelineMode.value === 'five_stage_pipeline'" :path="fiveStageVisualizationPath"
                :simulation-store="simulationStore" />
            <RiscvVisualization v-if="riscvSettings.pipelineMode.value === 'single_stage_pipeline'" :path="singleStageVisualizationPath"
                :simulation-store="simulationStore" />
        </div>
    </div>
</template>

<style>
#riscv-main-content-container {
    flex: 1;
    min-height: 0;
}

#riscv-text-content-container,
#riscv-visualizations-container {
    padding: 1em;
    height: 100%;
    overflow-y: hidden;
}

#riscv-text-content-container>*:not(:last-child) {
    margin: 0 1em 0 0;
    overflow: auto;
}
</style>
