<script setup>
import RiscvOutputField from "./RiscvOutputField.vue";
import RiscvRegisterTable from "./RiscvRegisterTable.vue";
</script>

<template>
    <div class="wrapper">
        <span class="archsim-text-element-heading">Registers</span>
        <RiscvRegisterTable class="registers" />
        <span class="archsim-text-element-heading">Output</span>
        <RiscvOutputField class="output" />
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
