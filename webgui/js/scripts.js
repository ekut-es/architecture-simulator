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
var pipeline_mode = "single_stage_pipeline";
window.addEventListener("DOMContentLoaded", function () {
    clearTimeout(input_timer);
    input_timer = setTimeout(
        finished_typing,
        parse_sim_after_not_typing_for_n_ms
    );
    document
        .getElementById("button_simulation_start_id")
        .addEventListener("click", () => {
            editor.save();
            //finished_typing(); FIXME: The input should get parsed after clicking the button in case the auto parsing wasn't triggered yet.
            // But this should only happen if the input has changed and not after the user has already started the simulation.
            document.getElementById("input").disabled = true; // I dont think this does anything. But codemirror provides a function "readOnly" that we could use.
            document.getElementById("vis_input").disabled = true;
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
        });

    document
        .getElementById("button_simulation_pause_id")
        .addEventListener("click", () => {
            document.getElementById("input").disabled = true;
            document.getElementById("vis_input").disabled = true;
            stop_timer();
            clearInterval(run);
            update_performance_metrics();
            enable_run();
            disable_pause();
            enable_step();
            stop_loading_animation();
            disable_pipeline_switch();
        });

    document
        .getElementById("button_simulation_next_id")
        .addEventListener("click", () => {
            editor.save();
            //finished_typing(); FIXME: The input should get parsed after clicking the button in case the auto parsing wasn't triggered yet.
            // But this should only happen if the input has changed and not after the user has already started the simulation.
            document.getElementById("input").disabled = true;
            document.getElementById("vis_input").disabled = true;
            evaluatePython_step_sim();
            update_performance_metrics();
            enable_run();
            disable_pause();
            enable_step();
            disable_pipeline_switch();
        });

    document
        .getElementById("button_simulation_refresh_id")
        .addEventListener("click", () => {
            document.getElementById("input").disabled = true;
            document.getElementById("vis_input").disabled = true;
            clearInterval(run);
            evaluatePython_reset_sim();
            document.getElementById("input").disabled = false;
            document.getElementById("input").disabled = false;
            enable_run();
            disable_pause();
            enable_step();
            enable_pipeline_switch();
            clearTimeout(input_timer);
            finished_typing();
        });

    function step_n_times() {
        //resume_timer()
        for (i = 0; i < steps_per_interval; i++) {
            evaluatePython_step_sim(false);
        }
        //stop_timer()
    }

    // select isa button listeners
    document
        .getElementById("isa_button_riscv_id")
        .addEventListener("click", () => {
            selected_isa = "riscv";
        });

    document
        .getElementById("isa_button_toy_id")
        .addEventListener("click", () => {
            selected_isa = "toy";
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

            document.getElementById("button_HazardDetection").checked = true;
            hazard_detection = true;
            document.getElementById("button_HazardDetection").disabled = true;
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

        document.getElementById("button_HazardDetection").title =
            "disable hazard detection";
        document.getElementById("button_HazardDetection").disabled = false;
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
        input_timer = setTimeout(
            finished_typing,
            parse_sim_after_not_typing_for_n_ms
        );
    });

    editor_vis.on("change", function () {
        synchronizeEditors(editor_vis, editor);
        editor_vis.save();
        // autoparse
        clearTimeout(input_timer);
        input_timer = setTimeout(
            finished_typing,
            parse_sim_after_not_typing_for_n_ms
        );
    });

    function finished_typing() {
        evaluatePython_parse_input();
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
