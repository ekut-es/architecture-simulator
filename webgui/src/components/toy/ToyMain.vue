<script setup>

import { ref, onMounted, onUnmounted, computed, watch } from 'vue';

import ToyControlBar from './ToyControlBar.vue';
import ToyMainTextContainer from './ToyMainTextContainer.vue';
import CodeEditor from '../CodeEditor.vue';
import SvgVisualization from '../SvgVisualization.vue';

import { ArchsimSplit } from '@/js/archsim-split';
import { useToySimulationStore } from '@/js/toy_simulation_store';
import svgPath from "/src/img/toy_structure.svg";
import { toySettings } from '@/js/toy_settings';

const simulationStore = useToySimulationStore();

const mainContentContainer = ref(null);
const textContentContainer = ref(null);
const visualizationsContainer = ref(null);

let split = null;

const textContainerPopulated = computed(() => (toySettings.showInput.value || toySettings.showMainColumn.value));
const enableSplit = computed(() => textContainerPopulated.value && toySettings.showVisualization.value);

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
  split.createSplit();
});

onUnmounted(() => {
    split.destroyObject();
});

</script>

<template>
    <ToyControlBar />

    <div ref="mainContentContainer" id="toy-main-content-container" class="d-flex">
        <div ref="textContentContainer" id="toy-text-content-container" :class="textContainerPopulated ? 'd-flex flex-grow-1' : 'd-none'">
            <CodeEditor class="flex-grow-1 code-editor" :simulation-store="simulationStore" isa-name="toy" v-show="toySettings.showInput.value"/>
            <ToyMainTextContainer v-show="toySettings.showMainColumn.value"/>
        </div>
        <div v-show="toySettings.showVisualization.value" ref="visualizationsContainer" id="toy-visualizations-container">
            <SvgVisualization :simulation-store="simulationStore" :path="svgPath"/>
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
.code-editor {
    min-width: 20em;
}
</style>
