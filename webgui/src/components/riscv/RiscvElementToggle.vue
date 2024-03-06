<!-- The toggle button group for toggling the riscv elements. -->
<script setup>
import ToggleButton from "../ToggleButton.vue";

import { riscvSettings } from "@/js/riscv_settings";
</script>

<template>
    <div class="d-flex justify-content-center">
        <div
            class="btn-group"
            role="group"
            aria-label="Toggle visibility of display elements"
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
            <ToggleButton
                v-model="riscvSettings.showVisualization.value"
                base-id="riscv-toggle-visualization"
                >Visualization
            </ToggleButton>
            <ToggleButton
                v-model="riscvSettings.showDataCache.value"
                base-id="riscv-toggle-data-cache"
                >Data Cache
            </ToggleButton>
            <ToggleButton
                v-model="riscvSettings.showInstructionCache.value"
                base-id="riscv-toggle-instruction-cache"
                >Instruction Cache
            </ToggleButton>
        </div>
    </div>
</template>
