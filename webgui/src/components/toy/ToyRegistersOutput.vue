<!-- Contains the register table and output field -->
<script setup>
import OutputField from "../OutputField.vue";
import ToyRegisterTable from "./ToyRegisterTable.vue";

import { useToySimulationStore } from "@/js/toy_simulation_store";

const simulationStore = useToySimulationStore();
</script>

<template>
    <div class="wrapper">
        <span class="archsim-text-element-heading">Registers</span>
        <ToyRegisterTable class="registers" />
        <span class="archsim-text-element-heading">Output</span>
        <OutputField class="output" :simulation-store="simulationStore" />
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
    margin-bottom: 0.5em;
}
</style>
