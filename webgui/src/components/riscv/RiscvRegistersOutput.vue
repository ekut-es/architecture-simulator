<script setup>
import OutputField from "../OutputField.vue";
import RiscvRegisterTable from "./RiscvRegisterTable.vue";

import { useRiscvSimulationStore } from "@/js/riscv_simulation_store";

const simulationStore = useRiscvSimulationStore();
const additionalMessageGetter = () => {
    let messages = [];
    messages.push(simulationStore.output);
    if (simulationStore.dataCacheStats !== null) {
        const hits = simulationStore.dataCacheStats.get("hits");
        const misses = simulationStore.dataCacheStats.get("accesses") - hits;
        messages.push(
            `Data Cache Hits: ${hits}`,
            `Data Cache Misses: ${misses}`
        );
    }
    if (simulationStore.instructionCacheStats !== null) {
        const hits = simulationStore.instructionCacheStats.get("hits");
        const misses =
            simulationStore.instructionCacheStats.get("accesses") - hits;
        messages.push(
            `Instruction Cache Hits: ${hits}`,
            `Instruction Cache Misses: ${misses}`
        );
    }
    return messages;
};
</script>

<template>
    <div class="wrapper">
        <span class="archsim-text-element-heading">Registers</span>
        <RiscvRegisterTable class="registers" />
        <span class="archsim-text-element-heading">Output</span>
        <OutputField
            class="output"
            :simulation-store="simulationStore"
            :additional-message-getter
        />
    </div>
</template>

<style scoped>
.wrapper {
    display: flex;
    flex-direction: column;
}

.registers,
.output {
    overflow-y: auto;
}

.registers {
    flex: 0 1 auto;
    margin-bottom: 0.5em;
}

.output {
    flex: 1 0 8em;
}
</style>
