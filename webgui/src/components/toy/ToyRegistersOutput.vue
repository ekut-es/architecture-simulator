<!-- Contains the register table and output field -->
<script setup>
import ToyOutputField from "./ToyOutputField.vue";
import ToyRegisterTable from "./ToyRegisterTable.vue";
</script>

<template>
    <div class="registers-output-wrapper">
        <ToyRegisterTable />
        <ToyOutputField />
    </div>
</template>

<style scoped>
.registers-output-wrapper {
    display: flex;
    flex-direction: column;
}
</style>
