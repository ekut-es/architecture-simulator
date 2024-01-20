<script setup>
import { computed } from 'vue';

import { useToySimulationStore } from '@/js/toy_simulation_store';
import { useEditorStore } from "@/js/editor_store";

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

</script>

<template>
    <nav id="nav-bar" class="container-fluid">
        <div class="row pt-1 pb-1">
            <!--Buttons on the left side-->
            <div class="col-auto">
                <button @click="simulationStore.runSimulation();" :disabled="disableRun" id="button-run-simulation"
                    class="btn btn-success me-1" title="run">
                    <i class="bi bi-play-fill"></i>
                </button>
                <button @click="simulationStore.pauseSimulation();" :disabled="disablePause" id="button-pause-simulation"
                    class="btn btn-warning me-1" title="pause" disabled>
                    <i class="bi bi-pause-fill"></i>
                </button>
                <button @click="stepButton();" :disabled="disableSingleStep" id="button-step-simulation"
                    class="btn btn-primary me-1" title="single step">
                    <i class="bi bi-skip-end-fill"></i>
                </button>
                <button @click="doubleStepButton();" :disabled="disableDoubleStep"
                    id="button-double-step-simulation" class="btn btn-primary me-1" title="double step">
                    <i class="bi bi-skip-forward-fill"></i>
                </button>
                <button @click="resetButton();" :disabled="disableReset" id="button-reset-simulation"
                    class="btn btn-danger me-1" title="reset">
                    <i class="bi bi-arrow-clockwise"></i>
                </button>
                <button @click="editorStore.clickFileSelector();" :disabled="disableUpload" id="upload-button" class="btn btn-secondary me-1"
                    title="upload">
                    <i class="bi bi-file-earmark-arrow-up"></i>
                </button>
                <button @click="editorStore.saveTextAsFile();" id="download-button" class="btn btn-secondary me-1"
                    title="download">
                    <i class="bi bi-file-earmark-arrow-down"></i>
                </button>
            </div>
            <!--Buttons on the right side-->
            <div class="col-auto ms-auto">
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
