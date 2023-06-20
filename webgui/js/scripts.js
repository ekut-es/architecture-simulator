const binary_representation = 0;
const decimal_representation = 1;
const hexa_representation = 2;
let representation_mode = binary_representation; //change this to set another default repr.
var run;

		let waiting_for_pyodide_flag = true
		window.addEventListener('DOMContentLoaded', function () {
			document.getElementById("button_simulation_start_id").addEventListener("click", () => {
				document.getElementById("input").disabled = true;
				if(run) {
					stop_loading_animation();
					clearInterval(run);
				}
				start_loading_animation();
				run = setInterval(evaluatePython_step_sim,1);
				disable_run();
				enable_pause();
				disable_step();
			});

			document.getElementById("button_simulation_pause_id").addEventListener("click", () => {
				document.getElementById("input").disabled = true;
				clearInterval(run);
				enable_run();
				disable_pause();
				enable_step();
				stop_loading_animation();
			});

			document.getElementById("button_simulation_next_id").addEventListener("click", () => {
				document.getElementById("input").disabled = true;
				document.getElementById("input").disabled = true;
				evaluatePython_step_sim();
				enable_run();
				disable_pause();
				enable_step();
			});

			document.getElementById("button_simulation_refresh_id").addEventListener("click", () => {
				document.getElementById("input").disabled = true;
				clearInterval(run);
				evaluatePython_reset_sim();
				document.getElementById("input").disabled = false;
				enable_run();
				disable_pause();
				enable_step();
			});

			document.getElementById("button_binary_representation_id").addEventListener("click", () => {
				representation_mode = binary_representation;
				evaluatePython_update_tables();
			});

			document.getElementById("button_decimal_representation_id").addEventListener("click", () => {
				representation_mode = decimal_representation;
				evaluatePython_update_tables();
			});

			document.getElementById("button_hexa_representation_id").addEventListener("click", () => {
				representation_mode = hexa_representation;
				evaluatePython_update_tables();
			});

		});
		// ask if you really wanna leave the site
		window.onbeforeunload = function() {
			return true;
		};

	function disable_run() {
		document.getElementById("button_simulation_start_id").disabled = true;
		document.getElementById("button_simulation_start_id").style.backgroundColor = getComputedStyle(document.documentElement).getPropertyValue("--button_disabled_color");
	}
	function enable_run() {
		document.getElementById("button_simulation_start_id").disabled = false;
		document.getElementById("button_simulation_start_id").style.backgroundColor = getComputedStyle(document.documentElement).getPropertyValue("--button_green_color");
	}
	function disable_pause() {
		document.getElementById("button_simulation_pause_id").disabled = true;
		document.getElementById("button_simulation_pause_id").style.backgroundColor = getComputedStyle(document.documentElement).getPropertyValue("--button_disabled_color");
	}
	function enable_pause() {
		document.getElementById("button_simulation_pause_id").disabled = false;
		document.getElementById("button_simulation_pause_id").style.backgroundColor = getComputedStyle(document.documentElement).getPropertyValue("--button_green_color");
	}
	function disable_step() {
		document.getElementById("button_simulation_next_id").disabled = true;
		document.getElementById("button_simulation_next_id").style.backgroundColor = getComputedStyle(document.documentElement).getPropertyValue("--button_disabled_color");
	}
	function enable_step() {
		document.getElementById("button_simulation_next_id").disabled = false;
		document.getElementById("button_simulation_next_id").style.backgroundColor = getComputedStyle(document.documentElement).getPropertyValue("--button_blue_color");
	}
	function disable_reset() {
		document.getElementById("button_simulation_refresh_id").disabled = true;
		document.getElementById("button_simulation_refresh_id").style.backgroundColor = getComputedStyle(document.documentElement).getPropertyValue("--button_disabled_color");
	}
	function enable_reset() {
		document.getElementById("button_simulation_refresh_id").disabled = false;
		document.getElementById("button_simulation_refresh_id").style.backgroundColor = getComputedStyle(document.documentElement).getPropertyValue("--button_red_color");
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
