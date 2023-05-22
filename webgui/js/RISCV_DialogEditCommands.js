/* ****************************************************************************** */

/* Class - RISCV_DialogEditCommands ********************************************* */

/* ****************************************************************************** */

class RISCV_DialogEditCommands {

	// private Classenattribute

	#_dialog;

	#_deploy_element;

	#_input_cmd;

	#_cmd_btn_ok;

	#_cmd_btn_cnl;

	#_command_execute_json;

	#_command_validate_json;

	#_main_cmd_table;

	#_main_memory_table;

	#_main_registers_table

	constructor(dialog_id, deploy_element_id, input_cmd_id, cmd_btn_ok_id, cmd_btn_cnl_id, main_cmd_table_id, main_memory_table_id, main_registers_table_id){

		this.#_dialog					= document.getElementById(dialog_id);

		this.#_deploy_element	 		= document.getElementById(deploy_element_id); // table body of dialog - add instructions dialog

		this.#_input_cmd				= document.getElementById(input_cmd_id);

		this.#_cmd_btn_ok	 			= document.getElementById(cmd_btn_ok_id); // Übernehmen in dialog

		this.#_cmd_btn_cnl	 			= document.getElementById(cmd_btn_cnl_id); //Abbrechen in dialog

		this.#_main_cmd_table			= document.getElementById(main_cmd_table_id);

		this.#_main_memory_table		= document.getElementById(main_memory_table_id);

		this.#_main_registers_table		= document.getElementById(main_registers_table_id);


		// create actual json and load it here

		let temp_validation_json_str 	= 	'{"cmd":[' 																					+

											'	{"cmd":"SUB ", 	"reg_expr":"^SUB [AT]{1}[0-9]{1}, [T]{1}[0-9]{1}, [T]{1}[0-9]{1}"},' 		+

											'	{"cmd":"SUBI", 	"reg_expr":"^SUBI[AT]{1}[0-9]{1}, [T]{1}[0-9]{1}, [T]{1}[0-9]{1}"} ' 		+

											']}';



		if(typeof temp_validation_json_str == "string" && temp_validation_json_str.length){



			this.#_command_validate_json= JSON.parse(temp_validation_json_str);

		}


		if(this.#_dialog && this.#_deploy_element && this.#_input_cmd && this.#_cmd_btn_ok && this.#_cmd_btn_cnl){

			this.#_input_cmd.addEventListener("input", () => {

				if(this.#_input_cmd.value.length > 0){

					if(this.#_command_validate_json){

						for(let val_idx = 0; val_idx < this.#_command_validate_json.cmd.length; val_idx ++){

							if(this.#_command_validate_json.cmd[val_idx].cmd == this.#_input_cmd.value.substr(0, 4)){// change to get substring until the first space

								this.#_input_cmd.pattern = this.#_command_validate_json.cmd[val_idx].reg_expr;

							}

						}

					}

				}

			});


			this.#_input_cmd.addEventListener("change", () => {

				if(this.#_input_cmd){

					if(this.#_input_cmd.pattern.length){

						let regex = RegExp(this.#_input_cmd.pattern);

						if(regex.test(this.#_input_cmd.value)){

							let cmd_json_str = '{"add":"' + document.getElementById("webapp_dialog_EditCommandsPcAddressID").value + '", "cmd":"' + this.#_input_cmd.value + '"}';

							let cmd_json = JSON.parse(cmd_json_str);

							if(cmd_json && this.#_command_execute_json){

								this.#_command_execute_json.cmd_list.push(cmd_json);

								this.#_input_cmd.value = "";
								this.#_initDialog();
							}

						}

					}

				}

			});



			this.#_cmd_btn_ok.addEventListener("click", () => {

				this.#_dialog.close();

				//simulation_json = JSON.parse(JSON.stringify(this.#_command_execute_json));

				this.updateMainCommandTable();
				this.updateMainMemoryTable();
				this.updateMainRegistersTable();

			});



			this.#_cmd_btn_cnl.addEventListener("click", () => {

				this.#_dialog.close();

				// do nothing

			});

		} else {

			return null;

		}

	}

	// private Methoden

	#_initDialog(){

		if(this.#_deploy_element && this.#_command_execute_json){

			while (this.#_deploy_element.firstChild) {

				this.#_deploy_element.removeChild(this.#_deploy_element.firstChild);

			}

			for(let cmd_idx = 0; cmd_idx < this.#_command_execute_json.cmd_list.length; cmd_idx ++){

				let html_el_table_td_row = document.createElement("tr");

				if(html_el_table_td_row){

					let html_el_table_td_pc = document.createElement("td");

					if(html_el_table_td_pc){

						html_el_table_td_pc.innerHTML = this.#_command_execute_json.cmd_list[cmd_idx].add;

						html_el_table_td_row.appendChild(html_el_table_td_pc);

					}

					let html_el_table_td_cmd = document.createElement("td");

					if(html_el_table_td_cmd){

					html_el_table_td_cmd.innerHTML = this.#_command_execute_json.cmd_list[cmd_idx].cmd;

						html_el_table_td_row.appendChild(html_el_table_td_cmd);

					}

					this.#_deploy_element.appendChild(html_el_table_td_row);

				}

				document.getElementById("webapp_dialog_EditCommandsPcAddressID").value = (cmd_idx * 4) + 4;

			}

		}

	}


	// public Methoden

	openDialog(){

		if(this.#_dialog){

			this.#_dialog.showModal();

		}

	}


	setCommandString(cmd_json_str){

		if(typeof cmd_json_str == "string" && cmd_json_str.length){

			this.#_command_execute_json = JSON.parse(cmd_json_str);

			if(this.#_deploy_element && this.#_command_execute_json){

				this.#_initDialog();

			}

		}

	}

	updateMainCommandTable(){

		if(this.#_main_cmd_table && this.#_command_execute_json){

			while (this.#_main_cmd_table.firstChild) {

				this.#_main_cmd_table.removeChild(this.#_main_cmd_table.firstChild);

			}

			for(let cmd_idx = 0; cmd_idx < this.#_command_execute_json.cmd_list.length; cmd_idx ++){

				let html_el_table_td_row = document.createElement("tr");

				if(html_el_table_td_row){

					let html_el_table_td_empty = document.createElement("td");
					let html_el_table_td_pc = document.createElement("td");

					if(html_el_table_td_pc){

						html_el_table_td_pc.innerHTML = this.#_command_execute_json.cmd_list[cmd_idx].add;

						html_el_table_td_row.appendChild(html_el_table_td_empty);
						html_el_table_td_row.appendChild(html_el_table_td_pc);

					}

					let html_el_table_td_cmd = document.createElement("td");

					if(html_el_table_td_cmd){

					html_el_table_td_cmd.innerHTML = this.#_command_execute_json.cmd_list[cmd_idx].cmd;

						html_el_table_td_row.appendChild(html_el_table_td_cmd);

					}

					this.#_main_cmd_table.appendChild(html_el_table_td_row);

				}

				document.getElementById("webapp_dialog_EditCommandsPcAddressID").value = cmd_idx;

			}

		}

	}

	updateMainMemoryTable(){

		if(this.#_main_memory_table && this.#_command_execute_json){

			while (this.#_main_memory_table.firstChild) {

				this.#_main_memory_table.removeChild(this.#_main_memory_table.firstChild);

			}

			for(let cmd_idx = 0; cmd_idx < this.#_command_execute_json.memory_list.length; cmd_idx ++){

				let html_el_table_td_row = document.createElement("tr");

				if(html_el_table_td_row){

					let html_el_table_td_empty = document.createElement("td");
					let html_el_table_td_pc = document.createElement("td");

					if(html_el_table_td_pc){

						html_el_table_td_pc.innerHTML = this.#_command_execute_json.memory_list[cmd_idx].index;

						html_el_table_td_row.appendChild(html_el_table_td_empty);
						html_el_table_td_row.appendChild(html_el_table_td_pc);

					}

					let html_el_table_td_cmd = document.createElement("td");

					if(html_el_table_td_cmd){

					html_el_table_td_cmd.innerHTML = this.#_command_execute_json.memory_list[cmd_idx].value;

						html_el_table_td_row.appendChild(html_el_table_td_cmd);

					}

					this.#_main_memory_table.appendChild(html_el_table_td_row);

				}

				document.getElementById("webapp_dialog_EditCommandsPcAddressID").value = cmd_idx;

			}

		}

	}




	updateMainRegistersTable(){

		if(this.#_main_registers_table && this.#_command_execute_json){

			while (this.#_main_registers_table.firstChild) {

				this.#_main_registers_table.removeChild(this.#_main_registers_table.firstChild);

			}

			for(let cmd_idx = 0; cmd_idx < this.#_command_execute_json.registers_list.length; cmd_idx ++){

				let html_el_table_td_row = document.createElement("tr");

				if(html_el_table_td_row){

					let html_el_table_td_empty = document.createElement("td");
					let html_el_table_td_pc = document.createElement("td");

					if(html_el_table_td_pc){

						html_el_table_td_pc.innerHTML = this.#_command_execute_json.registers_list[cmd_idx].index;

						html_el_table_td_row.appendChild(html_el_table_td_empty);
						html_el_table_td_row.appendChild(html_el_table_td_pc);

					}

					let html_el_table_td_cmd = document.createElement("td");

					if(html_el_table_td_cmd){

					html_el_table_td_cmd.innerHTML = this.#_command_execute_json.registers_list[cmd_idx].value;

						html_el_table_td_row.appendChild(html_el_table_td_cmd);

					}

					this.#_main_registers_table.appendChild(html_el_table_td_row);

				}

				document.getElementById("webapp_dialog_EditCommandsPcAddressID").value = cmd_idx;

			}

		}

	}

}
/* ------------------------------------------------------------------------------ */
