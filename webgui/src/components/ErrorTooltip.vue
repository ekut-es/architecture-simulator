<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";
import { Tooltip } from "bootstrap";

const props = defineProps(["message"]);

const tooltipElement = ref(null);
let tooltipObject = null;
onMounted(() => {
    const msg = props.message;
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
        :data-bs-title="props.message"
        class="ms-2 text-danger"
    >
        <i class="bi bi-exclamation-triangle-fill"></i>
        Error
    </span>
</template>
