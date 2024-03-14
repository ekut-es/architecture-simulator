<script setup>
import { ref, watch } from "vue";

const props = defineProps([
    "width",
    "height",
    "baseId",
    "indexStartCell",
    "indexEndCell",
    "blockOffsetStartCell",
    "blockOffsetEndCell",
    "cacheTable",
]);
const canvas = ref(null);

watch(props, drawCanvas);

function drawCanvas() {
    const ctx = canvas.value.getContext("2d");
    canvas.value.width = props.width;
    canvas.value.height = props.height;
    ctx.clearRect(0, 0, props.width, props.height);

    if (exists(props.indexStartCell) && exists(props.indexEndCell)) {
        ctx.beginPath();
        const start = computeOffset(props.indexStartCell, 0.5, 1);
        const dest = computeOffset(props.indexEndCell, 0, 0.5);
        const table = computeOffset(props.cacheTable, 0, 0); // top left corner of the whole cache table
        const yCenter = table.y / 2 + start.y / 2; // vertical center between address and cache tables
        const xCenter = table.x / 2; // horizontal center between the start of the canvas and the cache table
        ctx.moveTo(start.x, start.y);
        ctx.lineTo(start.x, yCenter); // move halfway down to the cache table
        ctx.lineTo(xCenter, yCenter); // go to the left
        ctx.lineTo(xCenter, dest.y); // go fully down
        ctx.lineTo(dest.x, dest.y); // go to the right to connect to the table
        ctx.stroke();
    }

    if (
        exists(props.blockOffsetStartCell) &&
        exists(props.blockOffsetEndCell)
    ) {
        ctx.beginPath();
        const start = computeOffset(props.blockOffsetStartCell, 0.5, 1);
        const dest = computeOffset(props.blockOffsetEndCell, 0.5, 0);
        const yCenter = dest.y / 2 + start.y / 2; // vertical center between address and cache tables
        ctx.moveTo(start.x, start.y);
        ctx.lineTo(start.x, yCenter); // move halfway down
        ctx.lineTo(dest.x, yCenter); // move sideways
        ctx.lineTo(dest.x, dest.y); // move fully down
        ctx.stroke();
    }
}

function exists(x) {
    return typeof x !== "undefined" && x !== null;
}

function computeOffset(el, relHOffset = 0, relVOffset = 0) {
    const selfRect = canvas.value.getBoundingClientRect();
    const elRect = el.getBoundingClientRect();
    let hOffset = elRect.width * relHOffset;
    let vOffset = elRect.height * relVOffset;

    return {
        x: elRect.left - selfRect.left + hOffset,
        y: elRect.top - selfRect.top + vOffset,
    };
}
</script>

<template>
    <canvas ref="canvas" id="baseId"></canvas>
</template>

<style scoped></style>
