<script setup>
import { computed } from 'vue';

import { useToySimulationStore } from '@/js/toy_simulation_store';

const simulationStore = useToySimulationStore();

let output = computed(() => {
    if (simulationStore.error) {
        switch (simulationStore.error[0]) {
            case "ParserException":
            case "InstructionExecutionException":
                return [simulationStore.error[1]];
            default:
                return [`An unknown error occured: ${simulationStore.error[1]}`];
        }
    }

    if (!simulationStore.hasStarted) {
        return ["Ready!"];
    }

    return simulationStore.performanceMetricsStr.split(/\n/);
});
</script>

<template>
    <div id="toy-output-wrapper">
        <span class="archsim-text-element-heading">Output</span>
        <div class="flex-shrink-0 archsim-default-border output-field">
            <template v-for="line in output">
                <template v-if="line">
                    {{ line }} <br>
                </template>
            </template>
        </div>
    </div>
</template>

<style scoped>
.output-field {
    background-color: #ffffff;
    padding: 1em;
    min-width: 12em;
}

#toy-output-wrapper,
#toy-registers-wrapper {
    flex: 0 0 auto;
}
</style>
