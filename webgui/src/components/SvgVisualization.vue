<!-- Shows a visualization and updates it according to the values of the simulation store.
TODO: This is currently only used for toy, but we should replace the kindred riscv component
with this (and modify the functions here so that this actually works).-->
<script setup>
import { ref, watchEffect } from "vue";

/**
 * path: The path to the svg.
 * simulationStore: The simulation store from which to pull the update values. They must be stored in a variable called "svgDirectives".
 */
const props = defineProps(["path", "simulationStore"]);

/**
 * The path to the svg.
 */
const path = props.path;

/**
 * The simulation store.
 */
const simulationStore = props.simulationStore;

/**
 * The svg itself (contentDocument of the object element). This is where
 * modifications to the svg can be made. Will be undefined before
 * the svg has finished loading.
 */
let svg = ref(null);

/**
 * This function can set the svg variable once it has loaded.
 * @param {Event} event load event
 */
function svgLoaded(event) {
    svg.value = event.target.contentDocument;
}

/**
 * Update the if the svgDirective change.
 * Will be invoked immediately but will only do something once the
 * simulation has loaded.
 */
watchEffect(() => {
    if (svg.value !== null) {
        updateVisualization(simulationStore.svgDirectives);
    }
});

/**
 * Core method for the svg updates.
 * Iterates over all entries and calls the related update functions.
 * @param {Array} updateValues svgDirectives
 */
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
    svg.value.querySelector("#" + id).setAttribute("style", "fill: " + color);
}

/**
 * Sets the text content of an element.
 * @param {string} id target id.
 * @param {string} text text to set as the content of the element.
 */
function toySvgSetText(id, text) {
    svg.value.querySelector("#" + id).textContent = text;
}

/**
 * Shows or hides an element.
 * @param {string} id target id.
 * @param {boolean} doShow Whether to show the element (display: block). Else it will be hidden (display: none)
 */
function toySvgShow(id, doShow) {
    const display = doShow ? "block" : "none";
    svg.value.querySelector("#" + id).style.display = display;
}
</script>

<template>
    <object
        @load.once="svgLoaded"
        :data="path"
        type="image/svg+xml"
        class="visualization"
    ></object>
</template>

<style scoped>
.visualization {
    height: 100%;
    width: 100%;
}
</style>
