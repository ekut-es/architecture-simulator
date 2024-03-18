<!-- A module for the settings page to control cache settings -->
<script setup>
import { useEditorStore } from "@/js/editor_store";
import { useRiscvSimulationStore } from "@/js/riscv_simulation_store";
import { ref, watch } from "vue";
import ErrorTooltip from "../ErrorTooltip.vue";

const cacheSettings = defineModel("cacheSettings");
const tooBigSetting = defineModel("tooBigSetting");
const props = defineProps(["isDataCache"]);

// refs to bind to the inputs so they can be validated first
const indexBits = ref(cacheSettings.value.num_index_bits);
const blockBits = ref(cacheSettings.value.num_block_bits);
const associativity = ref(cacheSettings.value.associativity);
const replacementStrategy = ref(cacheSettings.value.replacement_strategy);
const cacheType = ref(cacheSettings.value.cache_type);

// Status messages ("" is ok, everything else is an error)
const indexBitsStatus = ref("");
const blockBitsStatus = ref("");
const associativityStatus = ref("");

// Performance sucks right now, this is the max amount of words that works well
const totalSizeThreshold = 2048;

const simulationStore = useRiscvSimulationStore();
const editorStore = useEditorStore(simulationStore, "riscv");

// Watch the inputs, validate them and pass them to the actual settings
watch(
    [indexBits, blockBits, associativity, cacheType, replacementStrategy],
    ([
        newIndexBits,
        newBlockBits,
        newAssociativity,
        newCacheType,
        newReplacementStrategy,
    ]) => {
        newIndexBits = Number(newIndexBits);
        newBlockBits = Number(newBlockBits);
        newAssociativity = Number(newAssociativity);

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
            const tooBig =
                Math.pow(2, newIndexBits + newBlockBits) * newAssociativity >
                totalSizeThreshold;
            tooBigSetting.value = tooBig;

            cacheSettings.value.num_index_bits = newIndexBits;
            cacheSettings.value.num_block_bits = newBlockBits;
            cacheSettings.value.associativity = newAssociativity;
            cacheSettings.value.cache_type = newCacheType;
            cacheSettings.value.replacement_strategy = newReplacementStrategy;

            simulationStore.resetSimulation();
            editorStore.loadProgram();
        }
    },
    { immediate: true }
);

/**
 * Make sure that JS can cast the parameter to a number (or that it is a number)
 * and that it is greater or equal to the min value.
 *
 * @param {Any} number The number to check.
 * @param {Number} min The minimum allowed value.
 *
 * @return {String} A status message
 */
function validateGreaterEquals(number, min) {
    if (Number.isNaN(number)) {
        return "Error: The value must be a number.";
    }
    if (!(min <= number)) {
        return `Error: The value must be at least ${min}.`;
    }
    return "";
}

/**
 * Validate the associativity.
 *
 * @param {number} number The associativity
 * @param {string} strategy The replacement strategy (lru or plru)
 *
 * @return {string} a status message.
 */
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
    <p>
        2<sup>N</sup> sets:
        <input class="number-input" type="number" min="0" v-model="indexBits" />
        <ErrorTooltip v-if="indexBitsStatus" :message="indexBitsStatus" />
    </p>
    <p>
        2<sup>N</sup> words per block:
        <input class="number-input" type="number" min="0" v-model="blockBits" />
        <ErrorTooltip v-if="blockBitsStatus" :message="blockBitsStatus" />
    </p>
    <p>
        associativity:
        <input
            class="number-input"
            type="number"
            min="1"
            v-model="associativity"
        />
        <ErrorTooltip
            v-if="associativityStatus"
            :message="associativityStatus"
        />
    </p>
</template>

<style scoped>
.number-input {
    width: 3em;
}
</style>
