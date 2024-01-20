<script setup>
const setting = defineModel();
const props = defineProps({ "optionNames": Array, "optionValues": Array, "baseId": String, "defaultSelection": String, "displayName": String });
const zip = (a, b) => a.map((e, i) => [e, b[i]]);
</script>

<template>
    <div class="row">
        <div class="col-4">
            <h3 class="fs-6"> {{ props.displayName }} </h3>
        </div>
        <div :id="props.baseId + '-container'" class="col-8">
            <template v-for="[optionName, optionValue] in zip(props.optionNames, props.optionValues)">
                <label :for="props.baseId + '-' + optionValue" class="pe-2">
                    <input type="radio" :id="props.baseId + '-' + optionValue" :name="props.baseId + '-group'"
                        :value="optionValue" :checked="optionValue == props.defaultSelection" v-model="setting" />
                    {{ optionName }}
                </label>
            </template>
        </div>
    </div>
</template>
