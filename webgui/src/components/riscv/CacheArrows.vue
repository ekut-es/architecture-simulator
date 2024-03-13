<script setup>
import { onMounted, ref, watch } from "vue";

const props = defineProps([
    "width",
    "height",
    "baseId",
    "indexStartCell",
    "indexEndCell",
    "blockOffsetStartCell",
    "blockOffsetEndCell",
]);
const canvas = ref(null);

const width = ref(props.width);
const height = ref(props.width);

onMounted(drawCanvas);
watch(props, (p) => {
    width.value = p.width;
    height.value = p.height;
    drawCanvas();
});

function drawCanvas() {
    const ctx = canvas.value.getContext("2d");
    ctx.clearRect(0, 0, width.value, height.value);

    if (exists(props.indexStartCell) && exists(props.indexEndCell)) {
        ctx.beginPath();
        let xy = computeOffset(props.indexStartCell);
        ctx.moveTo(xy.x, xy.y);
        xy = computeOffset(props.indexEndCell);
        ctx.lineTo(xy.x, xy.y);
        ctx.stroke();
    }

    if (
        exists(props.blockOffsetStartCell) &&
        exists(props.blockOffsetEndCell)
    ) {
        ctx.beginPath();
        let xy = computeOffset(props.blockOffsetStartCell);
        ctx.moveTo(xy.x, xy.y);
        xy = computeOffset(props.blockOffsetEndCell);
        ctx.lineTo(xy.x, xy.y);
        ctx.stroke();
    }
}

function exists(x) {
    return typeof x !== "undefined" && x !== null;
}

function computeOffset(el) {
    const selfRect = canvas.value.getBoundingClientRect();
    const elRect = el.getBoundingClientRect();
    return { x: elRect.left - selfRect.left, y: elRect.top - selfRect.top };
}
</script>

<template>
    <canvas ref="canvas" id="baseId" :width="width" :height="height"></canvas>
</template>

<style scoped></style>
