<!-- The toggle button group for toggling the TOY elements. -->
<script setup>
import ToggleButton from "../ToggleButton.vue";
import { toySettings } from "@/js/toy_settings";
</script>

<template>
    <div
        class="btn-group"
        role="group"
        aria-label="Toggle visibility of display elements on the right side"
    >
        <ToggleButton
            v-model="toySettings.showInput.value"
            base-id="toy-toggle-input"
            >Input</ToggleButton
        >
        <ToggleButton
            v-model="toySettings.showMemory.value"
            base-id="toy-toggle-memory"
        >
            Memory</ToggleButton
        >
        <ToggleButton
            v-model="toySettings.showRegistersOutput.value"
            base-id="toy-toggle-registers-output"
        >
            Registers/Output</ToggleButton
        >
    </div>
</template>
