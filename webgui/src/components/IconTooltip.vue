<!-- A bootstrap tooltip component with an icon and text. -->
<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";
import { Tooltip } from "bootstrap";

const props = defineProps(["message", "iconName"]);

const tooltipElement = ref(null);
let tooltipObject = null;
onMounted(() => {
    const msg = props.message;
    tooltipObject = new Tooltip(tooltipElement.value);
});

onBeforeUnmount(() => {
    // You need to hide the tooltip before removing it from the DOM, apparently.
    // This should always be the case, but lets do it here anyway (not sure if I'm doing it correctly though).
    tooltipObject.hide();
});
</script>

<template>
    <span
        ref="tooltipElement"
        data-bs-toggle="tooltip"
        data-bs-trigger="hover click focus"
        :data-bs-title="props.message"
        class="ms-2"
    >
        <i :class="'bi ' + props.iconName"></i>
        <slot></slot>
    </span>
</template>
