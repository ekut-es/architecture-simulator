const output = document.getElementById("output");
const output_vis = document.getElementById("vis_output");
const registers = document.getElementById("gui_registers_table_body_id");
const registers_vis = document.getElementById(
    "vis_gui_registers_table_body_id"
);
const memory = document.getElementById("gui_memory_table_body_id");
const memory_vis = document.getElementById("vis_gui_memory_table_body_id");
const instructions = document.getElementById("gui_cmd_table_body_id");
const instructions_vis = document.getElementById("vis_gui_cmd_table_body_id");
const input = document.getElementById("input");
const input_vis = document.getElementById("vis_input");
const performance_metrics = document.getElementById("performance_metrics");
const performance_metrics_vis = document.getElementById(
    "vis_performance_metrics"
);

var previous_pc = 0;

var close_hint = false;

const pipeline_svg = document.getElementById(
    "visualization_pipeline"
).contentDocument;

var previous_registers = {};
var previous_memory = {};

/**
 * Adds the given string to the output field.
 *
 * @param {string} s -  string to paste to the output field.
 */
function addToOutput(s) {
    output.value += ">>>" + input.value + "\n" + s + "\n";
    output.scrollTop = output.scrollHeight;
    output_vis.value += ">>>" + input.value + "\n" + s + "\n";
    output_vis.scrollTop = output_vis.scrollHeight;
}

// Object containing functions to be exported to python
const archsim_js = {
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
        vis_highlight = false;
        tr = document.createElement("tr");
        td1 = document.createElement("td");
        td1.innerText = "x" + reg;
        td2 = document.createElement("td");
        td2.innerText = Array.from(representations)[reg_representation_mode];
        td2.id = "val_x" + reg;
        if (previous_registers[reg] != Array.from(representations)[1]) {
            td2.style.backgroundColor = "yellow";
            previous_registers[reg] = Array.from(representations)[1];
            vis_highlight = true;
        }
        td3 = document.createElement("td");
        td3.innerText = abi_name;
        td3.id = abi_name;
        tr.appendChild(td3);
        tr.appendChild(td1);
        tr.appendChild(td2);
        registers.appendChild(tr);

        tr_vis = document.createElement("tr");
        td1_vis = document.createElement("td");
        td1_vis.innerText = "x" + reg;
        td2_vis = document.createElement("td");
        td2_vis.innerText =
            Array.from(representations)[reg_representation_mode];
        td2_vis.id = "val_x" + reg;
        if (vis_highlight) {
            td2_vis.style.backgroundColor = "yellow";
        }
        td3_vis = document.createElement("td");
        td3_vis.innerText = abi_name;
        td3_vis.id = abi_name;
        tr_vis.appendChild(td3_vis);
        tr_vis.appendChild(td1_vis);
        tr_vis.appendChild(td2_vis);
        registers_vis.appendChild(tr_vis);
    },
    /**
     * Appends one row to the memory table.
     *
     * @param {string} address - memory address.
     * @param {Iterable} representations - iterable containing representations of the value stored at the given address.
     */
    update_memory_table: function (address, representations) {
        vis_highlight = false;
        tr = document.createElement("tr");
        td1 = document.createElement("td");
        td1.innerText = address;
        td2 = document.createElement("td");
        td2.innerText = Array.from(representations)[mem_representation_mode];
        td2.id = "memory" + address;
        if (previous_memory[address] != Array.from(representations)[1]) {
            td2.style.backgroundColor = "yellow";
            previous_memory[address] = Array.from(representations)[1];
            vis_highlight = true;
        }
        tr.appendChild(td1);
        tr.appendChild(td2);
        memory.appendChild(tr);

        tr_vis = document.createElement("tr");
        td1_vis = document.createElement("td");
        td1_vis.innerText = address;
        td2_vis = document.createElement("td");
        td2_vis.innerText =
            Array.from(representations)[mem_representation_mode];
        td2_vis.id = "memory" + address;
        if (vis_highlight) {
            td2_vis.style.backgroundColor = "yellow";
        }
        tr_vis.appendChild(td1_vis);
        tr_vis.appendChild(td2_vis);
        memory_vis.appendChild(tr_vis);
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
        instructions.appendChild(tr);

        tr_vis = document.createElement("tr");
        tr_vis.id = address;
        td1_vis = document.createElement("td");
        td1_vis.innerText = address;
        td2_vis = document.createElement("td");
        td2_vis.innerText = val;
        td2_vis.id = "instr" + address;
        td3_vis = document.createElement("td");
        td3_vis.innerText = stage;
        if (stage == "IF") {
            td1_vis.style.backgroundColor = "#FFFD00";
            td2_vis.style.backgroundColor = "#FFFD00";
            td3_vis.style.backgroundColor = "#FFFD00";
        } else if (stage == "ID") {
            td1_vis.style.backgroundColor = "#FFD700";
            td2_vis.style.backgroundColor = "#FFD700";
            td3_vis.style.backgroundColor = "#FFD700";
        } else if (stage == "EX") {
            td1_vis.style.backgroundColor = "#CD78FF";
            td2_vis.style.backgroundColor = "#CD78FF";
            td3_vis.style.backgroundColor = "#CD78FF";
        } else if (stage == "MEM") {
            td1_vis.style.backgroundColor = "#A37FFF";
            td2_vis.style.backgroundColor = "#A37FFF";
            td3_vis.style.backgroundColor = "#A37FFF";
        } else if (stage == "WB") {
            td1_vis.style.backgroundColor = "#5A1BFF";
            td2_vis.style.backgroundColor = "#5A1BFF";
            td3_vis.style.backgroundColor = "#5A1BFF";
        }
        tr_vis.appendChild(td1_vis);
        tr_vis.appendChild(td2_vis);
        tr_vis.appendChild(td3_vis);
        instructions_vis.appendChild(tr_vis);
    },
    /**
     * Clears the memory table.
     */
    clear_memory_table: function () {
        this.clear_a_table(memory);
        this.clear_a_table(memory_vis);
    },
    /**
     * Clears the register table.
     */
    clear_register_table: function () {
        this.clear_a_table(registers);
        this.clear_a_table(registers_vis);
    },
    /**
     * Clears the instruction memory table.
     */
    clear_instruction_table: function () {
        this.clear_a_table(instructions);
        this.clear_a_table(instructions_vis);
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
        output.value = str;
        output_vis.value = str;
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
        editor_vis.addLineClass(position - 1, "background", "highlight");
        editor_vis.refresh();
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

        if (
            document.getElementById("VisualizationTabContent").style.display ==
            "block"
        ) {
            if (!close_hint) editor_vis.showHint(error_description);
        } else {
            if (!close_hint) editor.showHint(error_description);
        }
    },
    /**
     * Removes all highlights from the editor.
     */
    remove_all_highlights: function () {
        for (let i = 0; i < editor.lineCount(); i++) {
            editor.removeLineClass(i, "background", "highlight");
            editor_vis.removeLineClass(i, "background", "highlight");
        }
        editor.refresh();
        editor_vis.refresh();
        editor.closeHint();
        editor_vis.closeHint();
    },
    /**
     * Highlights one row in the instruction table.
     *
     * @param {number} address - address of the instruction to highlight (which is not necessarily the same as the position in the table)
     */
    highlight_cmd_table: function (address) {
        table = document.getElementById("gui_cmd_table_id");
        position = 1;
        for (; position < table.rows.length; position++) {
            if (Number(table.rows[position].cells[0].innerHTML) == address) {
                break;
            }
        }
        table.rows[position].cells[0].style.backgroundColor = "yellow";
        table.rows[position].cells[1].style.backgroundColor = "yellow";

        table2 = document.getElementById("vis_gui_cmd_table_id");
        table2.rows[position].cells[0].style.backgroundColor = "yellow";
        table2.rows[position].cells[1].style.backgroundColor = "yellow";
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

output.value = "Output \n\nInitializing... ";
output_vis.value = "Output \n\nInitializing... ";

input.value = "";
performance_metrics.value = "Performance Metrics";
performance_metrics_vis.value = "Performance Metrics";
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
    output.value += "Ready!\n";
    performance_metrics.value += "...";
    output_vis.value += "Ready!\n";
    performance_metrics_vis.value += "...";
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
    try {
        step_sim = pyodide.globals.get("step_sim");
        let output_repr = Array.from(step_sim(input_str, is_run_simulation));
        if (output_repr[1] == false) {
            stop_timer();
            stop_loading_animation();
            disable_pause();
            disable_step();
            disable_run();
            clearInterval(run);
        }
        update_performance_metrics();
    } catch (err) {
        output.value = err;
        output_vis.value = err;
        stop_loading_animation();
        disable_pause();
        disable_step();
        disable_run();
        clearInterval(run);
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
 * Updates the performance metrics output field.
 */
async function update_performance_metrics() {
    let pyodide = await pyodideReadyPromise;
    get_performance_metrics_str = pyodide.globals.get(
        "get_performance_metrics_str"
    );
    performance_metrics.value = get_performance_metrics_str();
    performance_metrics_vis.value = get_performance_metrics_str();
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
        output.value = "";
        output_vis.value = "";
        performance_metrics.value = "";
        performance_metrics_vis.value = "";
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
    vis_input_str = vis_input.value;
    try {
        parse_input = pyodide.globals.get("parse_input");
        if (
            document.getElementById("VisualizationTabContent").style.display ==
            "block"
        ) {
            parse_input(vis_input_str);
        } else {
            parse_input(input_str);
        }
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
