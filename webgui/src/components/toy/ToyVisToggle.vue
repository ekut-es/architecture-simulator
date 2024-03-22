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
            v-model="toySettings.showVisualization.value"
            base-id="toy-toggle-visualization"
            >Processor
        </ToggleButton>
    </div>
</template>
