<script setup>
import CacheArrows from "./CacheArrows.vue";
import { computed, ref } from "vue";

const tagCell = ref(null);
const indexCell = ref(null);
// const blockOffsetCell = ref(null);
const wordOffsetCell = ref(null);
const addressTable = ref(null);

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

// address, settings
const address = computed(() => {
    const address = props.cacheStats.get("address");
    const numWordBits = 2;
    const numBlockBits = props.cacheSettings.num_block_bits;
    const numIndexBits = props.cacheSettings.num_index_bits;
    const numTagBits = 32 - numBlockBits - numIndexBits - numWordBits;
    let result = null;
    if (typeof address === "undefined" || address == null) {
        result = {
            wordOffsetBits: " ".repeat(numWordBits),
            blockOffsetBits: " ".repeat(numBlockBits),
            indexBits: " ".repeat(numIndexBits),
            tagBits: " ".repeat(numTagBits),
        };
    } else {
        result = {
            wordOffsetBits: address.slice(
                numTagBits + numIndexBits + numBlockBits
            ),
            blockOffsetBits: address.slice(
                numTagBits + numIndexBits,
                numTagBits + numIndexBits + numBlockBits
            ),
            indexBits: address.slice(numTagBits, numTagBits + numIndexBits),
            tagBits: address.slice(0, numTagBits),
        };
    }
    return result;
});

const tagArrow = computed(() => {
    if (tagCell.value === null) {
        return null;
    }
    const cords = {
        start: {
            x: tagCell.value.offsetWidth / 2 + addressTable.value.offsetLeft,
            y: tagCell.value.offsetHeight + addressTable.value.offsetTop,
        },
        stop: {
            x: tagCell.value.offsetWidth / 2 + addressTable.value.offsetLeft,
            y: tagCell.value.offsetHeight + addressTable.value.offsetTop + 50,
        },
    };
    return cords;
});
</script>

<template>
    <div>
        <p>Hits: {{ props.cacheStats.get("hits") }}</p>
        <p>Misses: {{ misses }}</p>
        <p>Address: {{ props.cacheStats.get("address") }}</p>
        <div class="tables-vis-wrapper">
            <CacheArrows
                class="arrow-layer"
                width="300"
                height="500"
                base-id="riscv-cache-canvas"
                :tag-arrow="tagArrow"
            />
            <div class="tables-wrapper">
                <table
                    ref="addressTable"
                    class="table table-sm table-bordered archsim-mono-table address-table"
                >
                    <tbody>
                        <tr>
                            <td ref="tagCell" v-if="address.tagBits">
                                {{ address.tagBits }}
                            </td>
                            <td ref="indexCell" v-if="address.indexBits">
                                {{ address.indexBits }}
                            </td>
                            <td v-if="address.blockOffsetBits">
                                {{ address.blockOffsetBits }}
                            </td>
                            <td
                                ref="wordOffsetCell"
                                v-if="address.wordOffsetBits"
                            >
                                {{ address.wordOffsetBits }}
                            </td>
                        </tr>
                    </tbody>
                </table>
                <template v-if="props.cacheEntries !== null">
                    <table
                        class="table table-sm table-bordered archsim-mono-table cache-table"
                    >
                        <thead>
                            <tr>
                                <th style="width: 0em">Index</th>
                                <th style="width: 0em">Valid</th>
                                <th v-if="showDirtyBit" style="width: 0em">
                                    Dirty
                                </th>
                                <th
                                    :style="{
                                        width: tagWidth,
                                        minWidth: tagWidth,
                                    }"
                                >
                                    Tag
                                </th>
                                <th v-for="i in blockSize" :style="wordStyle">
                                    Word {{ i }}
                                </th>
                            </tr>
                        </thead>
                        <tbody class="cache-table-body">
                            <template
                                v-for="zet in props.cacheEntries.get('sets')"
                            >
                                <tr v-for="(block, index) in zet.get('blocks')">
                                    <td
                                        v-if="
                                            index %
                                                props.cacheSettings
                                                    .associativity ===
                                            0
                                        "
                                        :rowspan="
                                            props.cacheSettings.associativity
                                        "
                                        class="index"
                                    >
                                        {{ zet.get("index") }}
                                    </td>
                                    <td class="valid">
                                        {{ block.get("valid_bit") }}
                                    </td>
                                    <td v-if="showDirtyBit" class="dirty">
                                        {{ block.get("dirty_bit") }}
                                    </td>
                                    <td class="tag">{{ block.get("tag") }}</td>
                                    <template
                                        v-for="addr_value in block.get(
                                            'address_value_list'
                                        )"
                                    >
                                        <td class="word">
                                            {{ addr_value[1] }}
                                        </td>
                                    </template>
                                </tr>
                            </template>
                        </tbody>
                    </table>
                </template>
            </div>
        </div>
    </div>
</template>

<style scoped>
.tables-vis-wrapper {
    position: relative;
}

.arrow-layer {
    position: absolute;
    left: 0;
    top: 0;
    z-index: 2;
}

.tables-wrapper {
    padding-left: 4em;
    position: absolute;
    left: 0;
    top: 0;
    z-index: 1;
}
.cache-table {
    margin-bottom: 0em;
    width: auto;
}

.address-table {
    width: auto;
    white-space: pre;
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
