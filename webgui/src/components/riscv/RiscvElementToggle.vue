<!-- The toggle button group for toggling the riscv elements. -->
<script setup>
import { watch } from "vue";
import ToggleButton from "../ToggleButton.vue";

import { riscvSettings } from "@/js/riscv_settings";

// Select the processor view if the user disables the cache he is currently viewing.
watch(
    () => [
        riscvSettings.dataCache.value.enable,
        riscvSettings.instructionCache.value.enable,
    ],
    ([enableDataCache, enableInstructionCache]) => {
        const selected = riscvSettings.visContainerSelection.value;
        if (
            (!enableDataCache && selected === "Data Cache") ||
            (!enableInstructionCache && selected === "Instruction Cache")
        ) {
            riscvSettings.visContainerSelection.value = "Processor";
        }
    }
);
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
    <select v-model="riscvSettings.visContainerSelection.value">
        <option>None</option>
        <option>Processor</option>
        <option v-if="riscvSettings.dataCache.value.enable">Data Cache</option>
        <option v-if="riscvSettings.instructionCache.value.enable">
            Instruction Cache
        </option>
    </select>
</template>
