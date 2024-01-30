<!-- Creates a radio settings row that will have options for selecting the representation of numbers (bin, udec, hex, sdec) -->
<script setup>
import RadioSettingsRow from "./RadioSettingsRow.vue";

/**
 * The ref that holds the variable that this setting shall modify.
 */
const setting = defineModel();

/**
 * displayName: the name to display to the left of the buttons
 * defaultSelction: the value of the button that shall be selected by default
 * baseId: some unique id that will be used so the buttons know which label they belong to
 */
const props = defineProps({
    displayName: String,
    defaultSelection: String,
    baseId: String,
});

/**
 * The props that will be passed to the radio settings row.
 */
const outgoingProps = {
    ...props,
    optionNames: [
        "binary",
        "unsigned decimal",
        "signed decimal",
        "hexadecimal",
    ],
    optionValues: ["0", "1", "3", "2"],
};
</script>

<template>
    <RadioSettingsRow v-model="setting" v-bind="outgoingProps" />
</template>
