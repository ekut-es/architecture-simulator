<script setup>
const props = defineProps(["cache"]);
</script>

<template>
    <table>
        <template v-if="props.cache">
            <template v-for="zet in props.cache.sets">
                <tr v-for="block in zet.blocks">
                    <td>{{ zet.index }}</td>
                    <td>{{ block.valid_bit }}</td>
                    <td>{{ block.dirty_bit }}</td>
                    <template v-for="addr_value in block.address_value_list">
                        <td>{{ addr_value[0] }}</td>
                        <td>{{ addr_value[1] }}</td>
                    </template>
                </tr>
            </template>
        </template>
    </table>
</template>

<style scoped></style>
