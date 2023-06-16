const binary_representation = 0;
const decimal_representation = 1;
const hexa_representation = 2;
let representation_mode = binary_representation; //change this to set another default repr.

		let waiting_for_pyodide_flag = true
		window.addEventListener('DOMContentLoaded', function () {
			document.getElementById("button_simulation_start_id").addEventListener("click", () => {
				evaluatePython_run_sim();
			});

			document.getElementById("button_simulation_next_id").addEventListener("click", () => {
				evaluatePython_step_sim();
			});

			document.getElementById("button_simulation_refresh_id").addEventListener("click", () => {
				evaluatePython_reset_sim();
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
