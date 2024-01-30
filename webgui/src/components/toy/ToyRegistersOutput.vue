<!-- Contains the register table and output field -->
<script setup>
import ToyOutputField from "./ToyOutputField.vue";
import ToyRegisterTable from "./ToyRegisterTable.vue";
</script>

<template>
    <div class="wrapper">
        <span class="archsim-text-element-heading">Registers</span>
        <ToyRegisterTable class="registers" />
        <span class="archsim-text-element-heading">Output</span>
        <ToyOutputField class="output" />
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
