<script setup>
import { watch } from "vue";

const props = defineProps(["path", "simulationStore"]);

const path = props.path;

const simulationStore = props.simulationStore;

/**
 * The svg itself (contentDocument of the object element). This is where
 * modifications to the svg can be made. Will be undefined before
 * the svg has finished loading.
 */
let svg;

function svgLoaded(event) {
    svg = event.target.contentDocument;
    updateVisualization(simulationStore.svgDirectives);
    watch(() => simulationStore.svgDirectives, (updateValues) => { updateVisualization(updateValues); });
}

function updateVisualization(updateValues) {
    for (let i = 0; i < updateValues.length; i++) {
        const update = updateValues[i];
        const id = update[0];
        const action = update[1];
        const value = update[2];
        switch (action) {
            case "highlight":
                toySvgHighlight(id, value);
                break;
            case "write":
                toySvgSetText(id, value);
                break;
            case "show":
                toySvgShow(id, value);
                break;
        }
    }
}

/**
 * Sets the fill color of an element.
 * @param {string} id target id.
 * @param {string} color hex color string.
 */
function toySvgHighlight(id, color) {
    svg.querySelector("#" + id).setAttribute("style", "fill: " + color);
}

/**
 * Sets the text content of an element.
 * @param {string} id target id.
 * @param {string} text text to set as the content of the element.
 */
function toySvgSetText(id, text) {
    svg.querySelector("#" + id).textContent = text;
}

/**
 * Shows or hides an element.
 * @param {string} id target id.
 * @param {boolean} doShow Whether to show the element (display: block). Else it will be hidden (display: none)
 */
function toySvgShow(id, doShow) {
    const display = doShow ? "block" : "none";
    svg.querySelector("#" + id).style.display = display;
}

</script>

<template>
    <object @load.once="svgLoaded" :data="path" type="image/svg+xml" class="visualization"></object>
</template>

<style scoped>
.visualization {
    height: 100%;
    width: 100%;
}
</style>
