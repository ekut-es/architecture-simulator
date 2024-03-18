<!-- RISCV settings page -->
<script setup>
import { nextTick, ref, watch } from "vue";
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
        // Do this in the next tick because if the cache gets disabled,
        // the CacheView needs time to disappear first
        nextTick(() => {
            simulationStore.resetSimulation();
            editorStore.loadProgram();
        });
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

    <CacheParameters
        v-model:cache-settings="riscvSettings.dataCache.value"
        v-model:too-big-setting="riscvSettings.dataCacheTooBig.value"
        :is-data-cache="true"
        base-id="riscv-data-cache"
    >
        Data Cache
    </CacheParameters>

    <CacheParameters
        v-model:cache-settings="riscvSettings.instructionCache.value"
        v-model:too-big-setting="riscvSettings.instructionCacheTooBig.value"
        :is-data-cache="false"
        base-id="ricsv-instruction-cache"
    >
        Instruction Cache
    </CacheParameters>
</template>

<style scoped></style>
