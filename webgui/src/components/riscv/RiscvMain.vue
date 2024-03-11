<!-- The main component for riscv. -->
<script setup>
import { onUnmounted, ref, watch, computed } from "vue";

import RiscvControlBar from "./RiscvControlBar.vue";
import CodeEditor from "../CodeEditor.vue";
import RiscvMemoryTable from "./RiscvMemoryTable.vue";
import RiscvRegistersOutput from "./RiscvRegistersOutput.vue";
import RiscvVisualization from "./RiscvVisualization.vue";
import CacheView from "./CacheView.vue";
// import SvgVisualization from '../SvgVisualization.vue';

import { useRiscvSimulationStore } from "@/js/riscv_simulation_store";
import fiveStageVisualizationPath from "/src/img/riscv_five_stage_pipeline.svg";
import singleStageVisualizationPath from "/src/img/riscv_single_stage_pipeline.svg";
import { riscvSettings } from "@/js/riscv_settings";
import { onMounted } from "vue";
import { ArchsimSplit } from "@/js/archsim-split";

const simulationStore = useRiscvSimulationStore();

// component refs
const mainContentContainer = ref(null);
const textContentContainer = ref(null);
const visualizationsContainer = ref(null);

// Holds the ArchsimSplit
let split = null;

// Values that are needed for controlling the split
const textContainerPopulated = computed(
    () =>
        riscvSettings.showInput.value ||
        riscvSettings.showMemory.value ||
        riscvSettings.showRegistersOutput.value
);

const visualizationsContainerPopulated = computed(
    () => riscvSettings.visContainerSelection.value !== "None"
);
const enableSplit = computed(
    () => textContainerPopulated.value && visualizationsContainerPopulated.value
);

// Creates or disables the split when enableSplit changes.
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

// Create an ArchsimSplit and activate it if desired.
onMounted(() => {
    split = new ArchsimSplit(
        mainContentContainer.value,
        textContentContainer.value,
        visualizationsContainer.value
    );
    if (enableSplit.value) {
        split.createSplit();
    }
});

// destroy the split when unmounting
onUnmounted(() => {
    split.destroyObject();
});
</script>

<template>
    <RiscvControlBar />

    <div
        ref="mainContentContainer"
        id="riscv-main-content-container"
        class="d-flex"
    >
        <div
            ref="textContentContainer"
            :class="textContainerPopulated ? 'd-flex flex-grow-1' : 'd-none'"
            id="riscv-text-content-container"
        >
            <CodeEditor
                class="editor"
                :simulation-store="simulationStore"
                isa-name="riscv"
                v-show="riscvSettings.showInput.value"
            />
            <RiscvMemoryTable
                class="memory"
                v-show="riscvSettings.showMemory.value"
            />
            <RiscvRegistersOutput
                class="reg-output"
                v-show="riscvSettings.showRegistersOutput.value"
            />
        </div>
        <div ref="visualizationsContainer" id="riscv-visualizations-container">
            <div
                class="processor-view-wrapper"
                v-if="riscvSettings.visContainerSelection.value == 'Processor'"
            >
                <RiscvVisualization
                    v-if="
                        riscvSettings.pipelineMode.value ===
                        'five_stage_pipeline'
                    "
                    :path="fiveStageVisualizationPath"
                    :simulation-store="simulationStore"
                />
                <RiscvVisualization
                    v-if="
                        riscvSettings.pipelineMode.value ===
                        'single_stage_pipeline'
                    "
                    :path="singleStageVisualizationPath"
                    :simulation-store="simulationStore"
                />
            </div>
            <div
                v-if="
                    riscvSettings.visContainerSelection.value ===
                        'Data Cache' ||
                    riscvSettings.visContainerSelection.value ===
                        'Instruction Cache'
                "
                class="cache-view-wrapper"
            >
                <CacheView
                    v-if="
                        riscvSettings.visContainerSelection.value ===
                        'Data Cache'
                    "
                    :cache-entries="simulationStore.dataCacheEntries"
                    :cache-settings="riscvSettings.dataCache.value"
                ></CacheView>
                <CacheView
                    v-if="
                        riscvSettings.visContainerSelection.value ===
                        'Instruction Cache'
                    "
                    :cache-entries="simulationStore.instructionCacheEntries"
                    :cache-settings="riscvSettings.instructionCache.value"
                ></CacheView>
            </div>
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
}

#riscv-visualizations-container {
    flex: 1 1 auto;
}

#riscv-text-content-container {
    gap: 1em;
    overflow: auto;
}

.processor-view-wrapper {
    height: 100%;
}

.cache-view-wrapper {
    height: 100%;
    overflow: auto;
}

.editor {
    min-width: 20em;
}

.memory,
.reg-output {
    flex: 0 0 auto;
    overflow: hidden;
}
</style>
