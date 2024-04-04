<!-- An output field that works with any simulation store -->
<script setup>
import { computed } from "vue";
const props = defineProps([
    "simulationStore",
    "exitCode",
    "additionalMessageGetter",
]);
const simulationStore = props.simulationStore;

/**
 * Contains error messages, status information on the simulation
 * as well as exit codes.
 */
let output = computed(() => {
    if (simulationStore.error) {
        switch (simulationStore.error[0]) {
            case "ParserException":
                return "An error has occured during parsing."; // exact error will be shown in the editor
            case "InstructionExecutionException":
                return simulationStore.error[1];
            default:
                return `An unknown error occured: ${simulationStore.error[1]}`;
        }
    }

    let message = "";

    if (!simulationStore.hasStarted) {
        message = "Ready!";
    } else if (simulationStore.hasStarted && !simulationStore.isDone) {
        message = "The simulation has started.";
    } else if (simulationStore.isDone) {
        message = "The simulation has finished";
        if (typeof props.exitCode !== "undefined" && props.exitCode !== null) {
            message += ` with exit code ${props.exitCode}`;
        }
        message += ".";
    }

    if (typeof props.additionalMessageGetter !== "undefined") {
        message += "<br/>" + props.additionalMessageGetter();
    }

    return message;
});
</script>

<template>
    <div class="archsim-default-border output-field" v-html="output"></div>
</template>

<style scoped>
.output-field {
    background-color: #ffffff;
    padding: 0.5em;
    min-width: 15em;
    max-width: 20em;
}
</style>
