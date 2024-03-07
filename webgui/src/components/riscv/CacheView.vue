<script setup>
const props = defineProps(["simulationStore"]);
</script>

<template>
    <template v-if="props.simulationStore.dataCacheEntries !== null">
        Cache
        <table>
            <template
                v-for="zet in props.simulationStore.dataCacheEntries.get(
                    'sets'
                )"
            >
                <tr v-for="block in zet.get('blocks')">
                    <td>index: {{ zet.get("index") }}</td>
                    <td>valid: {{ block.get("valid_bit") }}</td>
                    <td>dirty: {{ block.get("dirty_bit") }}</td>
                    <td>tag: {{ block.get("tag") }}</td>
                    <template
                        v-for="addr_value in block.get('address_value_list')"
                    >
                        <td>data: {{ addr_value[1] }}</td>
                    </template>
                </tr>
            </template>
        </table>
    </template>
</template>

<style scoped></style>
