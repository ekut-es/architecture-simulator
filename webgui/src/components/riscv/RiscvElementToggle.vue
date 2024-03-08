<!-- The toggle button group for toggling the riscv elements. -->
<script setup>
import ToggleButton from "../ToggleButton.vue";

import { riscvSettings } from "@/js/riscv_settings";
</script>

<template>
    <div
        class="btn-group"
        role="group"
        aria-label="Toggle visibility of display elements on the left side"
    >
        <ToggleButton
            v-model="riscvSettings.showInput.value"
            base-id="riscv-toggle-input"
            >Input</ToggleButton
        >
        <ToggleButton
            v-model="riscvSettings.showMemory.value"
            base-id="riscv-toggle-memory"
            >Memory</ToggleButton
        >
        <ToggleButton
            v-model="riscvSettings.showRegistersOutput.value"
            base-id="riscv-toggle-registers-output"
            >Registers/Output
        </ToggleButton>
    </div>
    <div
        class="btn-group"
        role="group"
        aria-label="Toggle visibility of the display elements on the right side"
    >
        <ToggleButton
            v-model="riscvSettings.showVisualization.value"
            base-id="riscv-toggle-visualization"
            >Visualization
        </ToggleButton>
        <ToggleButton
            v-if="riscvSettings.dataCache.value.enable"
            v-model="riscvSettings.showDataCache.value"
            base-id="riscv-toggle-data-cache"
            >Data Cache
        </ToggleButton>
        <ToggleButton
            v-if="riscvSettings.instructionCache.value.enable"
            v-model="riscvSettings.showInstructionCache.value"
            base-id="riscv-toggle-instruction-cache"
            >Instruction Cache
        </ToggleButton>
    </div>
</template>
