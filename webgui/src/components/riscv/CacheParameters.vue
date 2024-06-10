<!-- A module for the settings page to control cache settings -->
<script setup>
import { useEditorStore } from "@/js/editor_store";
import { useRiscvSimulationStore } from "@/js/riscv_simulation_store";
import { ref, watch } from "vue";
import ErrorTooltip from "../ErrorTooltip.vue";
import CacheDisabledTooltip from "./CacheDisabledTooltip.vue";

const cacheSettings = defineModel("cacheSettings");
const tooBigSetting = defineModel("tooBigSetting");
const props = defineProps(["isDataCache", "baseId"]);

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
const tooManyBitsUsed = ref(false);

// Disable the visualization if the cache exceeds this amount of words.
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
            tooManyBitsUsed.value = newIndexBits + newBlockBits + 2 > 32;
            if (tooManyBitsUsed.value) {
                return;
            }

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
    <div class="row">
        <div class="col-4">
            <h3 class="fs-6">
                <slot> </slot>
            </h3>
        </div>
        <div class="col-8">
            <label :for="props.baseId + '-enable'">
                <input
                    type="checkbox"
                    :id="props.baseId + '-enable'"
                    :checked="cacheSettings.enable"
                    v-model="cacheSettings.enable"
                />
                Enable
            </label>
            <CacheDisabledTooltip v-if="tooBigSetting" />
            <ErrorTooltip
                v-if="tooManyBitsUsed"
                message="This configuration uses more than 32 bits."
            />
        </div>
    </div>
    <div v-if="cacheSettings.enable" class="row">
        <div class="col-4"></div>
        <div class="col-8">
            <form class="archsim-form-table">
                <p v-if="props.isDataCache">
                    <label>Type:</label>
                    <select v-model="cacheType">
                        <option value="wb">Write-back, Write allocate</option>
                        <option value="wt">
                            Write-through, Write no-allocate
                        </option>
                    </select>
                </p>
                <p>
                    <label>Replacement Strategy:</label>
                    <select v-model="replacementStrategy">
                        <option value="lru">LRU</option>
                        <option value="plru">PLRU</option>
                    </select>
                </p>
                <p
                    v-if="cacheSettings.replacement_strategy === 'plru'"
                    class="ms-2"
                    :for="props.baseId + '-show-plru'"
                >
                    <label>Show PLRU Tree:</label>
                    <input
                        type="checkbox"
                        :id="props.baseId + '-show-plru'"
                        :checked="cacheSettings.showPlruTree"
                        v-model="cacheSettings.showPlruTree"
                    />
                </p>
                <p>
                    <label>ways (blocks per set):</label>
                    <select v-model="indexBits">
                        <option
                            v-for="option in Array.from(
                                { length: 9 },
                                (x, i) => i
                            )"
                            :value="option"
                        >
                            {{ Math.pow(2, option) }}
                        </option>
                    </select>
                    <ErrorTooltip
                        v-if="indexBitsStatus"
                        :message="indexBitsStatus"
                    />
                </p>
                <p>
                    <label>words per block:</label>
                    <select v-model="blockBits">
                        <option
                            v-for="option in Array.from(
                                { length: 9 },
                                (x, i) => i
                            )"
                            :value="option"
                        >
                            {{ Math.pow(2, option) }}
                        </option>
                    </select>
                    <ErrorTooltip
                        v-if="blockBitsStatus"
                        :message="blockBitsStatus"
                    />
                </p>
                <p>
                    <label>associativity (sets):</label>
                    <select v-model="associativity">
                        <option
                            v-for="option in Array.from({ length: 9 }, (x, i) =>
                                Math.pow(2, i)
                            )"
                            :value="option"
                        >
                            {{ option }}
                        </option>
                    </select>
                    <ErrorTooltip
                        v-if="associativityStatus"
                        :message="associativityStatus"
                    />
                </p>
            </form>
        </div>
    </div>
</template>

<style scoped>
.number-input {
    width: 3em;
}
</style>
