<!-- A checkbox button that shall be used in a button group for toggling the visibility of elements. -->
<script setup>
/**
 * The ref that holds the show-state of the respective element.
 */
const setting = defineModel();
/**
 * baseId: unique id so that the button knows what label it is for.
 */
const props = defineProps({ baseId: String });

// used for making the button (un-)checked by default.
const checked = setting.value;
</script>

<template>
    <input
        type="checkbox"
        class="btn-check"
        :id="baseId"
        autocomplete="off"
        :checked="checked"
        v-model="setting"
    />
    <label class="btn btn-outline-primary" :for="baseId">
        <slot></slot>
    </label>
</template>
