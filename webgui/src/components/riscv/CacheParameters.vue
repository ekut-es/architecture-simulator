<script setup>
import { useEditorStore } from "@/js/editor_store";
import { useRiscvSimulationStore } from "@/js/riscv_simulation_store";
import { ref, watch } from "vue";

const model = defineModel();

const indexBits = ref(model.value.num_index_bits);
const blockBits = ref(model.value.num_block_bits);
const associativity = ref(model.value.associativity);
const indexBitsStatus = ref("");
const blockBitsStatus = ref("");
const associativityStatus = ref("");

const simulationStore = useRiscvSimulationStore();
const editorStore = useEditorStore(simulationStore, "riscv");

watch(
    () => [indexBits.value, blockBits.value, associativity.value],
    ([newIndexBits, newBlockBits, newAssociativity]) => {
        indexBitsStatus.value = validateInput(newIndexBits, 0, 6);
        blockBitsStatus.value = validateInput(newBlockBits, 0, 6);
        associativityStatus.value = validateInput(newAssociativity, 0, 8);

        if (indexBitsStatus.value === "") {
            model.value.num_index_bits = newIndexBits;
        }
        if (blockBitsStatus.value === "") {
            model.value.num_block_bits = newBlockBits;
        }
        if (associativityStatus.value === "") {
            model.value.associativity = newAssociativity;
        }
        simulationStore.resetSimulation();
        editorStore.loadProgram();
    }
);

function validateInput(number, min, max) {
    if (Number.isNaN(number)) {
        return "Error: The value must be a number.";
    }
    if (!(min <= number && number <= max)) {
        return `Error: The value must be between ${min} and ${max}.`;
    }
    return "";
}
</script>

<template>
    <p>
        2<sup>N</sup> sets:
        <input class="number-input" type="number" min="0" v-model="indexBits" />
        {{ indexBitsStatus }}
    </p>
    <p>
        2<sup>N</sup> words per block:
        <input class="number-input" type="number" min="0" v-model="blockBits" />
        {{ blockBitsStatus }}
    </p>
    <p>
        associativity:
        <input
            class="number-input"
            type="number"
            min="1"
            v-model="associativity"
        />
        {{ associativityStatus }}
    </p>
</template>

<style scoped>
.number-input {
    width: 3em;
}
</style>
