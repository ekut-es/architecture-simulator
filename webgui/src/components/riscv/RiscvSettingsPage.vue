<!-- RISCV settings page -->
<script setup>
import { ref, watch, watchEffect } from "vue";
import RadioSettingsRow from "../RadioSettingsRow.vue";
import RepresentationSettingsRow from "../RepresentationSettingsRow.vue";

import { useRiscvSimulationStore } from "@/js/riscv_simulation_store";
import { useEditorStore } from "@/js/editor_store";
import { riscvSettings } from "@/js/riscv_settings";

const simulationStore = useRiscvSimulationStore();
const editorStore = useEditorStore(simulationStore, "riscv");

// Changes to these values must be watched to perform side effects
const pipelineMode = ref(riscvSettings.pipelineMode.value);
const dataHazardDetection = ref(riscvSettings.dataHazardDetection.value);
const enableDataCache = ref(riscvSettings.dataCache.value.enable);
const dataCacheIndexBits = ref(riscvSettings.dataCache.value.num_index_bits);
const dataCacheBlockBits = ref(riscvSettings.dataCache.value.num_block_bits);
const dataCacheAssociativity = ref(riscvSettings.dataCache.value.associativity);
const enableInstructionCache = ref(riscvSettings.instructionCache.value.enable);
const instructionCacheIndexBits = ref(
    riscvSettings.instructionCache.value.num_index_bits
);
const instructionCacheBlockBits = ref(
    riscvSettings.instructionCache.value.num_block_bits
);
const instructionCacheAssociativity = ref(
    riscvSettings.instructionCache.value.associativity
);

// Reset the sim and parse the input if the pipeline or data hazard detection changes
watch(
    () => [
        pipelineMode.value,
        dataHazardDetection.value,
        enableDataCache.value,
        dataCacheIndexBits.value,
        dataCacheBlockBits.value,
        dataCacheAssociativity.value,
        enableInstructionCache.value,
        instructionCacheIndexBits.value,
        instructionCacheBlockBits.value,
        instructionCacheAssociativity.value,
    ],
    ([
        pipelineMode,
        dataHazardDetection,
        enableDataCache,
        dataCacheIndexBits,
        dataCacheBlockBits,
        dataCacheAssociativity,
        enableInstructionCache,
        instructionCacheIndexBits,
        instructionCacheBlockBits,
        instructionCacheAssociativity,
    ]) => {
        riscvSettings.pipelineMode.value = pipelineMode;
        riscvSettings.dataHazardDetection.value = dataHazardDetection;
        riscvSettings.dataCache.value.enable = enableDataCache;
        riscvSettings.dataCache.value.num_index_bits = dataCacheIndexBits;
        riscvSettings.dataCache.value.num_block_bits = dataCacheBlockBits;
        riscvSettings.dataCache.value.associativity = dataCacheAssociativity;
        riscvSettings.instructionCache.value.enable = enableInstructionCache;
        riscvSettings.instructionCache.value.num_index_bits =
            instructionCacheIndexBits;
        riscvSettings.instructionCache.value.num_block_bits =
            instructionCacheBlockBits;
        riscvSettings.instructionCache.value.associativity =
            instructionCacheAssociativity;
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
        <div class="col-4">Data Cache</div>
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
            <p>2<sup>N</sup> sets:</p>
            <input type="number" min="0" v-model="dataCacheIndexBits" />
            <p>2<sup>N</sup> words per block:</p>
            <input type="number" min="0" v-model="dataCacheBlockBits" />
            <p>associativity:</p>
            <input type="number" min="1" v-model="dataCacheAssociativity" />
        </div>
    </div>
</template>
