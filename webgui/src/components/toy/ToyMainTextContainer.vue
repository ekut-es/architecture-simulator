<script setup>
import ToyMemoryTable from './ToyMemoryTable.vue';
import ToyRegisterTable from './ToyRegisterTable.vue';
import ToyOutputField from './ToyOutputField.vue';
</script>

<template>
    <div id="toy-main-text-container">
        <ToyRegisterTable />
        <ToyMemoryTable />
        <ToyOutputField />
    </div>
</template>

<style scoped>
#toy-main-text-container {
    margin-left: var(--content-margin);
    overflow: auto;
}

#toy-main-text-container>* {
    overflow: auto;
}
</style>
