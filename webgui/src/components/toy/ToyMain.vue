<script setup>

import { ref, onMounted, onUnmounted } from 'vue';

import ToyControlBar from './ToyControlBar.vue';
import ToyMainTextContainer from './ToyMainTextContainer.vue';
import CodeEditor from '../CodeEditor.vue';
import SvgVisualization from '../SvgVisualization.vue';

import { ArchsimSplit } from '@/js/archsim-split';
import { useToySimulationStore } from '@/js/toy_simulation_store';
import svgPath from "/src/img/toy_structure.svg";

const simulationStore = useToySimulationStore();

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
});

</script>

<template>
    <ToyControlBar />

    <div ref="mainContentContainer" id="toy-main-content-container">
        <div ref="textContentContainer" id="toy-text-content-container" class="d-flex justify-content-between">
            <CodeEditor :simulation-store="simulationStore" isa-name="toy"/>
            <ToyMainTextContainer />
        </div>
        <div ref="visualizationsContainer" id="toy-visualizations-container">
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
</style>
