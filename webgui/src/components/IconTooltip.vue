<!-- A bootstrap tooltip component with an icon and text. -->
<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { Tooltip } from "bootstrap";

const props = defineProps(["message", "iconName"]);

// dynamically change the content of the tooltip
watch(
    () => props.message,
    (msg) => {
        tooltipObject.setContent({ ".tooltip-inner": msg });
    }
);

const initialMessage = props.message;

const tooltipElement = ref(null);
let tooltipObject = null;
onMounted(() => {
    tooltipObject = new Tooltip(tooltipElement.value);
});

onBeforeUnmount(() => {
    tooltipObject.hide();
});
</script>

<template>
    <span
        ref="tooltipElement"
        data-bs-toggle="tooltip"
        data-bs-trigger="hover click focus"
        data-bs-animation="false"
        :data-bs-title="initialMessage"
    >
        <i :class="'bi ' + props.iconName"></i>
        <slot></slot>
    </span>
</template>
