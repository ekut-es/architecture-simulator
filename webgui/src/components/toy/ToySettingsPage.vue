<!-- The settings page for TOY -->
<script setup>
import RepresentationSettingsRow from "../RepresentationSettingsRow.vue";

import { toySettings } from "@/js/toy_settings";
</script>

<template>
    <RepresentationSettingsRow
        display-name="Registers"
        v-model="toySettings.registerRepresentation.value"
        :default-selection="toySettings.registerRepresentation.value"
        base-id="toy-register-representation"
    />
    <RepresentationSettingsRow
        display-name="Memory"
        v-model="toySettings.memoryRepresentation.value"
        :default-selection="toySettings.memoryRepresentation.value"
        base-id="toy-memory-representation"
    />
</template>
