<script setup>
import RadioSettingsRow from './RadioSettingsRow.vue';

const setting = defineModel();
const props = defineProps({ "displayName": String, "defaultSelection": String, "baseId": String });
const outgoingProps = { ...props, optionNames: ["binary", "unsigned decimal", "signed decimal", "hexadecimal"], optionValues: ["0", "1", "3", "2"] };
</script>

<template>
    <RadioSettingsRow v-model="setting" v-bind="outgoingProps" />
</template>
