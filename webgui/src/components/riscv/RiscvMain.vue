<script setup>
import { onUnmounted, ref, watch, computed } from 'vue';

import RiscvControlBar from './RiscvControlBar.vue';
import RiscvDataMemory from './RiscvDataMemory.vue';
import RiscvInstructionMemory from './RiscvInstructionMemory.vue';
import RiscvUnifiedMemory from './RiscvUnifiedMemory.vue';
import RiscvRegisterTable from './RiscvRegisterTable.vue';
import CodeEditor from '../CodeEditor.vue';
import RiscvOutputField from './RiscvOutputField.vue';
import RiscvVisualization from './RiscvVisualization.vue';
// import SvgVisualization from '../SvgVisualization.vue';

import { useRiscvSimulationStore } from '@/js/riscv_simulation_store';
import fiveStageVisualizationPath from "/src/img/riscv_five_stage_pipeline.svg";
import singleStageVisualizationPath from "/src/img/riscv_single_stage_pipeline.svg";
import { riscvSettings } from '@/js/riscv_settings';
import { onMounted } from 'vue';
import { ArchsimSplit } from '@/js/archsim-split';

const simulationStore = useRiscvSimulationStore();

const mainContentContainer = ref(null);
const textContentContainer = ref(null);
const visualizationsContainer = ref(null);

let split = null;

const textContainerPopulated = computed(() => (riscvSettings.showInput.value || riscvSettings.showMemory.value || riscvSettings.showRegisters.value || riscvSettings.showOutput.value));
const enableSplit = computed(() => textContainerPopulated.value && riscvSettings.showVisualization.value);

watch(enableSplit, (enable) => {
    if (split === null) {
        return;
    }

    if (enable) {
        split.createSplit();
    } else {
        split.destroySplit();
    }
});

onMounted(() => {
    split = new ArchsimSplit(mainContentContainer.value, textContentContainer.value, visualizationsContainer.value);
    if (enableSplit.value) {
        split.createSplit();
    }
});

onUnmounted(() => {
    split.destroyObject();
})

</script>

<template>
    <RiscvControlBar />

    <div ref="mainContentContainer" id="riscv-main-content-container" class="d-flex">
        <div ref="textContentContainer" :class="textContainerPopulated ? 'd-flex flex-grow-1' : 'd-none'"
            id="riscv-text-content-container">
            <CodeEditor class="flex-grow-1 code-editor" :simulation-store="simulationStore" isa-name="riscv"
                v-show="riscvSettings.showInput.value" />
            <RiscvUnifiedMemory class="flex-shrink-0" v-show="riscvSettings.showMemory.value" />
            <!-- <RiscvInstructionMemory /> -->
            <RiscvRegisterTable class="flex-shrink-0" v-show="riscvSettings.showRegisters.value" />
            <!-- <RiscvDataMemory /> -->
            <RiscvOutputField class="flex-shrink-0" v-show="riscvSettings.showOutput.value" />
        </div>
        <div v-show="riscvSettings.showVisualization.value" ref="visualizationsContainer"
            id="riscv-visualizations-container">
            <RiscvVisualization v-if="riscvSettings.pipelineMode.value === 'five_stage_pipeline'"
                :path="fiveStageVisualizationPath" :simulation-store="simulationStore" />
            <RiscvVisualization v-if="riscvSettings.pipelineMode.value === 'single_stage_pipeline'"
                :path="singleStageVisualizationPath" :simulation-store="simulationStore" />
        </div>
    </div>
</template>

<style scoped>
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

.code-editor {
    min-width: 20em;
}
</style>
