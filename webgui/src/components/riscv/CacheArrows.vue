<!-- A canvas that draws all the arrows for the cache -->
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
    "replacementStatus",
    "plruTreeGap",
    "plruBranchWidth",
]);

const canvas = ref(null);

/** Distance of the vertical index arrow line to the table */
const indexArrowGap = 20;
/** Font size for the PLRU tree bits */
const fontSize = 16;

watch(props, drawCanvas);

/**
 * Clears and redraws the entire canvas.
 */
function drawCanvas() {
    const ctx = canvas.value.getContext("2d");
    canvas.value.width = props.width;
    canvas.value.height = props.height;
    ctx.clearRect(0, 0, props.width, props.height);

    // Draw the index arrow
    if (exists(props.indexStartCell) && exists(props.indexEndCell)) {
        ctx.beginPath();
        const start = computeOffset(props.indexStartCell, 0.5, 1);
        const dest = computeOffset(props.indexEndCell, 0, 0.5);
        const table = computeOffset(props.cacheTable, 0, 0); // top left corner of the whole cache table
        const yIntermediate = Math.round(table.y * 0.4 + start.y * 0.6); // between address and cache tables
        const xIntermediate = table.x - indexArrowGap; // between the start of the canvas and the cache table
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

    // Draw the block offset arrow
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

    // Draw the PLRU trees
    if (
        props.cacheSettings.showPlruTree &&
        props.cacheSettings.replacement_strategy === "plru"
    ) {
        const table = props.cacheTable;
        const associativity = props.cacheSettings.associativity;
        const sets = Math.pow(2, props.cacheSettings.num_index_bits);
        // draw a tree for each set
        for (let i = 0; i < sets; i++) {
            const rowStartIdx = 1 + i * associativity;
            const rowEndIdx = 1 + (i + 1) * associativity;
            // get all the rows of that set and get their coordinates
            const rows = [...table.rows].slice(rowStartIdx, rowEndIdx);
            const rowCoordinates = rows.map((row) => {
                const cellStart = computeOffset(row, 0, 0.5);
                return { x: cellStart.x - props.plruTreeGap, y: cellStart.y };
            });
            drawPlruTree(ctx, rowCoordinates, i);
        }
    }
}

/**
 * Draws one PLRU tree for the rows that start at the given coordinates
 * (should be the coordinates of the table rows)
 *
 * @param {CanvasRenderingContext2D} ctx 2d canvas context
 * @param {Array} coordinates Array of objects with x and y entries.
 * @param {Number} setIdx The index of the set that is being drawn.
 */
function drawPlruTree(ctx, coordinates, setIdx) {
    // the coordinates for all nodes in one layer
    let coords = structuredClone(coordinates); // clone just for good meassure
    let bitPositions = []; // the positions of the non-leaf nodes where the bits need to be drawn
    // repeat the drawing until only one node is left
    while (coords.length > 1) {
        let newCoords = [];
        for (let i = 0; i < coords.length; i += 2) {
            // draw a branch spanning two nodes and remember the parent coordinates
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

    // draw the bits
    for (const [bitIndex, bitPosition] of bitPositions.entries()) {
        const bit = props.replacementStatus[setIdx].get(bitIndex) ? "1" : "0";
        drawPlruBit(ctx, bitPosition.x, bitPosition.y, bit);
    }
}

/**
 * Draws a branch and returns the coordinates of the parent
 * @param {CanvasRenderingContext2D} ctx 2d canvas context
 * @param {Number} x x coordinate of the leaves
 * @param {Number} y1 y coordinate of the first leaf
 * @param {Number} y2 y coordinate of the second leaf
 *
 * @returns {object} Parent coordinates in the x and y entries
 */
function drawPlruBranch(ctx, x, y1, y2) {
    const intermediate = { x: x - props.plruBranchWidth, y: (y1 + y2) / 2 };
    ctx.beginPath();
    ctx.moveTo(x, y1);
    ctx.lineTo(intermediate.x, intermediate.y);
    ctx.lineTo(x, y2);
    ctx.stroke();
    return intermediate;
}

/**
 * Draws the string at the given position (both horizontally and vertically centered)
 * @param {CanvasRenderingContext2D} ctx 2d canvas context
 * @param {Number} x x coordinate
 * @param {Number} y y coordinate
 * @param {String} value String to draw
 */
function drawPlruBit(ctx, x, y, value) {
    const topLeft = { x: x - fontSize / 2, y: y - fontSize / 2 };
    // clear a square around the bit so you can actually read it
    ctx.clearRect(topLeft.x, topLeft.y, fontSize, fontSize);
    ctx.font = `${fontSize}px monospace`;
    ctx.textBaseline = "middle";
    ctx.textAlign = "center";
    ctx.fillText(value, x, y);
}

/**
 * Returns true if the variable is defined and not null.
 * @param {any} x variable to test
 */
function exists(x) {
    return typeof x !== "undefined" && x !== null;
}

/**
 * Get the coordinates of the given element relative to the canvas.
 * @param {HTMLElement} el The element.
 * @param {Number} relHOffset Add a horizontal offset to x that is relative to the nodes width.
 * @param {Number} relVOffset Add a vertical offset to y that is relative to the nodes height.
 *
 * @returns {object} The x and y coordinates.
 */
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
