const input = document.getElementById("input");

var previous_pc = 0;

var close_hint = false;

var previous_registers = {};
var previous_memory = {};

/**
 * Adds the given string to the output field.
 *
 * @param {string} s -  string to paste to the output field.
 */
function addToOutput(s) {
    const output = document.getElementById("output-field-id");
    output.innerText += ">>>" + input.value + "\n" + s + "\n";
    output.scrollTop = output.scrollHeight;
}

// Object containing functions to be exported to python
const archsim_js = {
    /**
     * Updates the TOY accu.
     * @param representations A Python Tuple containing the representations (binary, unsigned decimal, hexadecimal, signed decimal) for the accu.
     */
    toyUpdateAccu: function (representations) {
        document.getElementById("toy-accu-id").innerText =
            Array.from(representations)[reg_representation_mode];
    },
    /**
     * Clears the TOY memory table.
     */
    toyClearMemoryTable: function () {
        document.getElementById("toy-memory-table-body-id").innerHTML = "";
    },
    /**
     * Updates the TOY memory table.
     * @param {string} address The memory address
     * @param value_representations A Python Tuple containing the representations (binary, unsigned decimal, hexadecimal, signed decimal) for one value in the memory.
     * @param {string} instruction_representation The instruction the value represents.
     * @param {boolean} is_current_instruction Whether this entry is the current instruction. This will be marked in the table.
     */
    toyUpdateMemoryTable: function (
        address,
        value_representations,
        instruction_representation,
        is_current_instruction
    ) {
        value_representations_array = Array.from(value_representations);
        const value = value_representations_array[mem_representation_mode];
        const row = document
            .getElementById("toy-memory-table-body-id")
            .insertRow();
        const cell1 = row.insertCell();
        const cell2 = row.insertCell();
        const cell3 = row.insertCell();
        cell1.innerText = address;
        cell2.innerText = value;
        cell3.innerText = instruction_representation;
        if (previous_memory[address] !== value_representations_array[1]) {
            previous_memory[address] = value_representations_array[1];
            cell2.style.backgroundColor = "yellow";
        }
        if (is_current_instruction) {
            cell1.innerHTML = instructionArrow + cell1.innerHTML;
        }
    },
    get_selected_isa: function () {
        return selected_isa;
    },
    get_pipeline_mode: function () {
        return pipeline_mode;
    },
    get_hazard_detection: function () {
        return hazard_detection;
    },
    /**
     * Appends one row to the register table.
     *
     * @param {number} reg - index of the register
     * @param {Iterable} representations - iterable containing representations of the value stored in the register.
     * @param {string} abi_name - an alternative name for the register.
     */
    update_register_table: function (reg, representations, abi_name) {
        tr = document.createElement("tr");
        td1 = document.createElement("td");
        td1.innerText = "x" + reg;
        td2 = document.createElement("td");
        td2.innerText = Array.from(representations)[reg_representation_mode];
        td2.id = "val_x" + reg;
        if (previous_registers[reg] != Array.from(representations)[1]) {
            td2.style.backgroundColor = "yellow";
            previous_registers[reg] = Array.from(representations)[1];
        }
        td3 = document.createElement("td");
        td3.innerText = abi_name;
        td3.id = abi_name;
        tr.appendChild(td3);
        tr.appendChild(td1);
        tr.appendChild(td2);
        document.getElementById("riscv-register-table-body-id").appendChild(tr);
    },
    /**
     * Appends one row to the memory table.
     *
     * @param {string} address - memory address.
     * @param {Iterable} representations - iterable containing representations of the value stored at the given address.
     */
    update_memory_table: function (address, representations) {
        tr = document.createElement("tr");
        td1 = document.createElement("td");
        td1.innerText = address;
        td2 = document.createElement("td");
        td2.innerText = Array.from(representations)[mem_representation_mode];
        td2.id = "memory" + address;
        if (previous_memory[address] != Array.from(representations)[1]) {
            td2.style.backgroundColor = "yellow";
            previous_memory[address] = Array.from(representations)[1];
        }
        tr.appendChild(td1);
        tr.appendChild(td2);
        document.getElementById("riscv-memory-table-body-id").appendChild(tr);
    },
    /**
     * Appends one row to the instruction memory table.
     *
     * @param {string} address - address of the instruction.
     * @param {string} val - representation of the instruction.
     * @param {string} stage - the stage the instruction currently is in.
     */
    update_instruction_table: function (address, val, stage) {
        tr = document.createElement("tr");
        tr.id = address;
        td1 = document.createElement("td");
        td1.innerText = address;
        td2 = document.createElement("td");
        td2.innerText = val;
        td2.id = "instr" + address;
        td3 = document.createElement("td");
        td3.innerText = stage;
        if (stage == "Single") {
            td1.style.backgroundColor = "#2DA800";
            td2.style.backgroundColor = "#2DA800";
            td3.style.backgroundColor = "#2DA800";
        } else if (stage == "IF") {
            td1.style.backgroundColor = "#FFFD00";
            td2.style.backgroundColor = "#FFFD00";
            td3.style.backgroundColor = "#FFFD00";
        } else if (stage == "ID") {
            td1.style.backgroundColor = "#FFD700";
            td2.style.backgroundColor = "#FFD700";
            td3.style.backgroundColor = "#FFD700";
        } else if (stage == "EX") {
            td1.style.backgroundColor = "#CD78FF";
            td2.style.backgroundColor = "#CD78FF";
            td3.style.backgroundColor = "#CD78FF";
        } else if (stage == "MEM") {
            td1.style.backgroundColor = "#A37FFF";
            td2.style.backgroundColor = "#A37FFF";
            td3.style.backgroundColor = "#A37FFF";
        } else if (stage == "WB") {
            td1.style.backgroundColor = "#7283FF";
            td2.style.backgroundColor = "#7283FF";
            td3.style.backgroundColor = "#7283FF";
        }
        tr.appendChild(td1);
        tr.appendChild(td2);
        tr.appendChild(td3);
        document
            .getElementById("riscv-instruction-table-body-id")
            .appendChild(tr);
    },
    /**
     * Clears the memory table.
     */
    clear_memory_table: function () {
        this.clear_a_table(
            document.getElementById("riscv-memory-table-body-id")
        );
    },
    /**
     * Clears the register table.
     */
    clear_register_table: function () {
        this.clear_a_table(
            document.getElementById("riscv-register-table-body-id")
        );
    },
    /**
     * Clears the instruction memory table.
     */
    clear_instruction_table: function () {
        this.clear_a_table(
            document.getElementById("riscv-instruction-table-body-id")
        );
    },
    /**
     * Clears the given table.
     *
     * @param {HTMLElement} table - table to clear.
     */
    clear_a_table: function (table) {
        table.innerHTML = "";
    },
    /**
     * Set the ouput field to the given string.
     *
     * @param {string} str - string to set the output field to.
     */
    set_output: function (str) {
        const output = document.getElementById("output-field-id");
        output.innerText = str;
    },
    /**
     * Highlights a line in the text editor and displays the given message as hint.
     * Can be used to display parser exceptions.
     *
     * @param {number} position - line number (starting at 1).
     * @param {string} str - string to display.
     */
    highlight: function (position, str) {
        editor.addLineClass(position - 1, "background", "highlight");
        editor.refresh();
        str.toString = function () {
            return this.str;
        };
        output_str = str.toString();
        var error_description = {
            hint: function () {
                return {
                    from: position,
                    to: position,
                    list: [output_str, ""],
                };
            },
            customKeys: {
                Up: function (cm, handle) {
                    CodeMirror.commands.goLineUp(cm);
                    handle.close();
                },
                Down: function (cm, handle) {
                    CodeMirror.commands.goLineDown(cm);
                    handle.close();
                },
            },
        };

        if (!close_hint) editor.showHint(error_description);
    },
    /**
     * Removes all highlights from the editor.
     */
    remove_all_highlights: function () {
        for (let i = 0; i < editor.lineCount(); i++) {
            editor.removeLineClass(i, "background", "highlight");
        }
        editor.refresh();
        editor.closeHint();
    },
    /**
     * Highlights one row in the instruction table.
     *
     * @param {number} address - address of the instruction to highlight (which is not necessarily the same as the position in the table)
     */
    highlight_cmd_table: function (address) {
        table = document.getElementById("riscv-instruction-table-id");
        position = 1;
        for (; position < table.rows.length; position++) {
            if (Number(table.rows[position].cells[0].innerHTML) == address) {
                break;
            }
        }
        table.rows[position].cells[0].style.backgroundColor = "yellow";
        table.rows[position].cells[1].style.backgroundColor = "yellow";
    },
    update_toy_visualization: function (update_values) {
        console.log("===update_toy_visualization===");
        for (let i = 0; i < update_values.length; i++) {
            const update = update_values.get(i);
            const id = update.get(0);
            const action = update.get(1);
            const value = update.get(2);
            console.log(action + ' "' + value + '" ' + id);
            switch (action) {
                case "highlight":
                    toy_svg_highlight(id, value);
                    break;
                case "write":
                    toy_svg_set_text(id, value);
                    break;
                case "show":
                    toy_svg_show(id, value);
                    break;
            }
            update.destroy();
        }
        update_values.destroy();
    },
    /**
     * @returns {bool} whether the riscv visualization svg has finished loading
     */
    get_riscv_visualization_loaded: function () {
        return riscv_visualization_loaded;
    },
    /**
     * @returns {bool} whether the toy visualization svg has finished loading
     */
    get_toy_visualization_loaded: function () {
        return toy_visualization_loaded;
    },
    /**Update IF Stage:
     *
     * Updates all Elements located in the IF Stage of the Visualization.
     *
     * Parameters:
     * @param mnemonic - The mnemonic value of the instr currently in the IF Stage
     * @param instruction - The repr of the instr currently in the IF Stage
     * @param address_of_instruction - The address of the instr currently in the IF Stage
     * @param pc_plus_instruction_length - The PC of the instr plus the instr lenght
     */
    update_IF_Stage: function (parameters) {
        mnemonic = parameters.get("mnemonic");
        instruction = parameters.get("instruction");
        address_of_instruction = parameters.get("address_of_instruction");
        pc = parameters.get("PC");
        pc_plus_instruction_length = parameters.get(
            "pc_plus_instruction_length"
        );
        i_length = parameters.get("i-length");
        // Update the mnemonic
        set_svg_text_complex_middle_align("Fetch", mnemonic);
        // Update Instr[31-0]
        set_svg_text_complex_right_align(
            "InstructionMemoryInstrText",
            instruction
        );
        if (instruction != "" && instruction != undefined) {
            set_svg_colour("InstructionMemory", "blue");
        } else {
            set_svg_colour("InstructionMemory", "black");
        }

        // Updates the Read Adress in the instr memory, it is a value if the reset is not pressed, otherwise undefined
        set_svg_text_complex_left_align(
            "InstructionReadAddressText",
            address_of_instruction
        );

        // Updates the PC value:
        set_svg_text_complex_middle_align("PC", previous_pc);
        previous_pc = pc;
        if (Number.isInteger(address_of_instruction)) {
            set_svg_colour("FetchPCOut", "blue");
        } else {
            set_svg_colour("FetchPCOut", "black");
        }

        // Updates the result of the Adder that adds pc and instr lenght
        set_svg_text_complex_middle_align(
            "FetchAddOutText",
            pc_plus_instruction_length
        );
        if (Number.isInteger(pc_plus_instruction_length)) {
            set_svg_colour("FetchAddOut", "blue");
        } else {
            set_svg_colour("FetchAddOut", "black");
        }

        set_svg_text_complex_middle_align("I-LengthText", i_length);
        if (Number.isInteger(i_length)) {
            set_svg_colour("FetchI-Length", "blue");
        } else {
            set_svg_colour("FetchI-Length", "black");
        }
    },
    /**Update ID Stage:
     *
     * Updates all Elements located in the ID Stage of the Visualization.
     *
     * Parameters:
     * @param mnemonic - The mnemonic value of the instr currently in the ID Stage
     * @param register_read_addr_1 - The read addr 1 of the register file
     * @param register_read_addr_2 - The read addr 2 of the register file
     * @param register_read_data_1 - The read data 1 of the register file
     * @param register_read_data_2 - The read data 2 of the register file
     * @param imm - The imm of the current instr
     * @param write_register - The write register of the current instr
     * @param pc_plus_instruction_length - The PC of the instr plus the instr lenght
     * @param address_of_instruction - The address of the instr
     * @param control_unit_signals - The control unit signals
     */
    update_ID_Stage: function (parameters, control_unit_signals) {
        mnemonic = parameters.get("mnemonic");
        register_read_addr_1 = parameters.get("register_read_addr_1");
        register_read_addr_2 = parameters.get("register_read_addr_2");
        register_read_data_1 = parameters.get("register_read_data_1");
        register_read_data_2 = parameters.get("register_read_data_2");
        imm = parameters.get("imm");
        write_register = parameters.get("write_register");
        pc_plus_instruction_length = parameters.get(
            "pc_plus_instruction_length"
        );
        address_of_instruction = parameters.get("address_of_instruction");

        set_svg_text_complex_middle_align("Decode", mnemonic);

        set_svg_text_complex_left_align(
            "RegisterFileReadAddress1Text",
            register_read_addr_1
        );
        if (Number.isInteger(register_read_addr_1)) {
            set_svg_colour("DecodeInstructionMemory1", "blue");
        } else {
            set_svg_colour("DecodeInstructionMemory1", "black");
        }

        set_svg_text_complex_left_align(
            "RegisterFileReadAddress2Text",
            register_read_addr_2
        );
        if (Number.isInteger(register_read_addr_2)) {
            set_svg_colour("DecodeInstructionMemory2", "blue");
        } else {
            set_svg_colour("DecodeInstructionMemory2", "black");
        }

        set_svg_text_complex_right_align(
            "RegisterFileReadData1Text",
            register_read_data_1
        );
        if (Number.isInteger(register_read_data_1)) {
            set_svg_colour("RegisterFileReadData1", "blue");
        } else {
            set_svg_colour("RegisterFileReadData1", "black");
        }

        set_svg_text_complex_right_align(
            "RegisterFileReadData2Text",
            register_read_data_2
        );
        if (Number.isInteger(register_read_data_2)) {
            set_svg_colour("RegisterFileReadData2", "blue");
        } else {
            set_svg_colour("RegisterFileReadData2", "black");
        }

        set_svg_text_complex_middle_align("ImmGenText", imm);
        if (Number.isInteger(imm)) {
            set_svg_colour("ImmGenOut", "blue");
        } else {
            set_svg_colour("ImmGenOut", "black");
        }
        if (Number.isInteger(imm)) {
            set_svg_colour("DecodeInstructionMemory3", "blue");
        } else {
            set_svg_colour("DecodeInstructionMemory3", "black");
        }

        set_svg_text_complex_middle_align(
            "DecodeInstructionMemory4Text",
            write_register
        );
        if (Number.isInteger(write_register)) {
            set_svg_colour("DecodeInstructionMemory4", "blue");
        } else {
            set_svg_colour("DecodeInstructionMemory4", "black");
        }

        set_svg_text_complex_middle_align(
            "DecodeFetchAddOutText",
            pc_plus_instruction_length
        );
        if (Number.isInteger(pc_plus_instruction_length)) {
            set_svg_colour("DecodeFetchAddOut", "blue");
        } else {
            set_svg_colour("DecodeFetchAddOut", "black");
        }

        set_svg_text_complex_middle_align(
            "DecodeUpperFetchPCOutText",
            address_of_instruction
        );
        set_svg_text_complex_middle_align(
            "DecodeLowerFetchPCOutText",
            address_of_instruction
        );
        if (Number.isInteger(address_of_instruction)) {
            set_svg_colour("DecodeUpperFetchPCOut", "blue");
            set_svg_colour("DecodeLowerFetchPCOut", "blue");
            set_svg_colour("DecodeInstructionMemory", "blue");
        } else {
            set_svg_colour("DecodeUpperFetchPCOut", "black");
            set_svg_colour("DecodeLowerFetchPCOut", "black");
            set_svg_colour("DecodeInstructionMemory", "black");
        }
    },
    /**Update EX Stage:
     *
     * Updates all Elements located in the EX Stage of the Visualization.
     *
     * Parameters:
     * @param mnemonic - The mnemonic value of the instr currently in the EX Stage
     * @param alu_in_1 - The Value that goes into the first ALU input
     * @param alu_in_2 - The Value that goes into the second ALU input
     * @param register_read_data_1 - The read data 1 of the register file
     * @param register_read_data_2 - The read data 2 of the register file
     * @param imm - The imm of the current instr
     * @param result - The result of the ALU computation
     * @param write_register - The write register of the current instr
     * @param comparison - The result of the comparison unit of the ALU
     * @param pc_plus_imm - The imm plus the PC
     * @param pc_plus_instruction_length - The PC of the instr plus the instr lenght
     * @param address_of_instruction - The address of the instr
     * @param control_unit_signals - The control unit signals
     */
    update_EX_Stage: function (parameters, control_unit_signals) {
        mnemonic = parameters.get("mnemonic");
        alu_in_1 = parameters.get("alu_in_1");
        alu_in_2 = parameters.get("alu_in_2");
        register_read_data_1 = parameters.get("register_read_data_1");
        register_read_data_2 = parameters.get("register_read_data_2");
        imm = parameters.get("imm");
        result = parameters.get("result");
        write_register = parameters.get("write_register");
        comparison = parameters.get("comparison");
        pc_plus_imm = parameters.get("pc_plus_imm");
        pc_plus_instruction_length = parameters.get(
            "pc_plus_instruction_length"
        );
        address_of_instruction = parameters.get("address_of_instruction");
        alu_src_1 = control_unit_signals.get("alu_src_1");
        alu_src_2 = control_unit_signals.get("alu_src_2");
        alu_op = control_unit_signals.get("alu_op");

        set_svg_text_complex_middle_align("Execute", mnemonic);

        set_svg_text_complex_middle_align("ExecuteRightMuxOutText", alu_in_1);
        if (Number.isInteger(alu_in_1)) {
            set_svg_colour("ExecuteRightMuxOut", "blue");
        } else {
            set_svg_colour("ExecuteRightMuxOut", "black");
        }

        set_svg_text_complex_middle_align("ExecuteLeftMuxOutText", alu_in_2);
        if (Number.isInteger(alu_in_2)) {
            set_svg_colour("ExecuteLeftMuxOut", "blue");
        } else {
            set_svg_colour("ExecuteLeftMuxOut", "black");
        }

        if (Number.isInteger(register_read_data_1)) {
            set_svg_colour("ExecuteRegisterFileReadData1", "blue");
        } else {
            set_svg_colour("ExecuteRegisterFileReadData1", "black");
        }

        set_svg_text_complex_middle_align(
            "ExecuteRegisterFileReadData2Text2",
            register_read_data_2
        );
        if (Number.isInteger(register_read_data_2)) {
            set_svg_colour("ExecuteRegisterFileReadData2", "blue");
        } else {
            set_svg_colour("ExecuteRegisterFileReadData2", "black");
        }

        set_svg_text_complex_middle_align("ExecuteImmGenText1", imm);
        set_svg_text_complex_middle_align("ExecuteImmGenText3", imm);
        if (Number.isInteger(imm)) {
            set_svg_colour("ExecuteImmGen", "blue");
        } else {
            set_svg_colour("ExecuteImmGen", "black");
        }

        set_svg_text_complex_left_align("ALUResultText", result);
        if (Number.isInteger(result)) {
            set_svg_colour("ExecuteAluResult", "blue");
        } else {
            set_svg_colour("ExecuteAluResult", "black");
        }

        set_svg_text_complex_middle_align(
            "ExecuteInstructionMemory4Text",
            write_register
        );
        if (Number.isInteger(write_register)) {
            set_svg_colour("ExecuteInstructionMemory4", "blue");
        } else {
            set_svg_colour("ExecuteInstructionMemory4", "black");
        }

        set_svg_text_complex_middle_align("ExecuteAddText", pc_plus_imm);
        if (Number.isInteger(pc_plus_imm)) {
            set_svg_colour("ExecuteAdd", "blue");
        } else {
            set_svg_colour("ExecuteAdd", "black");
        }

        set_svg_text_complex_middle_align(
            "ExecuteFetchAddOutText",
            pc_plus_instruction_length
        );
        if (Number.isInteger(pc_plus_instruction_length)) {
            set_svg_colour("ExecuteFetchAddOut", "blue");
        } else {
            set_svg_colour("ExecuteFetchAddOut", "black");
        }

        set_svg_text_complex_middle_align(
            "ExecuteUpperFetchPCOutText",
            address_of_instruction
        );
        if (Number.isInteger(address_of_instruction)) {
            set_svg_colour("ExecuteUpperFetchPCOut", "blue");
            set_svg_colour("ExecuteLowerFetchPCOut", "blue");
        } else {
            set_svg_colour("ExecuteUpperFetchPCOut", "black");
            set_svg_colour("ExecuteLowerFetchPCOut", "black");
        }

        if (comparison == true) {
            set_svg_colour("ALUComparison", "green");
        } else {
            set_svg_colour("ALUComparison", "black");
        }

        if (alu_src_1 == true) {
            set_svg_colour("ControlUnitLeftRight3", "green");
        } else {
            set_svg_colour("ControlUnitLeftRight3", "black");
        }

        if (alu_src_2 == true) {
            set_svg_colour("ControlUnitLeftRight4", "green");
        } else {
            set_svg_colour("ControlUnitLeftRight4", "black");
        }

        if (Number.isInteger(alu_op)) {
            set_svg_colour("AluControl", "blue");
        } else {
            set_svg_colour("AluControl", "black");
        }
    },
    /**Update MEM Stage:
     *
     * Updates all Elements located in the MEM Stage of the Visualization
     *
     * Parameters:
     * @param mnemonic - The mnemonic value of the instr currently in the EX Stage
     * @param memory_address - The address where the data memory is accessed at
     * @param result - The result of the ALU computation
     * @param memory_write_data - The data that will be written to memory
     * @param memory_read_data - The data that is read from memory
     * @param write_register - The write register of the current instr
     * @param comparison - The result of the comparison unit of the ALU
     * @param comparison_or_jump - The result of the or gate and the signal whether to modify pc or not
     * @param pc_plus_imm - The PC of the instr plus the imm of the instr
     * @param pc_plus_instruction_length - The PC of the instr plus the instr lenght
     * @param address_of_instruction - The address of the instr
     * @param imm - The imm of the instr
     * @param control_unit_signals - The control unit signals
     */
    update_MEM_Stage: function (parameters, control_unit_signals) {
        mnemonic = parameters.get("mnemonic");
        memory_address = parameters.get("memory_address");
        result = parameters.get("result");
        memory_write_data = parameters.get("memory_write_data");
        memory_read_data = parameters.get("memory_read_data");
        write_register = parameters.get("write_register");
        comparison = parameters.get("comparison");
        comparison_or_jump = parameters.get("comparison_or_jump");
        pc_plus_imm = parameters.get("pc_plus_imm");
        pc_plus_instruction_length = parameters.get(
            "pc_plus_instruction_length"
        );
        imm = parameters.get("imm");
        jump = control_unit_signals.get("jump");
        alu_to_pc = control_unit_signals.get("alu_to_pc");

        set_svg_text_complex_middle_align("Memory", mnemonic);

        set_svg_text_complex_left_align(
            "DataMemoryAddressText",
            memory_address
        );
        set_svg_text_complex_middle_align("MemoryExecuteAluResultText", result);
        set_svg_text_complex_middle_align(
            "MemoryExecuteAluResultText2",
            result
        );
        if (Number.isInteger(result) && Number.isInteger(memory_address)) {
            set_svg_colour("MemoryExecuteAluResult", "blue");
        } else {
            set_svg_colour("MemoryExecuteAluResult", "black");
        }

        set_svg_text_complex_left_align(
            "DataMemoryWriteDataText",
            memory_write_data
        );
        if (Number.isInteger(memory_write_data)) {
            set_svg_colour("MemoryRegisterFileReadData2", "blue");
        } else {
            set_svg_colour("MemoryRegisterFileReadData2", "black");
        }

        set_svg_text_complex_right_align(
            "DataMemoryReadDataText",
            memory_read_data
        );
        if (Number.isInteger(memory_read_data)) {
            set_svg_colour("DataMemoryReadData", "blue");
        } else {
            set_svg_colour("DataMemoryReadData", "black");
        }

        set_svg_text_complex_middle_align(
            "MemoryInstructionMemory4Text",
            write_register
        );
        if (Number.isInteger(write_register)) {
            set_svg_colour("MemoryInstructionMemory4", "blue");
        } else {
            set_svg_colour("MemoryInstructionMemory4", "black");
        }

        if (comparison == true) {
            set_svg_colour("MemoryALUComparison", "green");
        } else {
            set_svg_colour("MemoryALUComparison", "black");
        }

        if (comparison_or_jump == true) {
            set_svg_colour("MemoryJumpOut", "green");
        } else {
            set_svg_colour("MemoryJumpOut", "black");
        }

        set_svg_text_complex_middle_align(
            "MemoryExecuteAddOutText",
            pc_plus_imm
        );
        if (Number.isInteger(pc_plus_imm)) {
            set_svg_colour("MemoryExecuteAddOut", "blue");
        } else {
            set_svg_colour("MemoryExecuteAddOut", "black");
        }

        set_svg_text_complex_middle_align(
            "MemoryFetchAddOutText",
            pc_plus_instruction_length
        );
        if (Number.isInteger(pc_plus_instruction_length)) {
            set_svg_colour("MemoryFetchAddOut", "blue");
        } else {
            set_svg_colour("MemoryFetchAddOut", "black");
        }

        set_svg_text_complex_middle_align("MemoryImmGenText", imm);
        if (Number.isInteger(imm)) {
            set_svg_colour("MemoryImmGen", "blue");
        } else {
            set_svg_colour("MemoryImmGen", "black");
        }

        if (jump == true) {
            set_svg_colour("ControlUnitLeftRight", "green");
        } else {
            set_svg_colour("ControlUnitLeftRight", "black");
        }

        if (alu_to_pc == true) {
            set_svg_colour("ControlUnitLeft", "green");
        } else {
            set_svg_colour("ControlUnitLeft", "black");
        }
    },
    /**Update WB Stage:
     *
     * Updates all Elements located in the WB Stage of the Visualization.
     *
     * Parameters:
     * @param mnemonic - The mnemonic value of the instr currently in the EX Stage
     * @param register_write_data - The data that is written into the Register file
     * @param write_register - The write register of the current instr
     * @param memory_read_data - The data that is read from the memory
     * @param alu_result - The result of the ALU computation
     * @param pc_plus_instruction_length - The PC of the instr plus the instr lenght
     * @param imm - The imm of the instr
     * @param control_unit_signals - The control unit signals
     */
    update_WB_Stage: function (parameters, control_unit_signals) {
        mnemonic = parameters.get("mnemonic");
        register_write_data = parameters.get("register_write_data");
        write_register = parameters.get("write_register");
        memory_read_data = parameters.get("memory_read_data");
        alu_result = parameters.get("alu_result");
        pc_plus_instruction_length = parameters.get(
            "pc_plus_instruction_length"
        );
        imm = parameters.get("imm");
        wbsrc = control_unit_signals.get("wb_src");

        set_svg_text_complex_middle_align("WriteBack", mnemonic);

        set_svg_text_complex_left_align(
            "RegisterFileWriteDataText",
            register_write_data
        );
        if (Number.isInteger(register_write_data)) {
            set_svg_colour("WriteBackMuxOut", "blue");
        } else {
            set_svg_colour("WriteBackMuxOut", "black");
        }

        set_svg_text_complex_left_align(
            "RegisterFileWriteRegisterText",
            write_register
        );
        if (Number.isInteger(write_register)) {
            set_svg_colour("WriteBackInstructionMemory4", "blue");
        } else {
            set_svg_colour("WriteBackInstructionMemory4", "black");
        }

        set_svg_text_complex_middle_align(
            "WriteBackDataMemoryReadDataText",
            memory_read_data
        );
        if (Number.isInteger(memory_read_data)) {
            set_svg_colour("WriteBackDataMemoryReadData", "blue");
        } else {
            set_svg_colour("WriteBackDataMemoryReadData", "black");
        }

        set_svg_text_complex_middle_align(
            "WriteBackExecuteAluResultText",
            alu_result
        );
        if (Number.isInteger(alu_result)) {
            set_svg_colour("WriteBackExecuteAluResult", "blue");
        } else {
            set_svg_colour("WriteBackExecuteAluResult", "black");
        }

        set_svg_text_complex_middle_align(
            "WriteBackFetchAddOutText",
            pc_plus_instruction_length
        );
        if (Number.isInteger(pc_plus_instruction_length)) {
            set_svg_colour("WriteBackFetchAddOut", "blue");
        } else {
            set_svg_colour("WriteBackFetchAddOut", "black");
        }

        set_svg_text_complex_middle_align("WriteBackImmGenText", imm);
        if (Number.isInteger(imm)) {
            set_svg_colour("WriteBackImmGen", "blue");
        } else {
            set_svg_colour("WriteBackImmGen", "black");
        }

        set_svg_text_complex_middle_align("wbsrc", wbsrc);
        if (Number.isInteger(wbsrc)) {
            set_svg_colour("ControlUnitLeftRight2", "blue");
        } else {
            set_svg_colour("ControlUnitLeftRight2", "black");
        }
    },
    update_visualization: function (
        pc_plus_imm_or_pc_plus_instruction_length,
        pc_plus_imm_or_pc_plus_instruction_length_or_ALU_result
    ) {
        set_svg_text_complex_middle_align(
            "FetchRightMuxOutText",
            pc_plus_imm_or_pc_plus_instruction_length
        );
        set_svg_text_complex_middle_align(
            "FetchLeftMuxOutText",
            pc_plus_imm_or_pc_plus_instruction_length_or_ALU_result
        );
        if (Number.isInteger(pc_plus_imm_or_pc_plus_instruction_length)) {
            set_svg_colour("FetchRightMuxOut", "blue");
        } else {
            set_svg_colour("FetchRightMuxOut", "black");
        }

        if (
            Number.isInteger(
                pc_plus_imm_or_pc_plus_instruction_length_or_ALU_result
            )
        ) {
            set_svg_colour("path2453-0-7-7-9", "blue");
            set_svg_colour("path2453-2-5-7-0-7-5-1-0-4", "blue");
            set_svg_colour("path2453-2-5-7-0-7-6-2-29", "blue");
        } else {
            set_svg_colour("path2453-0-7-7-9", "black");
            set_svg_colour("path2453-2-5-7-0-7-5-1-0-4", "black");
            set_svg_colour("path2453-2-5-7-0-7-6-2-29", "black");
        }
    },
};

input.value = "";
/**
 * Initialize pyodide.
 * @returns pyodide.
 */
async function main() {
    start_loading_visuals();
    let pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    if (window.location.origin == "http://127.0.0.1:3000") {
        await micropip.install(
            window.location.origin +
                "/dist/architecture_simulator-0.1.0-py3-none-any.whl"
        );
    } else {
        await micropip.install(
            window.location.href +
                "/dist/architecture_simulator-0.1.0-py3-none-any.whl"
        );
    }

    pyodide.registerJsModule("archsim_js", archsim_js);
    await pyodide.runPython(`
from architecture_simulator.gui.webgui import *
sim_init()
    `);
    const output = document.getElementById("output-field-id");
    output.innerText += "Ready!\n";
    stop_loading_visuals();
    return pyodide;
}
let pyodideReadyPromise = main();

/**
 * Executes one step in the simulation and updates the visuals accordingly.
 */
async function evaluatePython_step_sim() {
    let pyodide = await pyodideReadyPromise;
    input_str = input.value;
    step_sim = pyodide.globals.get("step_sim");
    let output_repr = Array.from(step_sim(input_str, is_run_simulation));
    if (output_repr[1] == false) {
        stop_timer();
        stop_loading_animation();
        disable_pause();
        disable_step();
        if (selected_isa == "toy") {
            disable_double_step();
        }
        disable_run();
        clearInterval(run);
    }
    if (!output_repr[2]) {
        // Only update the performance metrics if there was no exception
        // otherwise it would overwrite the printed exception
        set_output_message(output_repr[0]);
    }
}

async function evaluatePython_toy_single_step() {
    let pyodide = await pyodideReadyPromise;
    const single_step = pyodide.globals.get("toy_single_step");
    const get_next_cycle = pyodide.globals.get("toy_get_next_cycle");
    input_str = input.value;
    let output_repr = Array.from(single_step(input_str));
    if (output_repr[1] == false) {
        stop_timer();
        stop_loading_animation();
        disable_pause();
        disable_step();
        disable_double_step();
        disable_run();
        clearInterval(run);
    } else {
        if (get_next_cycle() == 1) {
            enable_double_step();
            enable_run();
        } else {
            disable_double_step();
            disable_run();
        }
    }
    if (!output_repr[2]) {
        // Only update the performance metrics if there was no exception
        // otherwise it would overwrite the printed exception
        set_output_message(output_repr[0]);
    }
}

async function update_ui_async() {
    let pyodide = await pyodideReadyPromise;
    update_ui = pyodide.globals.get("update_ui");
    update_ui();
}

/**
 * Resumes the performance metrics timer.
 */
async function resume_timer() {
    let pyodide = await pyodideReadyPromise;
    resume_timer = pyodide.globals.get("resume_timer");
    resume_timer();
}

/**
 * Stops/pauses the performance metrics timer.
 */
async function stop_timer() {
    let pyodide = await pyodideReadyPromise;
    stop_timer = pyodide.globals.get("stop_timer");
    stop_timer();
}

/**
 * Updates the performance metrics output field with the performance metrics it pulls from python.
 */
async function update_performance_metrics() {
    let pyodide = await pyodideReadyPromise;
    get_performance_metrics_str = pyodide.globals.get(
        "get_performance_metrics_str"
    );
    set_output_message(get_performance_metrics_str());
}

function set_output_message(str) {
    const output = document.getElementById("output-field-id");
    output.innerText = str;
}

/**
 * Resets the simulation and sets it to the currently selected pipeline mode.
 */
async function evaluatePython_reset_sim(pipeline_mode) {
    // resets the saved memory for highlighting changed values, so that new values can be highlighted
    previous_memory = {};
    previous_registers = {};

    start_loading_animation();
    let pyodide = await pyodideReadyPromise;
    stop_loading_animation();
    try {
        previous_pc = 0; // resets the PC for the visualization
        reset_sim = pyodide.globals.get("reset_sim");
        reset_sim();
        set_output_message("");
    } catch (err) {
        addToOutput(err);
    }
}

/**
 * Updates the instruction/register/memory tables (and updates the visualization).
 */
async function evaluatePython_update_tables() {
    let pyodide = await pyodideReadyPromise;
    try {
        update_tables = pyodide.globals.get("update_tables");
        update_tables();
    } catch (err) {
        addToOutput(err);
    }
}

/**
 * Parses the text from the input field and loads it into the simulation.
 */
async function evaluatePython_parse_input() {
    let pyodide = await pyodideReadyPromise;
    input_str = input.value;
    try {
        parse_input = pyodide.globals.get("parse_input");
        parse_input(input_str);
    } catch (err) {
        addToOutput(err);
    }
}

/**
 * Loads the settings JSON using Python, to avoid local JS import errors.
 */
async function evaluatePython_load_settings() {
    let pyodide = await pyodideReadyPromise;
    try {
        load_settings = pyodide.globals.get("load_settings");
        return load_settings();
    } catch (err) {
        addToOutput(err);
    }
}
