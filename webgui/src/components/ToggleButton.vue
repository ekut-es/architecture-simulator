<script setup>
import { watchEffect } from 'vue';

const setting = defineModel();
const props = defineProps({ baseId: String });
const checked = setting.value;
</script>

<template>
    <input type="checkbox" class="btn-check" :id="baseId" autocomplete="off" :checked="checked" v-model="setting">
    <label class="btn btn-outline-primary" :for="baseId">
        <slot></slot>
    </label>
</template>
