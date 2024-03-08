<!-- RISCV settings page -->
<script setup>
import { ref, watch } from "vue";
import RadioSettingsRow from "../RadioSettingsRow.vue";
import RepresentationSettingsRow from "../RepresentationSettingsRow.vue";
import CacheParameters from "./CacheParameters.vue";

import { useRiscvSimulationStore } from "@/js/riscv_simulation_store";
import { useEditorStore } from "@/js/editor_store";
import { riscvSettings } from "@/js/riscv_settings";

const simulationStore = useRiscvSimulationStore();
const editorStore = useEditorStore(simulationStore, "riscv");

// Changes to these values must be watched to perform side effects
const pipelineMode = ref(riscvSettings.pipelineMode.value);
const dataHazardDetection = ref(riscvSettings.dataHazardDetection.value);
const enableDataCache = ref(riscvSettings.dataCache.value.enable);
const enableInstructionCache = ref(riscvSettings.instructionCache.value.enable);

// Reset the sim and parse the input if the pipeline or data hazard detection changes
watch(
    () => [
        pipelineMode.value,
        dataHazardDetection.value,
        enableDataCache.value,
        enableInstructionCache.value,
    ],
    ([
        pipelineMode,
        dataHazardDetection,
        enableDataCache,
        enableInstructionCache,
    ]) => {
        riscvSettings.pipelineMode.value = pipelineMode;
        riscvSettings.dataHazardDetection.value = dataHazardDetection;
        riscvSettings.dataCache.value.enable = enableDataCache;
        riscvSettings.instructionCache.value.enable = enableInstructionCache;
        // FIXME: This is the same as the reset button does in RiscvControlBar.vue
        simulationStore.resetSimulation();
        editorStore.loadProgram();
    }
);
</script>

<template>
    <RepresentationSettingsRow
        display-name="Registers"
        v-model="riscvSettings.registerRepresentation.value"
        :default-selection="riscvSettings.registerRepresentation.value"
        base-id="riscv-register-representation"
    />
    <RepresentationSettingsRow
        display-name="Memory"
        v-model="riscvSettings.memoryRepresentation.value"
        :default-selection="riscvSettings.memoryRepresentation.value"
        base-id="riscv-memory-representation"
    />
    <RadioSettingsRow
        display-name="Pipeline Mode"
        v-model="pipelineMode"
        :default-selection="riscvSettings.pipelineMode.value"
        base-id="riscv-pipeline-mode"
        :option-names="['Single Stage', 'Five Stage']"
        :option-values="['single_stage_pipeline', 'five_stage_pipeline']"
    />
    <div
        class="row"
        v-if="riscvSettings.pipelineMode.value === 'five_stage_pipeline'"
    >
        <div class="col-4"></div>
        <div class="col-8">
            <label type="checkbox" for="riscv-data-hazard-detection">
                <input
                    id="riscv-data-hazard-detection"
                    type="checkbox"
                    :checked="dataHazardDetection"
                    v-model="dataHazardDetection"
                />
                Data Hazard detection
            </label>
        </div>
    </div>
    <div class="row">
        <div class="col-4">
            <h3 class="fs-6">Data Cache</h3>
        </div>
        <div class="col-8">
            <label for="riscv-data-cache-enable">
                <input
                    type="checkbox"
                    id="riscv-data-cache-enable"
                    :checked="enableDataCache"
                    v-model="enableDataCache"
                />
                Enable
            </label>
        </div>
    </div>
    <div class="row">
        <div class="col-4"></div>
        <div class="col-8">
            <CacheParameters v-model="riscvSettings.dataCache.value" />
        </div>
    </div>
    <div class="row">
        <div class="col-4">
            <h3 class="fs-6">Instruction Cache</h3>
        </div>
        <div class="col-8">
            <label for="riscv-instruction-cache-enable">
                <input
                    type="checkbox"
                    id="riscv-instruction-cache-enable"
                    :checked="enableInstructionCache"
                    v-model="enableInstructionCache"
                />
                Enable
            </label>
        </div>
    </div>
    <div class="row">
        <div class="col-4"></div>
        <div class="col-8">
            <CacheParameters v-model="riscvSettings.instructionCache.value" />
        </div>
    </div>
</template>

<style scoped></style>
