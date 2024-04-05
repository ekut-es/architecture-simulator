<script setup>
import OutputField from "../OutputField.vue";
import RiscvRegisterTable from "./RiscvRegisterTable.vue";

import { useRiscvSimulationStore } from "@/js/riscv_simulation_store";

const simulationStore = useRiscvSimulationStore();
const additionalMessageGetter = () => simulationStore.output;
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
