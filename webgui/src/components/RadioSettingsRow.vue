<!-- Creates a row with radio buttons for the settings page -->

<script setup>

/**
 * The ref that holds the variable that this setting shall modify.
 */
const setting = defineModel();

/**
 * optionNames: the names that will be displayed next to the buttons
 * optionValues: the values that the buttons shall have
 * baseId: some unique id that will be used so the buttons know which label they belong to
 * defaultSelction: the value of the button that shall be selected by default
 * displayName: the name to display to the left of the buttons
 */
const props = defineProps({ "optionNames": Array, "optionValues": Array, "baseId": String, "defaultSelection": String, "displayName": String });

/**
 * Zips two arrays together.
 * @param {Array} a
 * @param {Array} b
 */
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
