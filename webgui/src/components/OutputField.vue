<!-- An output field that works with any simulation store -->
<script setup>
import { computed } from "vue";
const props = defineProps(["simulationStore", "additionalMessageGetter"]);
const simulationStore = props.simulationStore;

/**
 * An array that holds one string for each line to display
 * in the output field.
 *
 * Contains unknown errors and runtime errors, or shows the
 * performance metrics in case there are no errors.
 */
let output = computed(() => {
    if (simulationStore.error) {
        switch (simulationStore.error[0]) {
            case "ParserException":
                break; // Will be shown in the editor
            case "InstructionExecutionException":
                return [simulationStore.error[1]];
            default:
                return [
                    `An unknown error occured: ${simulationStore.error[1]}`,
                ];
        }
    }

    if (!simulationStore.hasStarted) {
        return ["Ready!"];
    }

    let messages = simulationStore.performanceMetricsStr.split(/\n/);
    if (typeof props.additionalMessageGetter !== "undefined") {
        messages = messages.concat(props.additionalMessageGetter());
    }
    return messages;
});
</script>

<template>
    <div class="archsim-default-border output-field">
        <template v-for="line in output">
            <template v-if="line"> {{ line }} <br /> </template>
        </template>
    </div>
</template>

<style scoped>
.output-field {
    background-color: #ffffff;
    padding: 0.5em;
    min-width: 18em;
    max-width: 20em;
}
</style>
