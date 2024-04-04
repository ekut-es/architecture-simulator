<!-- An icon that will show the performance metrics on hover or click. -->
<script setup>
import { computed } from "vue";

import IconTooltip from "./IconTooltip.vue";

const props = defineProps(["simulationStore", "additionalMessageGetter"]);

let output = computed(() => {
    let message = props.simulationStore.performanceMetricsStr;
    if (typeof props.additionalMessageGetter !== "undefined") {
        message += props.additionalMessageGetter();
    }
    return message;
});
</script>

<template>
    <IconTooltip
        data-bs-custom-class="archsim-performance-metrics-tooltip"
        data-bs-placement="bottom"
        :message="output"
        icon-name="bi-speedometer"
    />
</template>
