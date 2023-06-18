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
    update_register_table: function(reg, representations) {
        tr = document.createElement("tr")
        empty_td0 = document.createElement("td");
        td1 = document.createElement("td")
        td1.innerText = "x"+reg
        td2 = document.createElement("td")
        td2.innerText = Array.from(representations)[representation_mode]
        td2.id = "val_x"+reg
        tr.appendChild(empty_td0)
        tr.appendChild(td1)
        tr.appendChild(td2)
        registers.appendChild(tr)
    },
    // update_single_register: function(reg, val) {
    //     document.getElementById("val_x"+reg).innerText = val
    // },
    update_memory_table: function(address, representations) {
        tr = document.createElement("tr")
        empty_td0 = document.createElement("td");
        td1 = document.createElement("td")
        td1.innerText = address
        td2 = document.createElement("td")
        //alert(Array.from(representations))
        td2.innerText = Array.from(representations)[representation_mode]
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
input.value = "add x1, x2, x3 \nlui x1, 1"
// init Pyodide
async function main() {
    loading_screen.showModal()
    let pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    console.log(window.location.protocol)
    console.log(window.location.href)
    console.log(window.location.origin)
    console.log(window.location.hash)
    console.log(window.location.host)
    console.log(window.location.hostname)
    console.log(window.location.pathname)
    console.log(window.location.port)
    await micropip.install(window.location.origin+"/archsim/dist/architecture_simulator-0.1.0-py3-none-any.whl");
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
        let output =  Array.from(step_sim(input_str))[0];
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
    let output;
    try {
        // reset the sim before executing run
        reset_sim = pyodide.globals.get("reset_sim");
        reset_sim();

        simulation_ended_flag = false
        //run_sim = pyodide.globals.get("run_sim");
        //let output = run_sim(input_str);
        step_sim = pyodide.globals.get("step_sim");

        while(simulation_ended_flag == false)
        {
            simulation_ended_flag = Array.from(step_sim(input_str))[1]
            output =  Array.from(step_sim(input_str))[0];
        }
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

async function evaluatePython_update_tables() {
    loading_screen.showModal()
    let pyodide = await pyodideReadyPromise;
    loading_screen.close();
    //registers.innerHTML = ""
    //memory.innerHTML = ""
    try {
        update_tables = pyodide.globals.get("update_tables");
        let output = update_tables();
    } catch (err) {
        addToOutput(err);
    }
}
