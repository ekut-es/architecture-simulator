<script setup>
import { computed } from "vue";

const props = defineProps(["cacheEntries", "cacheSettings"]);
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

const wordWidth = "12ch";
</script>

<template>
    <div>
        <template v-if="props.cacheEntries !== null">
            <table
                class="table table-sm table-bordered archsim-mono-table cache-table"
            >
                <thead>
                    <tr>
                        <th style="width: 0em">Index</th>
                        <th style="width: 0em">Valid</th>
                        <th style="width: 0em">Dirty</th>
                        <th :style="{ width: tagWidth, minWidth: tagWidth }">
                            Tag
                        </th>
                        <th
                            v-for="i in blockSize"
                            :style="{ width: wordWidth, minWidth: wordWidth }"
                        >
                            Word {{ i }}
                        </th>
                    </tr>
                </thead>
                <tbody class="cache-table-body">
                    <template v-for="zet in props.cacheEntries.get('sets')">
                        <tr v-for="block in zet.get('blocks')">
                            <td>{{ zet.get("index") }}</td>
                            <td>{{ block.get("valid_bit") }}</td>
                            <td>{{ block.get("dirty_bit") }}</td>
                            <td>{{ block.get("tag") }}</td>
                            <template
                                v-for="addr_value in block.get(
                                    'address_value_list'
                                )"
                            >
                                <td>{{ addr_value[1] }}</td>
                            </template>
                        </tr>
                    </template>
                </tbody>
            </table>
        </template>
    </div>
</template>

<style scoped>
.cache-table-body > tr > td {
    text-align: right;
}

.cache-table-body > tr > td:nth-child(2),
.cache-table-body > tr > td:nth-child(3) {
    text-align: center;
}

.cache-table {
    margin-bottom: 0em;
    width: auto;
}
</style>
