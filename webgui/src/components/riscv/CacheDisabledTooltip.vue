<script setup>
import IconTooltip from "../IconTooltip.vue";
const message =
    "The cache visualization was disabled because the cache size is too big.";
</script>
<template>
    <IconTooltip
        :message
        icon-name="bi-info-circle-fill"
        class="text-primary"
    ></IconTooltip>
</template>
