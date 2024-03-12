<script setup>
import { computed } from "vue";

const props = defineProps([
    "cacheEntries",
    "cacheSettings",
    "isDataCache",
    "cacheStats",
]);
const blockSize = computed(() =>
    Math.pow(2, props.cacheSettings.num_block_bits)
);

const tagWidth = computed(() => {
    const bitWidth =
        32 -
        (props.cacheSettings.num_index_bits +
            props.cacheSettings.num_block_bits +
            2);
    const hexWidth = 4 + Math.ceil(bitWidth / 4);
    return hexWidth + "ch";
});

const wordWidth = "12ch"; // enough space for udec
const instrWidth = "20ch";
const wordStyle = (() => {
    const style = { minWidth: props.isDataCache ? wordWidth : instrWidth };
    if (props.isDataCache) {
        // instructions may use more space
        style.width = wordWidth;
    }
    return style;
})();

const showDirtyBit = computed(() => props.cacheSettings.cache_type === "wb");

const misses = computed(() =>
    String(
        Number(props.cacheStats.get("accesses")) -
            Number(props.cacheStats.get("hits"))
    )
);
</script>

<template>
    <div>
        <p>Hits: {{ props.cacheStats.get("hits") }}</p>
        <p>Misses: {{ misses }}</p>
        <template v-if="props.cacheEntries !== null">
            <table
                class="table table-sm table-bordered archsim-mono-table cache-table"
            >
                <thead>
                    <tr>
                        <th style="width: 0em">Index</th>
                        <th style="width: 0em">Valid</th>
                        <th v-if="showDirtyBit" style="width: 0em">Dirty</th>
                        <th :style="{ width: tagWidth, minWidth: tagWidth }">
                            Tag
                        </th>
                        <th v-for="i in blockSize" :style="wordStyle">
                            Word {{ i }}
                        </th>
                    </tr>
                </thead>
                <tbody class="cache-table-body">
                    <template v-for="zet in props.cacheEntries.get('sets')">
                        <tr v-for="(block, index) in zet.get('blocks')">
                            <td
                                v-if="
                                    index %
                                        props.cacheSettings.associativity ===
                                    0
                                "
                                :rowspan="props.cacheSettings.associativity"
                                class="index"
                            >
                                {{ zet.get("index") }}
                            </td>
                            <td class="valid">{{ block.get("valid_bit") }}</td>
                            <td v-if="showDirtyBit" class="dirty">
                                {{ block.get("dirty_bit") }}
                            </td>
                            <td class="tag">{{ block.get("tag") }}</td>
                            <template
                                v-for="addr_value in block.get(
                                    'address_value_list'
                                )"
                            >
                                <td class="word">{{ addr_value[1] }}</td>
                            </template>
                        </tr>
                    </template>
                </tbody>
            </table>
        </template>
    </div>
</template>

<style scoped>
.cache-table {
    margin-bottom: 0em;
    width: auto;
}

.index {
    vertical-align: middle;
    text-align: right;
}

.valid,
.dirty {
    text-align: center;
}

.tag,
.word {
    text-align: right;
}
</style>
