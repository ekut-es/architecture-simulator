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
const replacementStatus = ref(null);

const canvasWidth = ref(0);
const canvasHeight = ref(0);
let resizeObserver = null;
let highlightedTagCell = null;
let highlightedWordCell = null;

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

function highlightTagCell(cell) {
    if (highlightedTagCell !== null) {
        highlightedTagCell.classList.remove("archsim-cache-highlight");
    }

    if (cell !== null) {
        highlightedTagCell = cell;
        cell.classList.add("archsim-cache-highlight");
    }
}

function highlightWordCell(cell, hit) {
    if (highlightedWordCell !== null) {
        highlightedWordCell.classList.remove(
            "archsim-cache-hit",
            "archsim-cache-miss"
        );
    }

    if (cell !== null) {
        const clazz = hit ? "archsim-cache-hit" : "archsim-cache-miss";
        highlightedWordCell = cell;
        cell.classList.add(clazz);
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

            highlightTagCell(null);
            highlightWordCell(null, true);

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

            if (!isNaN(targetTag)) {
                // See if there is a block with the correct tag
                nextTick(() => {
                    const rowOffset =
                        1 +
                        (isNaN(targetIndex) ? 0 : targetIndex * associativity);
                    let tagCell = null;
                    for (let i = 0; i < associativity; i++) {
                        const row = cacheTable.value.rows[i + rowOffset];
                        const currentCell = row.querySelector(".tag");
                        const tag =
                            currentCell.innerText === ""
                                ? null
                                : Number(currentCell.innerText);
                        if (targetTag === tag) {
                            tagCell = currentCell;
                            highlightTagCell(tagCell);
                            break;
                        }
                    }
                    // Make the correct cell green/red for hit/miss
                    if (tagCell !== null) {
                        const hit = props.cacheStats.get("last_hit");
                        const blockOffset = isNaN(targetBlockOffset)
                            ? 0
                            : targetBlockOffset;
                        const wordCell =
                            tagCell.parentNode.querySelectorAll(".word")[
                                blockOffset
                            ];
                        highlightWordCell(wordCell, hit);
                    }
                });
            }

            replacementStatus.value = [];
            for (const set of props.cacheEntries.sets) {
                replacementStatus.value.push(set.replacement_status);
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
                :index-start-cell
                :index-end-cell
                :block-offset-start-cell
                :block-offset-end-cell
                :cache-table
                :cache-settings="props.cacheSettings"
                :replacement-status
            />
            <div ref="tablesWrapper" class="tables-wrapper">
                <div class="mb-1">
                    Address:
                    <template v-if="props.cacheStats.get('address')">
                        <span
                            v-if="props.cacheStats.get('last_hit')"
                            class="badge archsim-cache-hit"
                        >
                            Hit
                        </span>
                        <span v-else class="badge archsim-cache-miss">
                            Miss
                        </span>
                    </template>
                </div>
                <table
                    ref="addressTable"
                    class="table table-sm table-bordered archsim-mono-table address-table"
                >
                    <tbody>
                        <tr>
                            <td ref="tagCell">
                                {{ address.tagBits }}
                            </td>
                            <td ref="indexCell" v-show="address.indexBits">
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
                        <template v-for="zet in props.cacheEntries.sets">
                            <tr v-for="(block, index) in zet.blocks">
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
                                    {{ zet.index }}
                                </td>
                                <td class="valid">
                                    {{ block.valid_bit }}
                                </td>
                                <td v-if="showDirtyBit" class="dirty">
                                    {{ block.dirty_bit }}
                                </td>
                                <td v-if="showLRU" class="lru">
                                    {{ zet.replacement_status.get(index) }}
                                </td>
                                <td class="tag">{{ block.tag }}</td>
                                <template
                                    v-for="addr_value in block.address_value_list"
                                >
                                    <td class="word">
                                        {{ addr_value.get(1) }}
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
