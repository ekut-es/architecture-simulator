const binary_representation = 0;
const decimal_representation = 1;
const hexa_representation = 2;
const signed_decimal_representation = 3;
//change steps_per_interval if you want to change the amount of times evaluatePython_step_sim() is called per interval (10ms)
//the higher this number the less responsive the ui gets, at 200 it starts to get a bit too unresponsive. 100 feels acceptable
const steps_per_interval = 100;

//set use_more_than_one_step_per_10ms to false if you only want to call up evaluatePython_step_sim() more than once per interval (10ms)
const use_more_than_one_step_per_10ms = true;
const parse_sim_after_not_typing_for_n_ms = 500;

var input_timer;

let hazard_detection = true;

let selected_isa = "riscv";

let reg_representation_mode = decimal_representation; //change this to set another default repr.
let mem_representation_mode = decimal_representation;

var run;
var is_run_simulation = false;
var manual_run = false;
var pipeline_mode = "single_stage_pipeline";

window.addEventListener("DOMContentLoaded", function () {
    clearTimeout(input_timer);
    input_timer = setTimeout(
        finished_typing,
        parse_sim_after_not_typing_for_n_ms
    );

    // paste the help pages into the html
    document.getElementById("RiscvHelp").innerHTML = riscvDocumentation;
    document.getElementById("ToyHelp").innerHTML = toyDocumentation;

    document
        .getElementById("button_simulation_start_id")
        .addEventListener("click", () => {
            play_button();
        });

    function play_button() {
        is_run_simulation = true;
        manual_run = true;
        editor.save();
        //finished_typing(); FIXME: The input should get parsed after clicking the button in case the auto parsing wasn't triggered yet.
        // But this should only happen if the input has changed and not after the user has already started the simulation.
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
        update_ui_async();
    }

    document
        .getElementById("button_simulation_pause_id")
        .addEventListener("click", () => {
            pause_button();
        });

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
    }

    document
        .getElementById("button_simulation_next_id")
        .addEventListener("click", () => {
            next_button();
        });

    function next_button() {
        is_run_simulation = false;
        manual_run = true;
        editor.save();
        //finished_typing(); FIXME: The input should get parsed after clicking the button in case the auto parsing wasn't triggered yet.
        // But this should only happen if the input has changed and not after the user has already started the simulation.
        disable_editor();
        evaluatePython_step_sim();
        update_performance_metrics();
        enable_run();
        disable_pause();
        enable_step();
        disable_pipeline_switch();
    }

    document
        .getElementById("button_simulation_refresh_id")
        .addEventListener("click", () => {
            refresh_button();
        });

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
        enable_pipeline_switch();
        clearTimeout(input_timer);
        finished_typing();
    }

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
            selected_isa = "riscv";
            refresh_button();

            document.getElementById("HelpHeader").textContent = "RISC-V";
            RiscvHelp.style.display = "block";
            ToyHelp.style.display = "none";

            document.getElementById("button_SingleStage").disabled = false;
            document.getElementById("button_5-Stage").disabled = false;
            document.getElementById("modal_header_switch_stage").style.color =
                "black";
        });

    document
        .getElementById("isa_button_toy_id")
        .addEventListener("click", () => {
            selected_isa = "toy";
            refresh_button();
            
            document.getElementById("HelpHeader").textContent = "Toy";
            RiscvHelp.style.display = "none";
            ToyHelp.style.display = "block";

            if (document.getElementById("button_5-Stage").checked) {
                document.getElementById("button_SingleStage").click();
            }
            document.getElementById("button_SingleStage").disabled = true;
            document.getElementById("button_5-Stage").disabled = true;
            document.getElementById("modal_header_switch_stage").style.color =
                "grey";
        });

    // register representation button listeners
    document
        .getElementById("reg_button_binary_representation_id")
        .addEventListener("click", () => {
            reg_representation_mode = binary_representation;
            evaluatePython_update_tables();
        });

    document
        .getElementById("reg_button_decimal_representation_id")
        .addEventListener("click", () => {
            reg_representation_mode = decimal_representation;
            evaluatePython_update_tables();
        });

    document
        .getElementById("reg_button_signed_decimal_representation_id")
        .addEventListener("click", () => {
            reg_representation_mode = signed_decimal_representation;
            evaluatePython_update_tables();
        });

    document
        .getElementById("reg_button_hexa_representation_id")
        .addEventListener("click", () => {
            reg_representation_mode = hexa_representation;
            evaluatePython_update_tables();
        });

    // memory representation button listeners
    document
        .getElementById("mem_button_binary_representation_id")
        .addEventListener("click", () => {
            mem_representation_mode = binary_representation;
            evaluatePython_update_tables();
        });

    document
        .getElementById("mem_button_decimal_representation_id")
        .addEventListener("click", () => {
            mem_representation_mode = decimal_representation;
            evaluatePython_update_tables();
        });

    document
        .getElementById("mem_button_hexa_representation_id")
        .addEventListener("click", () => {
            mem_representation_mode = hexa_representation;
            evaluatePython_update_tables();
        });

    document
        .getElementById("mem_button_signed_decimal_representation_id")
        .addEventListener("click", () => {
            mem_representation_mode = signed_decimal_representation;
            evaluatePython_update_tables();
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
            document.getElementById("button_tab_visualization").style.display =
                "none";
            document.getElementById("VisualizationTabContent").style.display =
                "none";
            document.getElementById("MainContent").style.display = "block";
            document.getElementById("button_tab_visualization").textContent =
                "Visualization";

            disable_hazard_detection();
        });

    document.getElementById("button_5-Stage").addEventListener("click", () => {
        pipeline_mode = "five_stage_pipeline";
        evaluatePython_reset_sim();
        input_timer = setTimeout(
            finished_typing,
            parse_sim_after_not_typing_for_n_ms
        );

        document.getElementById("button_tab_visualization").style.display =
            "block";

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
        });

    editor.on("change", function () {
        synchronizeEditors(editor, editor_vis);
        editor.save();
        for (let i = 0; i < editor.lineCount(); i++) {
            editor.removeLineClass(i, "background", "highlight");
            editor_vis.removeLineClass(i, "background", "highlight");
        }
        editor.refresh();
        editor_vis.refresh();
        editor.closeHint();
        editor_vis.closeHint();
        // autoparse
        clearTimeout(input_timer);
        if (!manual_run) {
            input_timer = setTimeout(
                finished_typing,
                parse_sim_after_not_typing_for_n_ms
            );
        }
    });

    editor_vis.on("change", function () {
        synchronizeEditors(editor_vis, editor);
        editor_vis.save();
        // autoparse
        clearTimeout(input_timer);
        if (!manual_run) {
            input_timer = setTimeout(
                finished_typing,
                parse_sim_after_not_typing_for_n_ms
            );
        }
    });

    function finished_typing() {
        evaluatePython_parse_input();
        update_ui_async();
    }
});
// ask if you really wanna leave the site
window.onbeforeunload = function () {
    return true;
};

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
    document.getElementById("button_simulation_start_id").disabled = true;
    document.getElementById(
        "button_simulation_start_id"
    ).style.backgroundColor = getComputedStyle(
        document.documentElement
    ).getPropertyValue("--button_disabled_color");
}
function enable_run() {
    document.getElementById("button_simulation_start_id").disabled = false;
    document.getElementById(
        "button_simulation_start_id"
    ).style.backgroundColor = getComputedStyle(
        document.documentElement
    ).getPropertyValue("--button_green_color");
}
function disable_pause() {
    document.getElementById("button_simulation_pause_id").disabled = true;
    document.getElementById(
        "button_simulation_pause_id"
    ).style.backgroundColor = getComputedStyle(
        document.documentElement
    ).getPropertyValue("--button_disabled_color");
}
function enable_pause() {
    document.getElementById("button_simulation_pause_id").disabled = false;
    document.getElementById(
        "button_simulation_pause_id"
    ).style.backgroundColor = getComputedStyle(
        document.documentElement
    ).getPropertyValue("--button_green_color");
}
function disable_step() {
    document.getElementById("button_simulation_next_id").disabled = true;
    document.getElementById("button_simulation_next_id").style.backgroundColor =
        getComputedStyle(document.documentElement).getPropertyValue(
            "--button_disabled_color"
        );
}
function enable_step() {
    document.getElementById("button_simulation_next_id").disabled = false;
    document.getElementById("button_simulation_next_id").style.backgroundColor =
        getComputedStyle(document.documentElement).getPropertyValue(
            "--button_blue_color"
        );
}
function disable_reset() {
    document.getElementById("button_simulation_refresh_id").disabled = true;
    document.getElementById(
        "button_simulation_refresh_id"
    ).style.backgroundColor = getComputedStyle(
        document.documentElement
    ).getPropertyValue("--button_disabled_color");
}
function enable_reset() {
    document.getElementById("button_simulation_refresh_id").disabled = false;
    document.getElementById(
        "button_simulation_refresh_id"
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
    document.getElementById("loading_id").style.visibility = "visible";
}

function stop_loading_animation() {
    document.getElementById("loading_id").style.visibility = "hidden";
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
    editor_vis.setOption("readOnly", true);
}

function enable_editor() {
    editor.setOption("readOnly", false);
    editor_vis.setOption("readOnly", false);
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

function toggleVisualizationTabContent() {
    if (
        document.getElementById("VisualizationTabContent").style.display ===
        "none"
    ) {
        synchronizeEditors(editor, editor_vis);
        editor.closeHint();
        document.getElementById("VisualizationTabContent").style.display =
            "block";
        document.getElementById("MainContent").style.display = "none";
        document.getElementById("button_tab_visualization").textContent =
            "Visualization Off";
    } else {
        synchronizeEditors(editor_vis, editor);
        editor_vis.closeHint();
        document.getElementById("VisualizationTabContent").style.display =
            "none";
        document.getElementById("MainContent").style.display = "block";
        document.getElementById("button_tab_visualization").textContent =
            "Visualization";
    }
}

function toggleInputTab() {
    if (document.getElementById("InputTab").style.display === "none") {
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

function synchronizeEditors(sEditor, tEditor) {
    const content = sEditor.getValue();
    if (content !== tEditor.getValue()) {
        tEditor.setValue(content);
    }
}

window.addEventListener("load", function () {
    const pipeline_svg = document.getElementById(
        "visualization_pipeline"
    ).contentDocument;

    pipeline_svg
        .getElementById("MemoryExecuteAluResultText1")
        .setAttribute("visibility", "hidden");
    pipeline_svg
        .getElementById("MemoryRegisterFileReadData2Text")
        .setAttribute("visibility", "hidden");
});

function set_svg_text_simple(id, str) {
    const pipeline_svg = document.getElementById(
        "visualization_pipeline"
    ).contentDocument;
    pipeline_svg.getElementById(id).textContent = str;
}

// function set_svg_text_simple_right_align(id, str) {
//     const pipeline_svg = document.getElementById(
//         "visualization_pipeline"
//     ).contentDocument;
//     pipeline_svg.getElementById(id).textContent = str;
//     pipeline_svg.getElementById(id).setAttribute("text-anchor", "end");
// }

// function set_svg_text_simple_left_align(id, str) {
//     const pipeline_svg = document.getElementById(
//         "visualization_pipeline"
//     ).contentDocument;
//     pipeline_svg.getElementById(id).textContent = str;
//     pipeline_svg.getElementById(id).setAttribute("text-anchor", "start");
// }

function set_svg_text_complex_right_align(id, str) {
    const pipeline_svg = document.getElementById(
        "visualization_pipeline"
    ).contentDocument;
    pipeline_svg.getElementById(id).firstChild.nextSibling.style.fontSize =
        "15px";
    pipeline_svg.getElementById(id).firstChild.nextSibling.textContent = str;
    pipeline_svg
        .getElementById(id)
        .firstChild.nextSibling.setAttribute("text-anchor", "end");
}

function set_svg_text_complex_left_align(id, str) {
    const pipeline_svg = document.getElementById(
        "visualization_pipeline"
    ).contentDocument;
    pipeline_svg.getElementById(id).firstChild.nextSibling.style.fontSize =
        "15px";
    pipeline_svg.getElementById(id).firstChild.nextSibling.textContent = str;
    pipeline_svg
        .getElementById(id)
        .firstChild.nextSibling.setAttribute("text-anchor", "start");
}

function set_svg_text_complex_middle_align(id, str) {
    const pipeline_svg = document.getElementById(
        "visualization_pipeline"
    ).contentDocument;
    pipeline_svg.getElementById(id).firstChild.nextSibling.style.fontSize =
        "15px";
    pipeline_svg.getElementById(id).firstChild.nextSibling.textContent = str;
    pipeline_svg
        .getElementById(id)
        .firstChild.nextSibling.setAttribute("text-anchor", "middle");
}

function set_svg_colour(id, str) {
    const pipeline_svg = document.getElementById(
        "visualization_pipeline"
    ).contentDocument;
    const Child_Nodes = pipeline_svg.getElementById(id).childNodes;
    if (Child_Nodes.length > 0) {
        for (let i = 0; i < Child_Nodes.length; i++) {
            set_svg_colour(Child_Nodes[i].id, str);
        }
    } else {
        pipeline_svg.getElementById(id).style.stroke = str;
    }
}
