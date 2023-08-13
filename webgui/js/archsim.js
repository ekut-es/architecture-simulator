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
        //alert(Array.from(representations))
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
        //alert(Array.from(representations))
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
    // FIXME: I dont know what the following comment means, it might be outdated
    //ids und inner texts have to be changed then delete this comment
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
        )
            editor_vis.showHint(error_description);
        else {
            editor.showHint(error_description);
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
    update_IF_Stage: function (
        instruction,
        address_of_instruction,
        pc_plus_instruction_length
    ) {
        set_svg_text_simple_left_align("FetchText", instruction);
        set_svg_text_simple_right_align("IMInstr", instruction);
        if (address_of_instruction != "reset") {
            set_svg_text_simple_left_align(
                "IMReadAddress",
                address_of_instruction
            );
        } else {
            set_svg_text_simple_left_align("IMReadAddress", undefined);
        }
        if (
            address_of_instruction != undefined &&
            address_of_instruction != "reset"
        ) {
            set_svg_text_simple("PC", address_of_instruction);
            previous_pc = address_of_instruction;
        } else if (address_of_instruction == "reset") {
            set_svg_text_simple("PC", undefined);
        } else {
            set_svg_text_simple("PC", previous_pc);
        }
        set_svg_text_complex("FetchAddOutText", pc_plus_instruction_length);

        if (Number.isInteger(address_of_instruction)) {
            set_svg_colour("FetchPCOut", "blue");
        } else {
            set_svg_colour("FetchPCOut", "black");
        }

        if (Number.isInteger(pc_plus_instruction_length)) {
            set_svg_colour("FetchAddOut", "blue");
        } else {
            set_svg_colour("FetchAddOut", "black");
        }

        if (instruction != "" && instruction != undefined) {
            set_svg_colour("InstructionMemory", "blue");
        } else {
            set_svg_colour("InstructionMemory", "black");
        }
    },
    update_ID_Stage: function (
        register_read_addr_1,
        register_read_addr_2,
        register_read_data_1,
        register_read_data_2,
        imm,
        write_register,
        pc_plus_instruction_length,
        address_of_instruction,
        control_unit_signals
    ) {
        set_svg_text_simple_left_align("RFReadAddress1", register_read_addr_1);
        set_svg_text_simple_left_align("RFReadAddress2", register_read_addr_2);
        set_svg_text_simple_right_align("RFReadData1", register_read_data_1);
        set_svg_text_simple_right_align("RFReadData2", register_read_data_2);
        set_svg_text_simple("ImmGen", imm);
        set_svg_text_complex("DecodeInstructionMemory4Text", write_register);
        set_svg_text_complex(
            "DecodeFetchAddOutText",
            pc_plus_instruction_length
        );
        set_svg_text_complex(
            "DecodeUpperFetchPCOutText",
            address_of_instruction
        );
        set_svg_text_complex(
            "DecodeLowerFetchPCOutText",
            address_of_instruction
        );

        if (Number.isInteger(register_read_addr_1)) {
            set_svg_colour("DecodeInstructionMemory1", "blue");
        } else {
            set_svg_colour("DecodeInstructionMemory1", "black");
        }

        if (Number.isInteger(register_read_addr_2)) {
            set_svg_colour("DecodeInstructionMemory2", "blue");
        } else {
            set_svg_colour("DecodeInstructionMemory2", "black");
        }

        if (Number.isInteger(register_read_data_1)) {
            set_svg_colour("RegisterFileReadData1", "blue");
        } else {
            set_svg_colour("RegisterFileReadData1", "black");
        }

        if (Number.isInteger(register_read_data_2)) {
            set_svg_colour("RegisterFileReadData2", "blue");
        } else {
            set_svg_colour("RegisterFileReadData2", "black");
        }

        if (Number.isInteger(imm)) {
            set_svg_colour("DecodeInstructionMemory3", "blue");
        } else {
            set_svg_colour("DecodeInstructionMemory3", "black");
        }

        if (Number.isInteger(imm)) {
            set_svg_colour("g42637", "blue");
        } else {
            set_svg_colour("g42637", "black");
        }

        if (Number.isInteger(write_register)) {
            set_svg_colour("DecodeInstructionMemory4", "blue");
        } else {
            set_svg_colour("DecodeInstructionMemory4", "black");
        }

        if (Number.isInteger(pc_plus_instruction_length)) {
            set_svg_colour("DecodeFetchAddOut", "blue");
        } else {
            set_svg_colour("DecodeFetchAddOut", "black");
        }

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
    update_EX_Stage: function (
        alu_in_1,
        alu_in_2,
        register_read_data_1,
        register_read_data_2,
        imm,
        result,
        write_register,
        comparison,
        pc_plus_imm,
        pc_plus_instruction_length,
        address_of_instruction,
        control_unit_signals
    ) {
        control_signals = Array.from(control_unit_signals);
        if (Number.isInteger(control_signals[8])) {
            set_svg_colour("AluControl", "blue");
        } else {
            set_svg_colour("AluControl", "black");
        }

        if (control_signals[0] == true) {
            set_svg_colour("ControlUnitLeftRight3", "green");
        } else {
            set_svg_colour("ControlUnitLeftRight3", "black");
        }

        if (control_signals[1] == true) {
            set_svg_colour("ControlUnitLeftRight4", "green");
        } else {
            set_svg_colour("ControlUnitLeftRight4", "black");
        }

        set_svg_text_complex("ExecuteRightMuxOutText", alu_in_1);
        set_svg_text_complex("ExecuteLeftMuxOutText", alu_in_2);
        set_svg_text_complex(
            "ExecuteRegisterFileReadData2Text2",
            register_read_data_2
        );
        set_svg_text_complex("ExecuteImmGenText1", imm);
        set_svg_text_complex("ExecuteImmGenText3", imm);
        set_svg_text_simple_right_align("ALUResult-8-3-0", result);
        set_svg_text_complex("ExecuteInstructionMemory4Text", write_register);
        set_svg_text_complex("ExecuteAddText", pc_plus_imm);
        set_svg_text_complex(
            "ExecuteFetchAddOutText",
            pc_plus_instruction_length
        );
        set_svg_text_complex(
            "ExecuteUpperFetchPCOutText",
            address_of_instruction
        );

        if (Number.isInteger(alu_in_1)) {
            set_svg_colour("ExecuteRightMuxOut", "blue");
        } else {
            set_svg_colour("ExecuteRightMuxOut", "black");
        }

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

        if (Number.isInteger(register_read_data_2)) {
            set_svg_colour("ExecuteRegisterFileReadData2", "blue");
        } else {
            set_svg_colour("ExecuteRegisterFileReadData2", "black");
        }

        if (Number.isInteger(imm)) {
            set_svg_colour("ExecuteImmGen", "blue");
        } else {
            set_svg_colour("ExecuteImmGen", "black");
        }

        if (Number.isInteger(result)) {
            set_svg_colour("ExecuteAluResult", "blue");
        } else {
            set_svg_colour("ExecuteAluResult", "black");
        }

        if (Number.isInteger(write_register)) {
            set_svg_colour("ExecuteInstructionMemory4", "blue");
        } else {
            set_svg_colour("ExecuteInstructionMemory4", "black");
        }

        if (comparison == true) {
            set_svg_colour("ALUComparison", "green");
        } else {
            set_svg_colour("ALUComparison", "black");
        }

        if (Number.isInteger(pc_plus_imm)) {
            set_svg_colour("ExecuteAdd", "blue");
        } else {
            set_svg_colour("ExecuteAdd", "black");
        }

        if (Number.isInteger(pc_plus_instruction_length)) {
            set_svg_colour("ExecuteFetchAddOut", "blue");
        } else {
            set_svg_colour("ExecuteFetchAddOut", "black");
        }

        if (Number.isInteger(address_of_instruction)) {
            set_svg_colour("ExecuteUpperFetchPCOut", "blue");
            set_svg_colour("ExecuteLowerFetchPCOut", "blue");
        } else {
            set_svg_colour("ExecuteUpperFetchPCOut", "black");
            set_svg_colour("ExecuteLowerFetchPCOut", "black");
        }
    },
    update_MEM_Stage: function (
        memory_address,
        result,
        memory_write_data,
        memory_read_data,
        write_register,
        comparison,
        comparison_or_jump,
        pc_plus_imm,
        pc_plus_instruction_length,
        imm,
        control_unit_signals
    ) {
        control_signals = Array.from(control_unit_signals);
        if (control_signals[7] == true) {
            set_svg_colour("ControlUnitLeftRight1", "green");
        } else {
            set_svg_colour("ControlUnitLeftRight1", "black");
        }

        if (control_signals[9] == true) {
            set_svg_colour("ControlUnitLeft", "green");
        } else {
            set_svg_colour("ControlUnitLeft", "black");
        }

        set_svg_text_simple_left_align("DMAddress", memory_address);
        set_svg_text_complex("FetchLeftMuxInZeroText", result);
        set_svg_text_complex("MemoryExecuteAluResultText2", result);
        set_svg_text_simple_left_align("DMWriteData", memory_write_data);
        set_svg_text_simple_right_align("DMReadData", memory_read_data);
        set_svg_text_complex("MemoryInstructionMemory4Text", write_register);
        set_svg_text_complex("MemoryExecuteAddOutText", pc_plus_imm);
        set_svg_text_complex(
            "MemoryFetchAddOutText",
            pc_plus_instruction_length
        );
        set_svg_text_complex("MemoryImmGenText", imm);

        if (Number.isInteger(result) && Number.isInteger(memory_address)) {
            set_svg_colour("MemoryExecuteAluResult", "blue");
        } else {
            set_svg_colour("MemoryExecuteAluResult", "black");
        }

        if (Number.isInteger(memory_write_data)) {
            set_svg_colour("MemoryRegisterFileReadData2", "blue");
        } else {
            set_svg_colour("MemoryRegisterFileReadData2", "black");
        }

        if (Number.isInteger(memory_read_data)) {
            set_svg_colour("DataMemoryReadData", "blue");
        } else {
            set_svg_colour("DataMemoryReadData", "black");
        }

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

        if (Number.isInteger(pc_plus_imm)) {
            set_svg_colour("MemoryExecuteAddOut", "blue");
        } else {
            set_svg_colour("MemoryExecuteAddOut", "black");
        }

        if (Number.isInteger(pc_plus_instruction_length)) {
            set_svg_colour("MemoryFetchAddOut", "blue");
        } else {
            set_svg_colour("MemoryFetchAddOut", "black");
        }

        if (Number.isInteger(imm)) {
            set_svg_colour("MemoryImmGen", "blue");
        } else {
            set_svg_colour("MemoryImmGen", "black");
        }
    },
    update_WB_Stage: function (
        register_write_data,
        write_register,
        memory_read_data,
        alu_result,
        pc_plus_instruction_length,
        imm,
        control_unit_signals
    ) {
        control_signals = Array.from(control_unit_signals);

        if (Number.isInteger(control_signals[2])) {
            set_svg_colour("ControlUnitLeftRight2", "blue");
        } else {
            set_svg_colour("ControlUnitLeftRight2", "black");
        }
        set_svg_text_simple_left_align("RFWriteData", register_write_data);
        set_svg_text_simple_left_align("RFWriteFile", write_register);
        set_svg_text_complex(
            "WriteBackDataMemoryReadDataText",
            memory_read_data
        );
        set_svg_text_complex("WriteBackExecuteAluResultText", alu_result);
        set_svg_text_complex(
            "WriteBackFetchAddOutText",
            pc_plus_instruction_length
        );
        set_svg_text_complex("WriteBackImmGenText", imm);
        set_svg_text_complex("g89775", control_signals[2]);

        if (Number.isInteger(register_write_data)) {
            set_svg_colour("WriteBackMuxOut", "blue");
        } else {
            set_svg_colour("WriteBackMuxOut", "black");
        }

        if (Number.isInteger(write_register)) {
            set_svg_colour("WriteBackInstructionMemory4", "blue");
        } else {
            set_svg_colour("WriteBackInstructionMemory4", "black");
        }

        if (Number.isInteger(memory_read_data)) {
            set_svg_colour("WriteBackDataMemoryReadData", "blue");
        } else {
            set_svg_colour("WriteBackDataMemoryReadData", "black");
        }

        if (Number.isInteger(alu_result)) {
            set_svg_colour("WriteBackExecuteAluResult", "blue");
        } else {
            set_svg_colour("WriteBackExecuteAluResult", "black");
        }

        if (Number.isInteger(pc_plus_instruction_length)) {
            set_svg_colour("WriteBackFetchAddOut", "blue");
        } else {
            set_svg_colour("WriteBackFetchAddOut", "black");
        }

        if (Number.isInteger(imm)) {
            set_svg_colour("WriteBackImmGen", "blue");
        } else {
            set_svg_colour("WriteBackImmGen", "black");
        }
    },
    update_visualization: function (
        pc_plus_imm_or_pc_plus_instruction_length,
        pc_plus_imm_or_pc_plus_instruction_length_or_ALU_result
    ) {
        set_svg_text_complex(
            "FetchRightMuxOutText",
            pc_plus_imm_or_pc_plus_instruction_length
        );
        set_svg_text_complex(
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
            set_svg_colour("FetchLeftMuxOut", "blue");
        } else {
            set_svg_colour("FetchLeftMuxOut", "black");
        }
    },
};

output.value = "Output \n\nInitializing... ";
output_vis.value = "Output \n\nInitializing... ";

input.value = "add x1, x2, x3 \nlui x1, 1";
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
        let output_repr = Array.from(step_sim(input_str));
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
    start_loading_animation();
    let pyodide = await pyodideReadyPromise;
    stop_loading_animation();
    try {
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
    try {
        parse_input = pyodide.globals.get("parse_input");
        parse_input(input_str);
    } catch (err) {
        addToOutput(err);
    }
}
