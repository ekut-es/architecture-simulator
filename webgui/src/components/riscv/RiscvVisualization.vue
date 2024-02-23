<!-- Component for the riscv visualization.
This differs from the normal SvgVisualization.vue component because the five stage svg is a bit quirky -->
<script setup>
/**
 * This is almost the same as the normal Visualization.Vue component,
 * but it has the riscv functions.
 */
import { ref, watchEffect } from "vue";

const props = defineProps(["path", "simulationStore"]);

const path = props.path;

const simulationStore = props.simulationStore;

/**
 * The svg itself (contentDocument of the object element). This is where
 * modifications to the svg can be made. Will be undefined before
 * the svg has finished loading.
 */
let svg = ref(null);

function svgLoaded(event) {
    svg.value = event.target.contentDocument;
}

watchEffect(() => {
    if (svg.value !== null) {
        updateVisualization(simulationStore.svgDirectives);
    }
});

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
            case "highlight-plain":
                set_svg_colour_plain(id, value);
                break;
            case "write":
                set_svg_text_plain(id, value);
                break;
        }
    }
}

/**
 * Sets the text content of a element that can be directly found using getElementById
 * @param {string} id id of text field
 * @param {string} str text to insert
 */
function set_svg_text_plain(id, str) {
    svg.value.getElementById(id).textContent = str;
}

/**
 * Sets the color of a path and all attached markers where the path can be directly found using getElementById
 * @param {string} id id of the path
 * @param {string} str hex color code, starting with '#'
 */
function set_svg_colour_plain(id, color) {
    svg.value.getElementById(id).style.stroke = color;
    set_svg_marker_color(id, color);
}

/**set_svg_text_complex_right_align
 *
 * @param {string} id -- The id of the element where the text should be set
 * @param {string} str -- The text the element given by id should have, the text is right aligned
 */
function set_svg_text_complex_right_align(id, str) {
    svg.value.getElementById(id).firstChild.nextSibling.style.fontSize = "15px";
    svg.value.getElementById(id).firstChild.nextSibling.textContent = str;
    svg.value
        .getElementById(id)
        .firstChild.nextSibling.setAttribute("text-anchor", "end");
}

/**set_svg_text_complex_right_align
 *
 * @param {string} id -- The id of the element where the text should be set
 * @param {string} str -- The text the element given by id should have, the text is left aligned
 */
function set_svg_text_complex_left_align(id, str) {
    svg.value.getElementById(id).firstChild.nextSibling.style.fontSize = "15px";
    svg.value.getElementById(id).firstChild.nextSibling.textContent = str;
    svg.value
        .getElementById(id)
        .firstChild.nextSibling.setAttribute("text-anchor", "start");
}

/**set_svg_text_complex_right_align
 *
 * @param {string} id -- The id of the element where the text should be set
 * @param {string} str -- The text the element given by id should have, the text is middle aligned
 */
function set_svg_text_complex_middle_align(id, str) {
    svg.value.getElementById(id).firstChild.nextSibling.style.fontSize = "15px";
    svg.value.getElementById(id).firstChild.nextSibling.textContent = str;
    svg.value
        .getElementById(id)
        .firstChild.nextSibling.setAttribute("text-anchor", "middle");
}

/**
 *
 * @param {string} id -- The id of the element where the colour should be set
 * @param {string} str -- The colour the element and all its childnodes should have
 */
function set_svg_colour(id, colour) {
    try {
        const Child_Nodes = svg.value.getElementById(id).childNodes;
        if (Child_Nodes.length > 0) {
            for (let i = 0; i < Child_Nodes.length; i++) {
                set_svg_colour(Child_Nodes[i].id, colour);
            }
        } else {
            svg.value.getElementById(id).style.stroke = colour;
            set_svg_marker_color(id, colour);
        }
    } catch {
        console.log("id not found (?)");
    }
}

/**
 * Sets the color of all markers on the given path if it has any
 * @param {string} id id of the path that might have marker-start or marker-end
 * @param {string} str hex color code, starting with '#'
 */
function set_svg_marker_color(id, color) {
    // the marker is part of the style attribute
    var styleAttribute = svg.value.getElementById(id).getAttribute("style");
    // marker must contain 'XXXXXX_ArchsimMarker' where X is a hexnum. Can be followed or prepended by other characters.
    var marker_regex = /[\da-fA-F]{6}(?=_ArchsimMarker)/g; // the global flag g makes the regex apply to all matches
    // create the new style string where the new color is used
    var newStyleAttribute = styleAttribute.replaceAll(
        marker_regex,
        color.substring(1)
    );
    svg.value.getElementById(id).setAttribute("style", newStyleAttribute);
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
