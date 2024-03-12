<script setup>
import { onMounted, ref, watch } from "vue";

const props = defineProps(["height", "width", "baseId", "tagArrow"]);
const canvas = ref(null);

onMounted(drawCanvas);
watch(
    () => [props.height, props.width, props.tagArrow],
    (x) => {
        drawCanvas();
    }
);

function drawCanvas() {
    const ctx = canvas.value.getContext("2d");

    let cords = props.tagArrow;
    if (cords === null) {
        return;
    }
    ctx.beginPath();
    ctx.moveTo(cords.start.x, cords.start.y);
    ctx.lineTo(cords.stop.x, cords.stop.y);
    ctx.stroke();
}
</script>

<template>
    <canvas
        ref="canvas"
        id="baseId"
        :width="props.width"
        :height="props.height"
    ></canvas>
</template>

<style scoped></style>
