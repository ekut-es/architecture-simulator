var settings;

const binary_representation = 0;
const decimal_representation = 1;
const hexa_representation = 2;
const signed_decimal_representation = 3;

var use_more_than_one_step_per_10ms = true;

// Placeholder values! In order to change default settings, go to settings/settings.py
var steps_per_interval = 100;
var parse_sim_after_not_typing_for_n_ms = 500;
var selected_isa = "riscv";
var reg_representation_mode = 0;
var mem_representation_mode = 0;
var pipeline_mode = "single_stage_pipeline";
var hazard_detection = true;

var input_timer;
var run;
var is_run_simulation = false;
var manual_run = false;
var riscv_visualization_loaded = false;
var toy_visualization_loaded = false;

var split = null;

window.addEventListener("DOMContentLoaded", function () {
    setMainContainerHeight();
    window.addEventListener("resize", function () {
        setMainContainerHeight();
    });

    evaluatePython_load_settings().then((value) => {
        settings = JSON.parse(value);

        steps_per_interval = settings.steps_per_interval;
        parse_sim_after_not_typing_for_n_ms = settings.autoparse_delay;

        // do NOT directly manipulate selected_isa because things the riscv elements wont get destroyed otherwise
        let preferred_isa = settings.default_isa;
        reg_representation_mode = settings.default_register_representation;
        mem_representation_mode = settings.default_memory_representation;
        pipeline_mode = settings.default_pipeline_mode;
        hazard_detection = settings.hazard_detection;

        const urlParams = new URLSearchParams(window.location.search);
        const isaParam = urlParams.get("isa");
        if (isaParam !== null) {
            preferred_isa = isaParam.toLowerCase();
        }

        if (preferred_isa === "riscv") {
            document.getElementById("isa_button_riscv_id").click();
            if (pipeline_mode === "single_stage_pipeline") {
                document.getElementById("button_SingleStage").click();
            } else if (pipeline_mode === "five_stage_pipeline") {
                document.getElementById("button_5-Stage").click();
                if (!hazard_detection) {
                    document.getElementById("button_HazardDetection").click();
                }
            }
        } else if (preferred_isa === "toy") {
            document.getElementById("isa_button_toy_id").click();
        }

        if (reg_representation_mode === binary_representation) {
            document
                .getElementById("reg_button_binary_representation_id")
                .click();
        } else if (reg_representation_mode === decimal_representation) {
            document
                .getElementById("reg_button_decimal_representation_id")
                .click();
        } else if (reg_representation_mode === signed_decimal_representation) {
            document
                .getElementById("reg_button_signed_decimal_representation_id")
                .click();
        } else if (reg_representation_mode === hexa_representation) {
            document
                .getElementById("reg_button_hexa_representation_id")
                .click();
        }

        if (mem_representation_mode === binary_representation) {
            document
                .getElementById("mem_button_binary_representation_id")
                .click();
        } else if (mem_representation_mode === decimal_representation) {
            document
                .getElementById("mem_button_decimal_representation_id")
                .click();
        } else if (mem_representation_mode === signed_decimal_representation) {
            document
                .getElementById("mem_button_signed_decimal_representation_id")
                .click();
        } else if (mem_representation_mode === hexa_representation) {
            document
                .getElementById("mem_button_hexa_representation_id")
                .click();
        }

        clearTimeout(input_timer);
        input_timer = setTimeout(
            finished_typing,
            parse_sim_after_not_typing_for_n_ms
        );

        refresh_button();
    });

    // Insert RISC-V SVG
    const riscvSvgElement = document.createElement("object");
    riscvSvgElement.data = "img/riscv_pipeline.svg";
    riscvSvgElement.type = "image/svg+xml";
    riscvSvgElement.id = "riscv-visualization";
    riscvSvgElement.addEventListener("load", function () {
        riscv_visualization_loaded = true;
        update_ui_async();
    });
    document
        .getElementById("visualizations-container-id")
        .append(riscvSvgElement);

    // Insert TOY SVG
    const toySvgElement = document.createElement("object");
    toySvgElement.data = "img/toy_structure.svg";
    toySvgElement.type = "image/svg+xml";
    toySvgElement.id = "toy-visualization";
    toySvgElement.addEventListener("load", function () {
        toy_visualization_loaded = true;
        update_ui_async();
    });
    document
        .getElementById("visualizations-container-id")
        .append(toySvgElement);

    // paste the help pages into the html
    document.getElementById("riscv-help").innerHTML = riscvDocumentation;
    document.getElementById("toy-help").innerHTML = toyDocumentation;

    document
        .getElementById("button-run-simulation-id")
        .addEventListener("click", () => {
            play_button();
        });

    function setMainContainerHeight() {
        const headerHeight = document.getElementById("header").offsetHeight;
        const navBarHeight = document.getElementById("nav-bar").offsetHeight;
        document.getElementById(
            "main-content-container"
        ).style.height = `calc(100vh - ${headerHeight}px - ${navBarHeight}px)`;
    }

    /** play button
     *
     * this function is usually called when the play button is pressed, and steps the simulation until there
     * are no more instructions left, while performing the necessary UI updates.
     */
    function play_button() {
        is_run_simulation = true;
        manual_run = true;
        editor.save();
        disable_editor();
        if (run) {
            stop_loading_animation();
            clearInterval(run);
        }
        start_loading_animation();
        resume_timer();
        if (use_more_than_one_step_per_10ms) {
            run = setInterval(step_n_times, 1);
        } else {
            run = setInterval(evaluatePython_step_sim, 10);
        }
        disable_run();
        enable_pause();
        disable_step();
        disable_pipeline_switch();
        disable_isa_switch();
        update_ui_async();
    }

    document
        .getElementById("button-pause-simulation-id")
        .addEventListener("click", () => {
            pause_button();
        });

    /**pause button
     *
     * This function is usually called when the pause button is pressed. It stops the execution
     * of a program and updates the UI.
     */
    function pause_button() {
        update_ui_async();
        is_run_simulation = false;
        disable_editor;
        stop_timer();
        clearInterval(run);
        update_performance_metrics();
        enable_run();
        disable_pause();
        enable_step();
        stop_loading_animation();
        disable_pipeline_switch();
        disable_isa_switch();
    }

    document
        .getElementById("button-step-simulation-id")
        .addEventListener("click", () => {
            next_button();
        });

    /**next button
     *
     * This function is usually called when the next button is pressed.
     * It performs one step of the simulation and updates the UI.
     */
    function next_button() {
        is_run_simulation = false;
        manual_run = true;
        editor.save();
        disable_editor();
        if (selected_isa === "riscv") {
            evaluatePython_step_sim();
        } else if (selected_isa === "toy") {
            evaluatePython_toy_single_step();
        }
        enable_run();
        disable_pause();
        enable_step();
        disable_isa_switch();
        disable_pipeline_switch();
    }

    document
        .getElementById("button-reset-simulation-id")
        .addEventListener("click", () => {
            refresh_button();
        });

    /**refresh button
     *
     * This function is usually called when the reset button is pressed, or when a full reset is needed.
     * It resets the entire simulation and clears the UI.
     */
    function refresh_button() {
        is_run_simulation = false;
        manual_run = false;
        disable_editor();
        clearInterval(run);
        evaluatePython_reset_sim();
        enable_editor();
        enable_run();
        disable_pause();
        enable_step();
        if (selected_isa == "toy") {
            enable_double_step();
        }
        enable_pipeline_switch();
        enable_isa_switch();
        clearTimeout(input_timer);
        finished_typing();
    }

    /**
     * This function steps the simulation the amount of steps given in steps_per_interval.
     * It stops when it has stepped for 10ms
     */
    function step_n_times() {
        let startTime = performance.now(); // get the start time
        for (i = 0; i < steps_per_interval; i++) {
            // do some task
            let endTime = performance.now(); // get the end time
            let timeElapsed = endTime - startTime; // calculate the time elapsed
            if (timeElapsed >= 10) {
                break;
            }
            evaluatePython_step_sim();
        }
        update_ui_async();
    }

    // select isa button listeners
    document
        .getElementById("isa_button_riscv_id")
        .addEventListener("click", () => {
            if (selected_isa === "toy") {
                // Destroy TOY elements
                hideCurrentVisualization();
                destroySplit();
                destroyCurrentIsaElements();
                document.getElementById("toy-help").style.display = "none";

                // TODO: Maybe hide the current visualization and destroy the gutter

                selected_isa = "riscv";
                document.getElementById("help-heading-id").textContent =
                    "RISC-V";
                document
                    .getElementById(
                        "mem_button_signed_decimal_representation_id"
                    )
                    .click();
                document
                    .getElementById(
                        "reg_button_signed_decimal_representation_id"
                    )
                    .click();
                document.getElementById("riscv-help").style.display = "block";
                document.getElementById("button_SingleStage").disabled = false;
                document.getElementById("button_5-Stage").disabled = false;
                document.getElementById(
                    "pipeline-mode-heading-id"
                ).style.color = "black";
                insertRiscvElements();
                refresh_button();
            }
        });

    document
        .getElementById("isa_button_toy_id")
        .addEventListener("click", () => {
            if (selected_isa === "riscv") {
                // Destroy RISCV elements (and reset some settings for some reason)
                hideCurrentVisualization();
                destroyCurrentIsaElements();
                hazard_detection = true;
                document.getElementById("riscv-help").style.display = "none";
                if (document.getElementById("button_5-Stage").checked) {
                    document.getElementById("button_SingleStage").click();
                }
                document.getElementById("button_SingleStage").disabled = true;
                document.getElementById("button_5-Stage").disabled = true;
                document.getElementById(
                    "pipeline-mode-heading-id"
                ).style.color = "grey";

                // Insert Toy Elements
                insertToyElements();
                selected_isa = "toy";
                document.getElementById("toy-help").style.display = "block";
                document.getElementById("help-heading-id").textContent = "Toy";
                document
                    .getElementById("mem_button_decimal_representation_id")
                    .click();
                document
                    .getElementById("reg_button_decimal_representation_id")
                    .click();
                showCurrentVisualization();
                createSplit();
                refresh_button();
            }
        });

    // register representation button listeners
    document
        .getElementById("reg_button_binary_representation_id")
        .addEventListener("click", () => {
            reg_representation_mode = binary_representation;
            update_ui_async();
        });

    document
        .getElementById("reg_button_decimal_representation_id")
        .addEventListener("click", () => {
            reg_representation_mode = decimal_representation;
            update_ui_async();
        });

    document
        .getElementById("reg_button_signed_decimal_representation_id")
        .addEventListener("click", () => {
            reg_representation_mode = signed_decimal_representation;
            update_ui_async();
        });

    document
        .getElementById("reg_button_hexa_representation_id")
        .addEventListener("click", () => {
            reg_representation_mode = hexa_representation;
            update_ui_async();
        });

    // memory representation button listeners
    document
        .getElementById("mem_button_binary_representation_id")
        .addEventListener("click", () => {
            mem_representation_mode = binary_representation;
            update_ui_async();
        });

    document
        .getElementById("mem_button_decimal_representation_id")
        .addEventListener("click", () => {
            mem_representation_mode = decimal_representation;
            update_ui_async();
        });

    document
        .getElementById("mem_button_hexa_representation_id")
        .addEventListener("click", () => {
            mem_representation_mode = hexa_representation;
            update_ui_async();
        });

    document
        .getElementById("mem_button_signed_decimal_representation_id")
        .addEventListener("click", () => {
            mem_representation_mode = signed_decimal_representation;
            update_ui_async();
        });

    // pipeline mode button listeners
    document
        .getElementById("button_SingleStage")
        .addEventListener("click", () => {
            pipeline_mode = "single_stage_pipeline";
            evaluatePython_reset_sim();
            input_timer = setTimeout(
                finished_typing,
                parse_sim_after_not_typing_for_n_ms
            );
            destroySplit();
            hideCurrentVisualization();
            disable_hazard_detection();
        });

    document.getElementById("button_5-Stage").addEventListener("click", () => {
        pipeline_mode = "five_stage_pipeline";
        evaluatePython_reset_sim();
        input_timer = setTimeout(
            finished_typing,
            parse_sim_after_not_typing_for_n_ms
        );
        createSplit();
        showCurrentVisualization();
        enable_hazard_detection();
    });

    // hazard detection button listener
    document
        .getElementById("button_HazardDetection")
        .addEventListener("click", () => {
            var button = document.getElementById("button_HazardDetection");
            if (button.checked) {
                hazard_detection = true;
                button.title = "disable hazard detection";
            } else {
                hazard_detection = false;
                button.title = "enable hazard detection";
            }
            refresh_button();
        });

    /**
     * This is the event listener for the codemirror editor, it gets called when a change
     * in the text area occurs.
     * It removes all highlights and autoparses the input while once again highlighting errors.
     */
    editor.on("change", function () {
        editor.save();
        for (let i = 0; i < editor.lineCount(); i++) {
            editor.removeLineClass(i, "background", "highlight");
        }
        editor.refresh();
        editor.closeHint();
        // autoparse
        clearTimeout(input_timer);
        if (!manual_run) {
            input_timer = setTimeout(
                finished_typing,
                parse_sim_after_not_typing_for_n_ms
            );
        }
    });

    /**
     * Parses the input and updates the ui
     */
    function finished_typing() {
        evaluatePython_parse_input();
        update_ui_async();
    }
});
// ask if you really wanna leave the site
window.onbeforeunload = function () {
    return true;
};

function disable_isa_switch() {
    document.getElementById("isa_button_riscv_id").disabled = true;
    document.getElementById("isa_button_toy_id").disabled = true;
}

function enable_isa_switch() {
    document.getElementById("isa_button_riscv_id").disabled = false;
    document.getElementById("isa_button_toy_id").disabled = false;
}

function disable_pipeline_switch() {
    document.getElementById("button_SingleStage").disabled = true;
    document.getElementById("button_SingleStage").style.backgroundColor =
        getComputedStyle(document.documentElement).getPropertyValue(
            "--button_disabled_color"
        );
    document.getElementById("button_5-Stage").disabled = true;
    document.getElementById("button_5-Stage").style.backgroundColor =
        getComputedStyle(document.documentElement).getPropertyValue(
            "--button_disabled_color"
        );
    document.getElementById("button_HazardDetection").disabled = true;
}

function enable_pipeline_switch() {
    if (document.getElementById("isa_button_toy_id").checked) {
        return;
    }
    document.getElementById("button_SingleStage").disabled = false;
    document.getElementById("button_SingleStage").style.backgroundColor =
        getComputedStyle(document.documentElement).getPropertyValue(
            "button_switch_stage"
        );
    document.getElementById("button_5-Stage").disabled = false;
    document.getElementById("button_5-Stage").style.backgroundColor =
        getComputedStyle(document.documentElement).getPropertyValue(
            "button_switch_stage"
        );
    if (document.getElementById("button_5-Stage").checked) {
        enable_hazard_detection();
    } else {
        disable_hazard_detection();
    }
}

function disable_run() {
    document.getElementById("button-run-simulation-id").disabled = true;
    document.getElementById("button-run-simulation-id").style.backgroundColor =
        getComputedStyle(document.documentElement).getPropertyValue(
            "--button_disabled_color"
        );
}
function enable_run() {
    document.getElementById("button-run-simulation-id").disabled = false;
    document.getElementById("button-run-simulation-id").style.backgroundColor =
        getComputedStyle(document.documentElement).getPropertyValue(
            "--button_green_color"
        );
}
function disable_pause() {
    document.getElementById("button-pause-simulation-id").disabled = true;
    document.getElementById(
        "button-pause-simulation-id"
    ).style.backgroundColor = getComputedStyle(
        document.documentElement
    ).getPropertyValue("--button_disabled_color");
}
function enable_pause() {
    document.getElementById("button-pause-simulation-id").disabled = false;
    document.getElementById(
        "button-pause-simulation-id"
    ).style.backgroundColor = getComputedStyle(
        document.documentElement
    ).getPropertyValue("--button_green_color");
}
function disable_step() {
    document.getElementById("button-step-simulation-id").disabled = true;
    document.getElementById("button-step-simulation-id").style.backgroundColor =
        getComputedStyle(document.documentElement).getPropertyValue(
            "--button_disabled_color"
        );
}
function enable_step() {
    document.getElementById("button-step-simulation-id").disabled = false;
    document.getElementById("button-step-simulation-id").style.backgroundColor =
        getComputedStyle(document.documentElement).getPropertyValue(
            "--button_blue_color"
        );
}
function disable_reset() {
    document.getElementById("button-reset-simulation-id").disabled = true;
    document.getElementById(
        "button-reset-simulation-id"
    ).style.backgroundColor = getComputedStyle(
        document.documentElement
    ).getPropertyValue("--button_disabled_color");
}
function enable_reset() {
    document.getElementById("button-reset-simulation-id").disabled = false;
    document.getElementById(
        "button-reset-simulation-id"
    ).style.backgroundColor = getComputedStyle(
        document.documentElement
    ).getPropertyValue("--button_red_color");
}

function disable_control_buttons() {
    disable_run();
    disable_pause();
    disable_step();
    disable_reset();
}

function enable_control_buttons() {
    enable_run();
    enable_pause();
    enable_step();
    enable_reset();
}

function start_loading_animation() {
    document.getElementById("loading-spinner-id").style.visibility = "visible";
}

function stop_loading_animation() {
    document.getElementById("loading-spinner-id").style.visibility = "hidden";
}

function start_loading_visuals() {
    disable_control_buttons();
    start_loading_animation();
}

function stop_loading_visuals() {
    enable_control_buttons();
    stop_loading_animation();
    disable_pause();
}

function disable_editor() {
    editor.setOption("readOnly", true);
}

function enable_editor() {
    editor.setOption("readOnly", false);
}

function disable_hazard_detection() {
    if (!document.getElementById("button_HazardDetection").checked) {
        document.getElementById("button_HazardDetection").click();
    }
    document.getElementById("button_HazardDetection").disabled = true;
}

function enable_hazard_detection() {
    document.getElementById("button_HazardDetection").disabled = false;
}

function toggleInputTab() {
    if (document.getElementById("InputTab").style.display === "none") {
        close_hint = false;
        document.getElementById("InputTab").style.display = "block";
        document.getElementById("CmdTab").style.display = "none";
        document.getElementById("RegisterTab").style.display = "none";
        document.getElementById("MemoryTab").style.display = "none";

        document.getElementById("button_tab_input").classList.add("active");
        document.getElementById("button_tab_cmd").classList.remove("active");
        document.getElementById("button_tab_reg").classList.remove("active");
        document.getElementById("button_tab_mem").classList.remove("active");
    }
}

function toggleCmdTab() {
    if (document.getElementById("CmdTab").style.display === "none") {
        close_hint = true;
        document.getElementById("CmdTab").style.display = "block";
        document.getElementById("InputTab").style.display = "none";
        document.getElementById("RegisterTab").style.display = "none";
        document.getElementById("MemoryTab").style.display = "none";

        document.getElementById("button_tab_cmd").classList.add("active");
        document.getElementById("button_tab_input").classList.remove("active");
        document.getElementById("button_tab_reg").classList.remove("active");
        document.getElementById("button_tab_mem").classList.remove("active");
    }
}

function toggleRegisterTab() {
    if (document.getElementById("RegisterTab").style.display === "none") {
        close_hint = true;
        document.getElementById("RegisterTab").style.display = "block";
        document.getElementById("InputTab").style.display = "none";
        document.getElementById("CmdTab").style.display = "none";
        document.getElementById("MemoryTab").style.display = "none";

        document.getElementById("button_tab_reg").classList.add("active");
        document.getElementById("button_tab_input").classList.remove("active");
        document.getElementById("button_tab_cmd").classList.remove("active");
        document.getElementById("button_tab_mem").classList.remove("active");
    }
}

function toggleMemoryTab() {
    if (document.getElementById("MemoryTab").style.display === "none") {
        close_hint = true;
        document.getElementById("MemoryTab").style.display = "block";
        document.getElementById("CmdTab").style.display = "none";
        document.getElementById("RegisterTab").style.display = "none";
        document.getElementById("InputTab").style.display = "none";

        document.getElementById("button_tab_mem").classList.add("active");
        document.getElementById("button_tab_input").classList.remove("active");
        document.getElementById("button_tab_reg").classList.remove("active");
        document.getElementById("button_tab_cmd").classList.remove("active");
    }
}

/**set_svg_text_complex_right_align
 *
 * @param {string} id -- The id of the element where the text should be set
 * @param {string} str -- The text the element given by id should have, the text is right aligned
 */
function set_svg_text_complex_right_align(id, str) {
    const pipeline_svg = document.getElementById(
        "riscv-visualization"
    ).contentDocument;
    pipeline_svg.getElementById(id).firstChild.nextSibling.style.fontSize =
        "15px";
    pipeline_svg.getElementById(id).firstChild.nextSibling.textContent = str;
    pipeline_svg
        .getElementById(id)
        .firstChild.nextSibling.setAttribute("text-anchor", "end");
}

/**set_svg_text_complex_right_align
 *
 * @param {string} id -- The id of the element where the text should be set
 * @param {string} str -- The text the element given by id should have, the text is left aligned
 */
function set_svg_text_complex_left_align(id, str) {
    const pipeline_svg = document.getElementById(
        "riscv-visualization"
    ).contentDocument;
    pipeline_svg.getElementById(id).firstChild.nextSibling.style.fontSize =
        "15px";
    pipeline_svg.getElementById(id).firstChild.nextSibling.textContent = str;
    pipeline_svg
        .getElementById(id)
        .firstChild.nextSibling.setAttribute("text-anchor", "start");
}

/**set_svg_text_complex_right_align
 *
 * @param {string} id -- The id of the element where the text should be set
 * @param {string} str -- The text the element given by id should have, the text is middle aligned
 */
function set_svg_text_complex_middle_align(id, str) {
    const pipeline_svg = document.getElementById(
        "riscv-visualization"
    ).contentDocument;
    pipeline_svg.getElementById(id).firstChild.nextSibling.style.fontSize =
        "15px";
    pipeline_svg.getElementById(id).firstChild.nextSibling.textContent = str;
    pipeline_svg
        .getElementById(id)
        .firstChild.nextSibling.setAttribute("text-anchor", "middle");
}

/**
 *
 * @param {string} id -- The id of the element where the colour should be set
 * @param {string} str -- The colour the element and all its childnodes should have
 */
function set_svg_colour(id, str) {
    const pipeline_svg = document.getElementById(
        "riscv-visualization"
    ).contentDocument;
    const Child_Nodes = pipeline_svg.getElementById(id).childNodes;
    if (Child_Nodes.length > 0) {
        for (let i = 0; i < Child_Nodes.length; i++) {
            set_svg_colour(Child_Nodes[i].id, str);
        }
    } else {
        pipeline_svg.getElementById(id).style.stroke = str;
        set_svg_marker_color(id, str);
    }
}

/**
 * Sets the color of the marker on the given path if it has one (multiple markers will probably not work).
 * @param {string} id id of the path that might have marker-start or marker-end
 * @param {string} str color name (either black, blue or green)
 */
function set_svg_marker_color(id, str) {
    const pipeline_svg = document.getElementById(
        "riscv-visualization"
    ).contentDocument;
    // the marker is part of the style attribute
    var styleAttribute = pipeline_svg.getElementById(id).getAttribute("style");
    // marker must contain 'Triangle_XXXXXX' where X is a hexnum. Can be followed or prepended by other characters.
    var marker_regex = /Triangle_[0-9a-fA-F]{6}/;
    var result = marker_regex.exec(styleAttribute);
    if (result != null) {
        // get the hex value for that color
        var hexColor = strToHexColor(str);
        var newMarker = "Triangle_" + hexColor;
        // create the new style string where the new color is used
        var newStyleAttribute = styleAttribute.replace(marker_regex, newMarker);
        pipeline_svg
            .getElementById(id)
            .setAttribute("style", newStyleAttribute);
    }
}

/**
 * Turns color names into hex values.
 * @param {str} str name of the color - must be either black, blue or green.
 * @returns {Number} the corresponding hex value for that color.
 */
function strToHexColor(str) {
    if (str === "black") {
        return "000000";
    }
    if (str === "blue") {
        return "0000FF";
    }
    if (str === "green") {
        return "008000";
    }
    console.log("color not supported");
    return "000000";
}

/**
 * @returns {HTMLElement} The Visualization for the current ISA.
 */
function getCurrentVisualization() {
    if (selected_isa == "riscv") {
        return document.getElementById("riscv-visualization");
    } /*if (selected_isa == "toy")*/ else {
        return document.getElementById("toy-visualization");
    }
}

/**
 * Hides the visualization for the current isa.
 */
function hideCurrentVisualization() {
    getCurrentVisualization().style.display = "none";
}

/**
 * Shows the visualization for the current isa.
 */
function showCurrentVisualization() {
    getCurrentVisualization().style.display = "block";
}

/**
 * Removes the isa specific elements of the currently selected isa. This does not include the visualization svg.
 */
function destroyCurrentIsaElements() {
    if (selected_isa === "riscv") {
        destroyRiscvElements();
    } else if (selected_isa === "toy") {
        destroyToyElements();
    }
}

function createSplit() {
    var mainContentContainer = document.getElementById(
        "main-content-container"
    );

    if (split === null && mainContentContainer) {
        if (window.innerWidth < window.innerHeight) {
            // Vertical split
            mainContentContainer.classList.add("vertical-split");
            split = Split(
                ["#text-content-container", "#visualizations-container-id"],
                {
                    direction: "vertical",
                    minSize: 200,
                    sizes: [60, 40],
                    snapOffset: 0,
                }
            );
        } else {
            // Horizontal split
            mainContentContainer.classList.add("horizontal-split");
            split = Split(
                ["#text-content-container", "#visualizations-container-id"],
                {
                    minSize: 200,
                    sizes: [35, 65],
                    snapOffset: 0,
                }
            );
        }
    }
}

function destroySplit() {
    if (split !== null) {
        document
            .getElementById("main-content-container")
            .classList.remove("vertical-split", "horizontal-split");
        split.destroy();
        split = null;
    }
}

function handleResize() {
    var mainContentContainer = document.getElementById(
        "main-content-container"
    );
    if (
        (mainContentContainer.classList.contains("vertical-split") &&
            window.innerWidth >= window.innerHeight) ||
        (mainContentContainer.classList.contains("horizontal-split") &&
            window.innerWidth < window.innerHeight)
    ) {
        destroySplit();
        createSplit();
    }
}

window.addEventListener("resize", handleResize);
