<script setup>
import { computed } from "vue";

const props = defineProps(["simulationStore"]);

const stuff = computed(() => {
    return props.simulationStore.dataCacheEntries;
});
</script>

<template>
    <template v-if="props.simulationStore.dataCacheEntries !== null">
        Cache
        <table>
            <template
                v-for="zet in props.simulationStore.dataCacheEntries.sets"
            >
                <tr v-for="block in zet.blocks">
                    <td>index: {{ zet.index }}</td>
                    <td>valid: {{ block.valid_bit }}</td>
                    <td>dirty: {{ block.dirty_bit }}</td>
                    <td>tag: {{ block.tag }}</td>
                    <template v-for="addr_value in block.address_value_list">
                        <td>data: {{ addr_value[1] }}</td>
                    </template>
                </tr>
            </template>
        </table>
    </template>
</template>

<style scoped></style>
