<script setup>
import CacheArrows from "./CacheArrows.vue";
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";

const tagCell = ref(null);
const indexCell = ref(null);
const blockOffsetCell = ref(null);
const wordOffsetCell = ref(null);

const tablesWrapper = ref(null);
const addressTable = ref(null);
const cacheTable = ref(null);

// props for the arrows
const indexStartCell = ref(null);
const indexEndCell = ref(null);
const blockOffsetStartCell = ref(null);
const blockOffsetEndCell = ref(null);

const canvasWidth = ref(0);
const canvasHeight = ref(0);
let resizeObserver = null;
let highlightedCell = null;

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
const showLRU = computed(
    () => props.cacheSettings.replacement_strategy === "lru"
);

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

function updateCanvasSize() {
    canvasWidth.value = tablesWrapper.value.offsetWidth;
    canvasHeight.value = tablesWrapper.value.offsetHeight;
}

function highlightCell(cell) {
    if (highlightedCell !== null) {
        highlightedCell.classList.remove("archsim-cache-highlight");
    }

    if (cell !== null) {
        highlightedCell = cell;
        cell.classList.add("archsim-cache-highlight");
    }
}

onMounted(() => {
    watch(
        address,
        (addr) => {
            const targetTag = parseInt(addr.tagBits, 2);
            const targetIndex = parseInt(addr.indexBits, 2);
            const targetBlockOffset = parseInt(addr.blockOffsetBits, 2);
            const blockSize = Math.pow(2, props.cacheSettings.num_block_bits);
            const associativity = props.cacheSettings.associativity;

            highlightCell(null);

            indexStartCell.value = null;
            indexEndCell.value = null;
            blockOffsetStartCell.value = null;
            blockOffsetEndCell.value = null;

            if (!isNaN(targetIndex)) {
                indexStartCell.value = indexCell.value;
                indexEndCell.value =
                    cacheTable.value.rows[
                        targetIndex * associativity + 1
                    ].cells[0];
            }
            if (!isNaN(targetBlockOffset)) {
                const header = cacheTable.value.rows[0];
                blockOffsetStartCell.value = blockOffsetCell.value;
                blockOffsetEndCell.value =
                    header.cells[
                        header.cells.length - blockSize + targetBlockOffset
                    ];
            }
            if (!isNaN(targetIndex)) {
                // See if there is a block with the correct tag
                nextTick(() => {
                    for (let i = 0; i < associativity; i++) {
                        const row =
                            cacheTable.value.rows[
                                i + targetIndex * associativity + 1
                            ];
                        const cell = row.querySelector(".tag");
                        const tag = Number(cell.innerText);
                        if (targetTag === tag) {
                            highlightCell(cell);
                            break;
                        }
                    }
                });
            }
        },
        { immediate: true }
    );

    // watch for resizes (be it by changing the cache config, zooming or whatever)
    resizeObserver = new ResizeObserver(updateCanvasSize);
    resizeObserver.observe(tablesWrapper.value);
});

onUnmounted(() => {
    if (resizeObserver !== null) {
        resizeObserver.disconnect();
    }
});
</script>

<template>
    <div>
        <span class="badge text-bg-secondary me-3 stats-badge"
            >Hits: {{ props.cacheStats.get("hits") }}</span
        >
        <span class="badge text-bg-secondary mb-3 stats-badge"
            >Misses: {{ misses }}</span
        >
        <div
            class="tables-vis-wrapper"
            :width="canvasWidth"
            :height="canvasHeight"
        >
            <CacheArrows
                class="arrow-layer"
                :width="canvasWidth"
                :height="canvasHeight"
                base-id="riscv-cache-canvas"
                :index-start-cell="indexStartCell"
                :index-end-cell="indexEndCell"
                :block-offset-start-cell="blockOffsetStartCell"
                :block-offset-end-cell="blockOffsetEndCell"
                :cache-table="cacheTable"
            />
            <div ref="tablesWrapper" class="tables-wrapper">
                Address:
                <table
                    ref="addressTable"
                    class="table table-sm table-bordered archsim-mono-table address-table"
                >
                    <tbody>
                        <tr>
                            <td ref="tagCell">
                                {{ address.tagBits }}
                            </td>
                            <td ref="indexCell">
                                {{ address.indexBits }}
                            </td>
                            <td
                                ref="blockOffsetCell"
                                v-show="address.blockOffsetBits"
                            >
                                {{ address.blockOffsetBits }}
                            </td>
                            <td ref="wordOffsetCell">
                                {{ address.wordOffsetBits }}
                            </td>
                        </tr>
                    </tbody>
                </table>
                <table
                    ref="cacheTable"
                    class="table table-sm table-bordered archsim-mono-table cache-table"
                >
                    <thead>
                        <tr>
                            <th style="width: 0em">Index</th>
                            <th style="width: 0em">Valid</th>
                            <th v-if="showDirtyBit" style="width: 0em">
                                Dirty
                            </th>
                            <th v-if="showLRU">LRU</th>
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
                        <template v-for="zet in props.cacheEntries.get('sets')">
                            <tr v-for="(block, index) in zet.get('blocks')">
                                <td
                                    v-if="
                                        index %
                                            props.cacheSettings
                                                .associativity ===
                                        0
                                    "
                                    :rowspan="props.cacheSettings.associativity"
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
                                <td v-if="showLRU" class="lru">
                                    {{ zet.get("replacement_status")[index] }}
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
            </div>
        </div>
    </div>
</template>

<style scoped>
.stats-badge {
    min-width: 8em;
}
.tables-vis-wrapper {
    position: relative;
}

.arrow-layer {
    position: absolute;
    left: 0;
    top: 0;
    z-index: 1;
}

.tables-wrapper {
    padding-left: 4em;
    position: absolute;
    left: 0;
    top: 0;
    z-index: 2;
}
.cache-table {
    margin-bottom: 0em;
    width: auto;
}

.address-table {
    width: auto;
    white-space: pre;
    margin-bottom: 4em;
}

.index {
    vertical-align: middle;
    text-align: right;
}

.valid,
.dirty,
.lru {
    text-align: center;
}

.tag,
.word {
    text-align: right;
}
</style>
