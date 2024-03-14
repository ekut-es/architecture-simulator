<script setup>
import { useEditorStore } from "@/js/editor_store";
import { useRiscvSimulationStore } from "@/js/riscv_simulation_store";
import { ref, watch } from "vue";

const model = defineModel();
const props = defineProps(["isDataCache"]);

const indexBits = ref(model.value.num_index_bits);
const blockBits = ref(model.value.num_block_bits);
const associativity = ref(model.value.associativity);
const indexBitsStatus = ref("");
const blockBitsStatus = ref("");
const associativityStatus = ref("");
const totalSize = ref(0);
const totalSizeValid = ref(true);
const replacementStrategy = ref(model.value.replacement_strategy);
const cacheType = ref(model.value.cache_type);
// const replacementStrategy = ref(model.value.replacement_strategy.toUpperCase());
// const cacheTypeReadable = ref(cacheTypeToReadable(model.value.cache_type));

const totalSizeThreshold = 2048;

const simulationStore = useRiscvSimulationStore();
const editorStore = useEditorStore(simulationStore, "riscv");

watch(
    [indexBits, blockBits, associativity, cacheType, replacementStrategy],
    ([
        newIndexBits,
        newBlockBits,
        newAssociativity,
        newCacheType,
        newReplacementStrategy,
    ]) => {
        indexBitsStatus.value = validateGreaterEquals(newIndexBits, 0);
        blockBitsStatus.value = validateGreaterEquals(newBlockBits, 0);
        associativityStatus.value = validateAssociativity(
            newAssociativity,
            newReplacementStrategy
        );

        if (
            indexBitsStatus.value === "" &&
            blockBitsStatus.value === "" &&
            associativityStatus.value === ""
        ) {
            totalSize.value =
                Math.pow(2, newIndexBits + newBlockBits) * newAssociativity;
        }

        totalSizeValid.value = totalSize.value <= totalSizeThreshold;

        if (!totalSizeValid.value) {
            return;
        }

        if (
            indexBitsStatus.value === "" &&
            blockBitsStatus.value === "" &&
            associativityStatus.value === ""
        ) {
            model.value.num_index_bits = newIndexBits;
            model.value.num_block_bits = newBlockBits;
            model.value.associativity = newAssociativity;
            model.value.cache_type = newCacheType;
            model.value.replacement_strategy = newReplacementStrategy;
            simulationStore.resetSimulation();
            editorStore.loadProgram();
        }
    },
    { immediate: true }
);

function validateGreaterEquals(number, min) {
    if (Number.isNaN(number)) {
        return "Error: The value must be a number.";
    }
    if (!(min <= number)) {
        return `Error: The value must be at least ${min}.`;
    }
    return "";
}

function validateAssociativity(number, strategy) {
    let status = validateGreaterEquals(number, 1);
    if (status !== "") {
        return status;
    }
    if (strategy === "plru" && !Number.isInteger(Math.log2(number))) {
        return "When using PLRU, associativity must be a power of 2";
    }
    return "";
}
</script>

<template>
    <p v-if="props.isDataCache">
        Type:
        <select v-model="cacheType">
            <option value="wb">Write-back, Write allocate</option>
            <option value="wt">Write-through, Write no-allocate</option>
        </select>
    </p>
    <p>
        Replacement Strategy:
        <select v-model="replacementStrategy">
            <option value="lru">LRU</option>
            <option value="plru">PLRU</option>
        </select>
    </p>
    <div
        v-if="!totalSizeValid"
        class="alert alert-warning d-flex align-items-center"
        role="alert"
    >
        <i class="bi bi-exclamation-triangle-fill flex-shrink-0 me-2"></i>
        <div>
            The current cache configuration is invalid because it would create
            more than {{ totalSizeThreshold }} words.
        </div>
    </div>
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
