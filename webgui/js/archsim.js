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

var previous_registers = {};
var previous_memory = {};

function addToOutput(s) {
    output.value += ">>>" + input.value + "\n" + s + "\n";
    output.scrollTop = output.scrollHeight;
    output_vis.value += ">>>" + input.value + "\n" + s + "\n";
    output_vis.scrollTop = output_vis.scrollHeight;
}

// Object containing functions to be exported to python
const archsim_js = {
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
    // update_single_register: function(reg, val) {
    //     document.getElementById("val_x"+reg).innerText = val
    // },
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
        td1.innerText = address;
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
    // update_single_memory_address: function(address, val) {
    //     try{
    //     document.getElementById("memory"+address).innerText = val
    //     }
    //     catch
    //     {
    //     tr = document.createElement("tr")
    //     td1 = document.createElement("td")
    //     td1.innerText = address
    //     td2 = document.createElement("td")
    //     td2.innerText = val
    //     td2.id = "memory"+address
    //     tr.appendChild(td1)
    //     tr.appendChild(td2)
    //     memory.appendChild(tr)
    //     }
    // },
    //ids und inner texts have to be changed then delete this comment
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
            td1.style.backgroundColor = "#FFEC00";
            td2.style.backgroundColor = "#FFEC00";
            td3.style.backgroundColor = "#FFEC00";
        } else if (stage == "ID") {
            td1.style.backgroundColor = "#FFC900";
            td2.style.backgroundColor = "#FFC900";
            td3.style.backgroundColor = "#FFC900";
        } else if (stage == "EX") {
            td1.style.backgroundColor = "#695CC4";
            td2.style.backgroundColor = "#695CC4";
            td3.style.backgroundColor = "#695CC4";
        } else if (stage == "MEM") {
            td1.style.backgroundColor = "#2A17B1";
            td2.style.backgroundColor = "#2A17B1";
            td3.style.backgroundColor = "#2A17B1";
        } else if (stage == "WB") {
            td1.style.backgroundColor = "#580EAD";
            td2.style.backgroundColor = "#580EAD";
            td3.style.backgroundColor = "#580EAD";
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
            td1_vis.style.backgroundColor = "#FFEC00";
            td2_vis.style.backgroundColor = "#FFEC00";
            td3_vis.style.backgroundColor = "#FFEC00";
        } else if (stage == "ID") {
            td1_vis.style.backgroundColor = "#FFC900";
            td2_vis.style.backgroundColor = "#FFC900";
            td3_vis.style.backgroundColor = "#FFC900";
        } else if (stage == "EX") {
            td1_vis.style.backgroundColor = "#695CC4";
            td2_vis.style.backgroundColor = "#695CC4";
            td3_vis.style.backgroundColor = "#695CC4";
        } else if (stage == "MEM") {
            td1_vis.style.backgroundColor = "#2A17B1";
            td2_vis.style.backgroundColor = "#2A17B1";
            td3_vis.style.backgroundColor = "#2A17B1";
        } else if (stage == "WB") {
            td1_vis.style.backgroundColor = "#580EAD";
            td2_vis.style.backgroundColor = "#580EAD";
            td3_vis.style.backgroundColor = "#580EAD";
        }
        tr_vis.appendChild(td1_vis);
        tr_vis.appendChild(td2_vis);
        tr_vis.appendChild(td3_vis);
        instructions_vis.appendChild(tr_vis);
    },
    clear_memory_table: function () {
        this.clear_a_table(memory);
        this.clear_a_table(memory_vis);
    },
    clear_register_table: function () {
        this.clear_a_table(registers);
        this.clear_a_table(registers_vis);
    },
    clear_instruction_table: function () {
        this.clear_a_table(instructions);
        this.clear_a_table(instructions_vis);
    },
    clear_a_table: function (table) {
        table.innerHTML = "";
    },
    set_output: function (str) {
        output.value = str;
        output_vis.value = str;
    },
    highlight: function (position, str) {
        //editor.removeLineClass(position-1, "background", "highlight")
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
    highlight_cmd_table: function (position) {
        table = document.getElementById("gui_cmd_table_id");
        table.rows[position + 1].cells[0].style.backgroundColor = "yellow";
        table.rows[position + 1].cells[1].style.backgroundColor = "yellow";
        console.log(table.innerHTML);

        table2 = document.getElementById("vis_gui_cmd_table_id");
        table2.rows[position + 1].cells[0].style.backgroundColor = "yellow";
        table2.rows[position + 1].cells[1].style.backgroundColor = "yellow";
        console.log(table2.innerHTML);
    },
    update_IF_Stage: function (instruction, address_of_instruction) {},
    update_ID_Stage: function (
        register_read_addr_1,
        register_read_addr_2,
        register_read_data_1,
        register_read_data_2,
        imm,
        control_unit_signals
    ) {},
    update_EX_Stage: function (
        alu_in_1,
        alu_in_2,
        register_read_data_2,
        imm,
        result,
        comparison,
        pc_plus_imm,
        control_unit_signals
    ) {},
    update_MEM_Stage: function (
        memory_address,
        result,
        memory_write_data,
        memory_read_data,
        comparison,
        pc_src,
        pc_plus_imm,
        control_unit_signals
    ) {},
    update_WB_Stage: function (
        register_write_data,
        write_register,
        memory_read_data,
        alu_result,
        control_unit_signals
    ) {},
};

output.value = "Output \n\nInitializing... ";
output_vis.value = "Output \n\nInitializing... ";

input.value = "add x1, x2, x3 \nlui x1, 1";
performance_metrics.value = "Performance Metrics";
performance_metrics_vis.value = "Performance Metrics";
// init Pyodide
async function main() {
    start_loading_visuals();
    let pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    console.log(window.location.protocol);
    console.log(window.location.href);
    console.log(window.location.origin);
    console.log(window.location.hash);
    console.log(window.location.host);
    console.log(window.location.hostname);
    console.log(window.location.pathname);
    console.log(window.location.port);
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

async function resume_timer() {
    let pyodide = await pyodideReadyPromise;
    resume_timer = pyodide.globals.get("resume_timer");
    resume_timer();
}

async function stop_timer() {
    let pyodide = await pyodideReadyPromise;
    stop_timer = pyodide.globals.get("stop_timer");
    stop_timer();
}

async function update_performance_metrics() {
    let pyodide = await pyodideReadyPromise;
    get_performance_metrics = pyodide.globals.get("get_performance_metrics");
    //output.value = get_performance_metrics();
    performance_metrics.value = get_performance_metrics();
    performance_metrics_vis.value = get_performance_metrics();
}

// async function evaluatePython_run_sim() {
//     start_loading_animation();
//     let pyodide = await pyodideReadyPromise;
//     stop_loading_animation();
//     input_str = input.value
//     let output;
//     try {
//         // reset the sim before executing run
//         reset_sim = pyodide.globals.get("reset_sim");
//         reset_sim();

//         run_sim = pyodide.globals.get("run_sim");
//         let output = run_sim(input_str);
//         addToOutput(output);
//     } catch (err) {
//         addToOutput(err);
//     }
// }

async function evaluatePython_reset_sim(pipeline_mode) {
    start_loading_animation();
    let pyodide = await pyodideReadyPromise;
    stop_loading_animation();
    try {
        reset_sim = pyodide.globals.get("reset_sim");
        reset_sim(pipeline_mode);
        output.value = "";
        output_vis.value = "";
        performance_metrics.value = "";
        performance_metrics_vis.value = "";
    } catch (err) {
        addToOutput(err);
    }
}

async function evaluatePython_update_tables() {
    let pyodide = await pyodideReadyPromise;
    try {
        update_tables = pyodide.globals.get("update_tables");
        let output = update_tables();
        var table = document.getElementById("gui_cmd_table_id");
        var rows = table.rows;
        rows[0].classList.add("highlight");
        console.log(rows[2].classList);
        console.log(table.innerHTML);
    } catch (err) {
        addToOutput(err);
    }
}

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

//function update_output(output_string) {
//    output.value = output_string;
//}
