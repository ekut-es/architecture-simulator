<script setup>
const props = defineProps({ instructions: Array });
const fields = ["Instruction", "Operation", "Notes", "Format"];
</script>
<template>
    <table class="table table-bordered">
        <thead>
            <tr>
                <th v-for="field in fields">
                    {{ field }}
                </th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="item in props.instructions">
                <td v-for="field in fields">
                    <code
                        v-if="field == 'Instruction' || field == 'Operation'"
                        style="white-space: pre"
                    >
                        {{ item[field] }}
                    </code>
                    <div v-else>{{ item[field] }}</div>
                </td>
            </tr>
        </tbody>
    </table>
</template>
