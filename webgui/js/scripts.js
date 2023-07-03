const binary_representation = 0;
const decimal_representation = 1;
const hexa_representation = 2;
//change steps_per_interval if you want to change the amount of times evaluatePython_step_sim() is called per interval (10ms)
//the higher this number the less responsive the ui gets, at 200 it starts to get a bit too unresponsive. 100 feels acceptable
const steps_per_interval = 100;
//set use_more_than_one_step_per_10ms to false if you only want to call up evaluatePython_step_sim() more than once per interval (10ms)
const use_more_than_one_step_per_10ms = true;
const parse_sim_after_not_typing_for_n_ms = 2000;
var input_timer;
let representation_mode = decimal_representation; //change this to set another default repr.
var run;

let waiting_for_pyodide_flag = true;
window.addEventListener("DOMContentLoaded", function () {
    clearTimeout(input_timer);
    input_timer = setTimeout(
        finished_typing,
        parse_sim_after_not_typing_for_n_ms
    );
    document
        .getElementById("button_simulation_start_id")
        .addEventListener("click", () => {
            document.getElementById("input").disabled = true;
            if (run) {
                stop_loading_animation();
                clearInterval(run);
            }
            start_loading_animation();
            resume_timer();
            if (use_more_than_one_step_per_10ms) {
                run = setInterval(step_n_times, 1); //minimum is 10ms but we use 1ms in case it gets changed in the future
            } else {
                run = setInterval(evaluatePython_step_sim, 1);
            }
            disable_run();
            enable_pause();
            disable_step();
        });

    document
        .getElementById("button_simulation_pause_id")
        .addEventListener("click", () => {
            document.getElementById("input").disabled = true;
            clearInterval(run);
            stop_timer();
            update_performance_metrics();
            enable_run();
            disable_pause();
            enable_step();
            stop_loading_animation();
        });

    document
        .getElementById("button_simulation_next_id")
        .addEventListener("click", () => {
            document.getElementById("input").disabled = true;
            document.getElementById("input").disabled = true;
            resume_timer();
            evaluatePython_step_sim();
            stop_timer();
            update_performance_metrics();
            enable_run();
            disable_pause();
            enable_step();
        });

    document
        .getElementById("button_simulation_refresh_id")
        .addEventListener("click", () => {
            document.getElementById("input").disabled = true;
            clearInterval(run);
            evaluatePython_reset_sim();
            document.getElementById("input").disabled = false;
            enable_run();
            disable_pause();
            enable_step();
            clearTimeout(input_timer);
            input_timer = setTimeout(
                finished_typing,
                parse_sim_after_not_typing_for_n_ms
            );
        });

    function step_n_times() {
        for (i = 0; i < steps_per_interval; i++) {
            evaluatePython_step_sim();
        }
    }

    document
        .getElementById("button_binary_representation_id")
        .addEventListener("click", () => {
            representation_mode = binary_representation;
            evaluatePython_update_tables();
            document
                .getElementById("button_binary_representation_id")
                .classList.add("active");
            document
                .getElementById("button_decimal_representation_id")
                .classList.remove("active");
            document
                .getElementById("button_hexa_representation_id")
                .classList.remove("active");
        });

    document
        .getElementById("button_decimal_representation_id")
        .addEventListener("click", () => {
            representation_mode = decimal_representation;
            evaluatePython_update_tables();
            document
                .getElementById("button_decimal_representation_id")
                .classList.add("active");
            document
                .getElementById("button_binary_representation_id")
                .classList.remove("active");
            document
                .getElementById("button_hexa_representation_id")
                .classList.remove("active");
        });

    document
        .getElementById("button_hexa_representation_id")
        .addEventListener("click", () => {
            representation_mode = hexa_representation;
            evaluatePython_update_tables();
            document
                .getElementById("button_hexa_representation_id")
                .classList.add("active");
            document
                .getElementById("button_decimal_representation_id")
                .classList.remove("active");
            document
                .getElementById("button_binary_representation_id")
                .classList.remove("active");
        });

    document.getElementById("input").addEventListener("keyup", () => {
        // line numbers:
        const numberOfLines = input.value.split("\n").length;
        lineNumbers = this.document.getElementById("line_numbers");
        lineNumbers.innerHTML = Array(numberOfLines)
            .fill("<span></span>")
            .join("");

        // autoparse
        clearTimeout(input_timer);
        input_timer = setTimeout(
            finished_typing,
            parse_sim_after_not_typing_for_n_ms
        );
    });

    document.getElementById("input").addEventListener("keydown", () => {
        clearTimeout(input_timer);
    });

    function finished_typing() {
        evaluatePython_parse_input();
    }
});
// ask if you really wanna leave the site
window.onbeforeunload = function () {
    return true;
};

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
