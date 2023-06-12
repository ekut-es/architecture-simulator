let dialogEditCommands = null;

		let simulation_json = '{"cmd_list":[{"add":"0x0000", "cmd":"ADD A0, T0, T2"}, {"add":"0x0004", "cmd":"ADD A0, T0, T2"}], "registers_list":[], "memory_list":[]}';

		let waiting_for_pyodide_flag = true
		window.addEventListener('DOMContentLoaded', function () {
			dialogEditCommands = new RISCV_DialogEditCommands( 	"webapp_dialog_EditCommandsID",
																"webapp_dialog_EditCommandsTableBodyID",
																"webapp_dialog_EditCommandsTextInputID",
																"webapp_dialog_EditCommandsFooterBtnOkID",
																"webapp_dialog_EditCommandsFooterBtnCnlID",
                                "gui_cmd_table_body_id",
								"gui_memory_table_body_id",
								"gui_registers_table_body_id"
								);
				dialogEditCommands.setCommandString(simulation_json);

			document.getElementById("button_gui_cmd_edit_id").addEventListener("click", () => {
				if(dialogEditCommands){
					dialogEditCommands.setCommandString(simulation_json); //placeholder, load json from simulator
					dialogEditCommands.openDialog();
				}
			});

			document.getElementById("button_simulation_start_id").addEventListener("click", () => {
				evaluatePython_run_sim();
				dialogEditCommands.setCommandString(simulation_json);
			});

			document.getElementById("button_simulation_next_id").addEventListener("click", () => {
				evaluatePython_step_sim();
				dialogEditCommands.setCommandString(simulation_json);
			});

			document.getElementById("button_simulation_stop_id").addEventListener("click", () => {
				evaluatePython_reset_sim();
				dialogEditCommands.setCommandString(simulation_json);
			});

		});
		// ask if you really wanna leave the site
		window.onbeforeunload = function() {
			return true;
		};
