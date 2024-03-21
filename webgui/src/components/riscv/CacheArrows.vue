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
    "cacheSettings",
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
        const yIntermediate = Math.round(table.y * 0.4 + start.y * 0.6); // between address and cache tables
        const xIntermediate = Math.round(table.x / 2); // between the start of the canvas and the cache table
        ctx.moveTo(start.x, start.y);
        ctx.lineTo(start.x, yIntermediate); // move halfway down to the cache table
        ctx.lineTo(xIntermediate, yIntermediate); // go to the left
        ctx.lineTo(xIntermediate, dest.y); // go fully down
        ctx.lineTo(dest.x, dest.y); // go to the right to connect to the table
        ctx.stroke();
        ctx.beginPath(); // draw an arrowhead
        ctx.moveTo(dest.x, dest.y);
        ctx.lineTo(dest.x - 10, dest.y - 5);
        ctx.lineTo(dest.x - 10, dest.y + 5);
        ctx.closePath();
        ctx.fill();
    }

    if (
        exists(props.blockOffsetStartCell) &&
        exists(props.blockOffsetEndCell)
    ) {
        ctx.beginPath();
        const start = computeOffset(props.blockOffsetStartCell, 0.5, 1);
        const dest = computeOffset(props.blockOffsetEndCell, 0.5, 0);
        const yIntermediate = Math.round(dest.y * 0.6 + start.y * 0.4); // between address and cache tables
        ctx.moveTo(start.x, start.y);
        ctx.lineTo(start.x, yIntermediate); // move halfway down
        ctx.lineTo(dest.x, yIntermediate); // move sideways
        ctx.lineTo(dest.x, dest.y); // move fully down
        ctx.stroke();
        ctx.beginPath(); // draw an arrowhead
        ctx.moveTo(dest.x, dest.y);
        ctx.lineTo(dest.x + 5, dest.y - 10);
        ctx.lineTo(dest.x - 5, dest.y - 10);
        ctx.closePath();
        ctx.fill();
    }

    if (props.cacheSettings.replacement_strategy === "plru") {
        const table = props.cacheTable;
        const associativity = props.cacheSettings.associativity;
        const sets = Math.pow(2, props.cacheSettings.num_index_bits);
        for (let i = 0; i < sets; i++) {
            const rowStartIdx = 1 + i * associativity;
            const rowEndIdx = 1 + (i + 1) * associativity;
            const rows = [...table.rows].slice(rowStartIdx, rowEndIdx);
            const rowCoordinates = rows.map((row) =>
                computeOffset(row, 0, 0.5)
            );
            drawPlruTree(ctx, rowCoordinates);
        }
    }
}

const branchWidth = 25;
const fontSize = 16;

function drawPlruTree(ctx, coordinates) {
    let coords = structuredClone(coordinates);
    let bitPositions = [];
    while (coords.length > 1) {
        let newCoords = [];
        for (let i = 0; i < coords.length; i += 2) {
            const branchOrigin = drawPlruBranch(
                ctx,
                coords[i].x,
                coords[i].y,
                coords[i + 1].y
            );
            newCoords.push(branchOrigin);
        }
        bitPositions = newCoords.concat(bitPositions);
        coords = newCoords;
    }

    for (const bitPosition of bitPositions) {
        drawPlruBit(ctx, bitPosition.x, bitPosition.y, "1");
    }
}

function drawPlruBranch(ctx, x, y1, y2) {
    const intermediate = { x: x - branchWidth, y: (y1 + y2) / 2 };
    ctx.beginPath();
    ctx.moveTo(x, y1);
    ctx.lineTo(intermediate.x, intermediate.y);
    ctx.lineTo(x, y2);
    ctx.stroke();
    return intermediate;
}

function drawPlruBit(ctx, x, y, value) {
    const topLeft = { x: x - fontSize / 2, y: y - fontSize / 2 };
    ctx.clearRect(topLeft.x, topLeft.y, fontSize, fontSize);
    ctx.font = `${fontSize}px monospace`;
    ctx.textBaseline = "middle";
    ctx.textAlign = "center";
    ctx.fillText(value, x, y);
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
        x: Math.round(elRect.left - selfRect.left + hOffset),
        y: Math.round(elRect.top - selfRect.top + vOffset),
    };
}
</script>

<template>
    <canvas ref="canvas" id="baseId"></canvas>
</template>

<style scoped></style>
