let dialogEditCommands = null;


		let waiting_for_pyodide_flag = true
		window.addEventListener('DOMContentLoaded', function () {
			document.getElementById("button_simulation_start_id").addEventListener("click", () => {
				evaluatePython_run_sim();
				//dialogEditCommands.setCommandString(simulation_json);
			});

			document.getElementById("button_simulation_next_id").addEventListener("click", () => {
				evaluatePython_step_sim();
				//dialogEditCommands.setCommandString(simulation_json);
			});

			document.getElementById("button_simulation_refresh_id").addEventListener("click", () => {
				evaluatePython_reset_sim();
				//dialogEditCommands.setCommandString(simulation_json);
			});

		});
		// ask if you really wanna leave the site
		window.onbeforeunload = function() {
			return true;
		};
