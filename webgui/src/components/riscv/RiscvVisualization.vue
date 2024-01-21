<script setup>
/**
 * This is almost the same as the normal Visualization.Vue component,
 * but it has the riscv functions.
 */
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
    watch(() => simulationStore.svgDirectives, (updateValues) => { updateVisualization(updateValues); }, { immediate: true });
}

function updateVisualization(updateValues) {
    for (let i = 0; i < updateValues.length; i++) {
        const update = updateValues[i];
        const id = update[0];
        const action = update[1];
        const value = update[2];
        switch (action) {
            case "highlight":
                set_svg_colour(id, value);
                break;
            case "write-left":
                set_svg_text_complex_left_align(id, value);
                break;
            case "write-center":
                set_svg_text_complex_middle_align(id, value);
                break;
            case "write-right":
                set_svg_text_complex_right_align(id, value);
                break;
        }
    }
}

/**set_svg_text_complex_right_align
 *
 * @param {string} id -- The id of the element where the text should be set
 * @param {string} str -- The text the element given by id should have, the text is right aligned
 */
function set_svg_text_complex_right_align(id, str) {
    svg.getElementById(id).firstChild.nextSibling.style.fontSize =
        "15px";
    svg.getElementById(id).firstChild.nextSibling.textContent =
        str;
    svg
        .getElementById(id)
        .firstChild.nextSibling.setAttribute("text-anchor", "end");
}

/**set_svg_text_complex_right_align
 *
 * @param {string} id -- The id of the element where the text should be set
 * @param {string} str -- The text the element given by id should have, the text is left aligned
 */
function set_svg_text_complex_left_align(id, str) {
    svg.getElementById(id).firstChild.nextSibling.style.fontSize =
        "15px";
    svg.getElementById(id).firstChild.nextSibling.textContent =
        str;
    svg
        .getElementById(id)
        .firstChild.nextSibling.setAttribute("text-anchor", "start");
}

/**set_svg_text_complex_right_align
 *
 * @param {string} id -- The id of the element where the text should be set
 * @param {string} str -- The text the element given by id should have, the text is middle aligned
 */
function set_svg_text_complex_middle_align(id, str) {
    svg.getElementById(id).firstChild.nextSibling.style.fontSize =
        "15px";
    svg.getElementById(id).firstChild.nextSibling.textContent =
        str;
    svg
        .getElementById(id)
        .firstChild.nextSibling.setAttribute("text-anchor", "middle");
}

/**
 *
 * @param {string} id -- The id of the element where the colour should be set
 * @param {string} str -- The colour the element and all its childnodes should have
 */
function set_svg_colour(id, colour) {
    const Child_Nodes = svg.getElementById(id).childNodes;
    if (Child_Nodes.length > 0) {
        for (let i = 0; i < Child_Nodes.length; i++) {
            set_svg_colour(Child_Nodes[i].id, colour);
        }
    } else {
        svg.getElementById(id).style.stroke = colour;
        set_svg_marker_color(id, colour);
    }
}

/**
 * Sets the color of the marker on the given path if it has one (multiple markers will probably not work).
 * @param {string} id id of the path that might have marker-start or marker-end
 * @param {string} str hex color code, starting with '#'
 */
function set_svg_marker_color(id, color) {
    // the marker is part of the style attribute
    var styleAttribute = svg
        .getElementById(id)
        .getAttribute("style");
    // marker must contain 'XXXXXX_ArchsimMarker' where X is a hexnum. Can be followed or prepended by other characters.
    var marker_regex = /[\da-fA-F]{6}(?=_ArchsimMarker)/;
    // create the new style string where the new color is used
    var newStyleAttribute = styleAttribute.replace(
        marker_regex,
        color.substring(1)
    );
    if (styleAttribute !== newStyleAttribute) {
        console.log("");
    }

    svg
        .getElementById(id)
        .setAttribute("style", newStyleAttribute);
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
