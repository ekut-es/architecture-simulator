const output = document.getElementById("output");
const registers = document.getElementById("gui_registers_table_id");
const memory = document.getElementById("gui_memory_table_id");
const instructions = document.getElementById("gui_cmd_table_body_id");
const input = document.getElementById("input");
const loading_screen = document.getElementById("loading_screen");

function addToOutput(s) {
    output.value += ">>>" + input.value + "\n" + s + "\n";
    output.scrollTop = output.scrollHeight;
}

// Object containing functions to be exported to python
const archsim_js = {
    update_register_table: function(reg, val) {
        tr = document.createElement("tr")
        empty_td0 = document.createElement("td");
        td1 = document.createElement("td")
        td1.innerText = "x"+reg
        td2 = document.createElement("td")
        td2.innerText = val
        td2.id = "val_x"+reg
        tr.appendChild(empty_td0)
        tr.appendChild(td1)
        tr.appendChild(td2)
        registers.appendChild(tr)
    },
    // update_single_register: function(reg, val) {
    //     document.getElementById("val_x"+reg).innerText = val
    // },
    update_memory_table: function(address, val) {
        tr = document.createElement("tr")
        empty_td0 = document.createElement("td");
        td1 = document.createElement("td")
        td1.innerText = address
        td2 = document.createElement("td")
        td2.innerText = val
        td2.id = "memory"+address
        tr.appendChild(empty_td0)
        tr.appendChild(td1)
        tr.appendChild(td2)
        memory.appendChild(tr)
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
    update_instruction_table: function(address, val) {
        tr = document.createElement("tr")
        empty_td0 = document.createElement("td");
        td1 = document.createElement("td")
        td1.innerText = address
        td2 = document.createElement("td")
        td2.innerText = val
        td2.id = "instr"+address
        tr.appendChild(empty_td0)
        tr.appendChild(td1)
        tr.appendChild(td2)
        instructions.appendChild(tr)
    },
    clear_memory_table: function() {
        this.clear_a_table(memory);

    },
    clear_register_table: function() {
        this.clear_a_table(registers);
    },
    clear_instruction_table: function() {
        this.clear_a_table(instructions);
    },
    clear_a_table: function(table) {
        while (table.childNodes.length > 2) {
            table.removeChild(table.lastChild);
        }
    }
};

output.value = "Output \n\nInitializing... ";
input.value = "add x1, x2, x3"
// init Pyodide
async function main() {
    loading_screen.showModal()
    let pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install("/dist/architecture_simulator-0.1.0-py3-none-any.whl");
    pyodide.registerJsModule("archsim_js", archsim_js);
    await pyodide.runPython(`
from architecture_simulator.gui.webgui import *
sim_init()
    `);
    output.value += "Ready!\n";
    loading_screen.close();
    return pyodide;
}
let pyodideReadyPromise = main();

async function evaluatePython_step_sim() {
    loading_screen.showModal()
    let pyodide = await pyodideReadyPromise;
    loading_screen.close();
    input_str = input.value
    try {
        step_sim = pyodide.globals.get("step_sim");
        let output = step_sim(input_str);
        addToOutput(output);
    } catch (err) {
        addToOutput(err);
    }
}

async function evaluatePython_run_sim() {
    loading_screen.showModal()
    let pyodide = await pyodideReadyPromise;
    loading_screen.close();
    input_str = input.value
    try {
        run_sim = pyodide.globals.get("run_sim");
        let output = run_sim(input_str);
        addToOutput(output);
    } catch (err) {
        addToOutput(err);
    }
}

async function evaluatePython_reset_sim() {
    loading_screen.showModal()
    let pyodide = await pyodideReadyPromise;
    loading_screen.close();
    //registers.innerHTML = ""
    //memory.innerHTML = ""
    try {
        reset_sim = pyodide.globals.get("reset_sim");
        let output = reset_sim();
        addToOutput(output);
    } catch (err) {
        addToOutput(err);
    }
}
