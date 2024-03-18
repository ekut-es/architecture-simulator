<script setup>
import IconTooltip from "./IconTooltip.vue";

const props = defineProps(["message"]);
</script>

<template>
    <IconTooltip
        :message="message"
        icon-name="bi-exclamation-triangle-fill"
        class="text-danger"
    >
        Error
    </IconTooltip>
</template>
