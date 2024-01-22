<script setup>
import ToggleButton from '../ToggleButton.vue';

import { toySettings } from '@/js/toy_settings';
</script>

<template>
    <div class="btn-group" role="group" aria-label="Toggle visibility of display elements">
        <ToggleButton v-model="toySettings.showInput.value" base-id="toy-toggle-input">Input</ToggleButton>
        <ToggleButton v-model="toySettings.showMainColumn.value" base-id="toy-toggle-main-column">Registers/Memory/Output</ToggleButton>
        <ToggleButton v-model="toySettings.showVisualization.value" base-id="toy-toggle-visualization">Visualization</ToggleButton>
    </div>
</template>
