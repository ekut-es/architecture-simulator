const binary_representation = 0;
const decimal_representation = 1;
const hexa_representation = 2;
let representation_mode = binary_representation; //change this to set another default repr.
var run;

		let waiting_for_pyodide_flag = true
		window.addEventListener('DOMContentLoaded', function () {
			document.getElementById("button_simulation_start_id").addEventListener("click", () => {
				document.getElementById("input").disabled = true;
				disable_run();
				enable_pause();
				disable_step();
				if(run) {
					clearInterval(run);
				}
				try{
					run = setInterval(evaluatePython_step_sim,10);
				} catch {
					clearInterval(run);
				}
			});

			document.getElementById("button_simulation_pause_id").addEventListener("click", () => {
				document.getElementById("input").disabled = true;
				enable_run();
				disable_pause();
				enable_step();
				clearInterval(run);
			});

			document.getElementById("button_simulation_next_id").addEventListener("click", () => {
				document.getElementById("input").disabled = true;
				enable_run();
				disable_pause();
				enable_step();
				document.getElementById("input").disabled = true;
				evaluatePython_step_sim();
			});

			document.getElementById("button_simulation_refresh_id").addEventListener("click", () => {
				document.getElementById("input").disabled = true;
				enable_run();
				disable_pause();
				enable_step();
				clearInterval(run);
				evaluatePython_reset_sim();
				document.getElementById("input").disabled = false;
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