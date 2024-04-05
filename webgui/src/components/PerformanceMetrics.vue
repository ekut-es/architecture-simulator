<!-- An icon that will show the performance metrics on hover or click. -->
<script setup>
import { computed } from "vue";

import IconTooltip from "./IconTooltip.vue";

const props = defineProps(["simulationStore", "additionalMessageGetter"]);

const options = {
    animation: false, // prevents flickering when updating the content
    placement: "bottom",
    fallbackPlacements: ["bottom"],
    customClass: "archsim-performance-metrics-tooltip",
};

let output = computed(() => {
    let message = props.simulationStore.performanceMetricsStr;
    if (typeof props.additionalMessageGetter !== "undefined") {
        message += props.additionalMessageGetter();
    }
    return message;
});
</script>

<template>
    <IconTooltip :options :message="output" icon-name="bi-speedometer" />
</template>
