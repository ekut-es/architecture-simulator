<script setup>
import { computed, watch } from 'vue';

import ToyElementToggle from './ToyElementToggle.vue';

import { useToySimulationStore } from '@/js/toy_simulation_store';
import { useEditorStore } from "@/js/editor_store";
import { toySettings } from '@/js/toy_settings';
import ToyControlButtons from './ToyControlButtons.vue';

const simulationStore = useToySimulationStore();
const editorStore = useEditorStore(simulationStore, "toy");

const cantStep = computed(() => simulationStore.isRunning || !simulationStore.hasInstructions || simulationStore.isDone || editorStore.hasUnparsedChanges.value);

const disableRun = cantStep;

const disablePause = computed(() => !simulationStore.isRunning);

const disableSingleStep = cantStep;

const disableDoubleStep = computed(() => cantStep.value || (simulationStore.nextCycle != 1));

const disableReset = computed(() => simulationStore.isRunning);

const disableUpload = computed(() => simulationStore.hasStarted);

function stepButton() {
    simulationStore.resumePerformanceTimer();
    simulationStore.stepSimulation();
    simulationStore.stopPerformanceTimer();
    simulationStore.syncAll();
}

function doubleStepButton() {
    simulationStore.resumePerformanceTimer();
    simulationStore.doubleStepSimulation();
    simulationStore.stopPerformanceTimer();
    simulationStore.syncAll();
}

function resetButton() {
    simulationStore.resetSimulation();
    editorStore.loadProgram();
}

/**
 * Hide the input field when the simulation starts.
 */
watch(() => simulationStore.hasStarted, (hasStarted) => {
    toySettings.showInput.value = !hasStarted;
});

</script>

<template>
    <nav id="nav-bar" class="container-fluid py-1">
        <div class="row">
            <ToyControlButtons class="col" />
            <ToyElementToggle class="col" />
            <div class="d-flex justify-content-end col">
                <button class="btn" title="settings" data-bs-toggle="modal" data-bs-target="#settings-modal">
                    <i class="bi bi-gear-fill"></i>
                </button>
            </div>
        </div>
    </nav>
</template>

<style scoped>
button {
    font-size: 1.5rem;
    padding: 0px 6px;
}

nav {
    background-color: var(--bs-secondary-bg);
}
</style>
