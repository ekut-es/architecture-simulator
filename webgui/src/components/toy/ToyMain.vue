<!-- The main component for TOY. -->
<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from "vue";

import ToyControlBar from "./ToyControlBar.vue";
import CodeEditor from "../CodeEditor.vue";
import SvgVisualization from "../SvgVisualization.vue";

import { ArchsimSplit } from "@/js/archsim-split";
import { useToySimulationStore } from "@/js/toy_simulation_store";
import svgPath from "/src/img/toy_structure.svg";
import { toySettings } from "@/js/toy_settings";
import ToyMemoryTable from "./ToyMemoryTable.vue";
import ToyRegistersOutput from "./ToyRegistersOutput.vue";

const simulationStore = useToySimulationStore();

// component refs
const mainContentContainer = ref(null);
const textContentContainer = ref(null);
const visualizationsContainer = ref(null);

// Holds the ArchsimSplit
let split = null;

// Values that are needed for controlling the split
const textContainerPopulated = computed(
    () =>
        toySettings.showInput.value ||
        toySettings.showMemory.value ||
        toySettings.showRegistersOutput.value
);

const enableSplit = computed(
    () => textContainerPopulated.value && toySettings.showVisualization.value
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
    <ToyControlBar />

    <div
        ref="mainContentContainer"
        id="toy-main-content-container"
        class="d-flex"
    >
        <div
            ref="textContentContainer"
            id="toy-text-content-container"
            :class="textContainerPopulated ? 'd-flex flex-grow-1' : 'd-none'"
        >
            <CodeEditor
                class="editor"
                :simulation-store="simulationStore"
                isa-name="toy"
                v-show="toySettings.showInput.value"
            />
            <ToyMemoryTable
                class="memory"
                v-show="toySettings.showMemory.value"
            />
            <ToyRegistersOutput
                class="reg-output"
                v-show="toySettings.showRegistersOutput.value"
            />
        </div>
        <div
            v-show="toySettings.showVisualization.value"
            ref="visualizationsContainer"
            id="toy-visualizations-container"
        >
            <SvgVisualization
                :simulation-store="simulationStore"
                :path="svgPath"
            />
        </div>
    </div>
</template>

<style scoped>
#toy-main-content-container {
    flex: 1;
    min-height: 0;
}

#toy-text-content-container,
#toy-visualizations-container {
    padding: 1em;
    height: 100%;
}

#toy-text-content-container {
    overflow: hidden;
    gap: 1em;
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
