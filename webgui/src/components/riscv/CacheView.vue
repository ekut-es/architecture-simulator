<script setup>
import { riscvSettings } from "@/js/riscv_settings";
import { computed } from "vue";

const props = defineProps(["simulationStore"]);
const blockSize = computed(() =>
    Math.pow(2, riscvSettings.dataCache.value.num_block_bits)
);
</script>

<template>
    <template v-if="props.simulationStore.dataCacheEntries !== null">
        <table class="table table-sm table-bordered archsim-mono-table">
            <thead>
                <tr>
                    <th>Index</th>
                    <th>Valid</th>
                    <th>Dirty</th>
                    <th>Tag</th>
                    <th v-for="i in blockSize">Word {{ i }}</th>
                </tr>
            </thead>
            <tbody class="cache-table-body">
                <template
                    v-for="zet in props.simulationStore.dataCacheEntries.get(
                        'sets'
                    )"
                >
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
</template>

<style scoped>
.cache-table-body > tr > td {
    text-align: right;
}

.cache-table-body > tr > td:nth-child(2),
.cache-table-body > tr > td:nth-child(3) {
    text-align: center;
}
</style>
