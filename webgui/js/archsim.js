const output = document.getElementById("output");
const registers = document.getElementById("registers");
const memory = document.getElementById("memory");
const input = document.getElementById("input");

function addToOutput(s) {
    output.value += ">>>" + input.value + "\n" + s + "\n";
    output.scrollTop = output.scrollHeight;
}

// Object containing functions to be exported to python
const archsim_js = {
    append_register: function(reg, val) {
        tr = document.createElement("tr")
        td1 = document.createElement("td")
        td1.innerText = "x"+reg
        td2 = document.createElement("td")
        td2.innerText = val
        td2.id = "val_x"+reg
        tr.appendChild(td1)
        tr.appendChild(td2)
        registers.appendChild(tr)
    },
    update_register: function(reg, val) {
        document.getElementById("val_x"+reg).innerText = val
    },
    append_registers: function(reg_json_str) {
        temp_simulation_json = JSON.parse(simulation_json)
        temp_reg_json_str = JSON.parse(reg_json_str)
        temp_simulation_json.reg_list = temp_reg_json_str
        simulation_json = JSON.stringify(temp_simulation_json)
    },
    append_memory: function(address, val) {
        tr = document.createElement("tr")
        td1 = document.createElement("td")
        td1.innerText = address
        td2 = document.createElement("td")
        td2.innerText = val
        td2.id = "memory"+address
        tr.appendChild(td1)
        tr.appendChild(td2)
        memory.appendChild(tr)
    },
    update_memory: function(address, val) {
        try{
        document.getElementById("memory"+address).innerText = val
        }
        catch
        {
        tr = document.createElement("tr")
        td1 = document.createElement("td")
        td1.innerText = address
        td2 = document.createElement("td")
        td2.innerText = val
        td2.id = "memory"+address
        tr.appendChild(td1)
        tr.appendChild(td2)
        memory.appendChild(tr)
        }
    },
    append_memories: function(mem_json_str) {
        temp_simulation_json = JSON.parse(simulation_json)
        temp_mem_json_str = JSON.parse(mem_json_str)
        temp_simulation_json.mem_list = temp_mem_json_str
        simulation_json = JSON.stringify(temp_simulation_json)
    },
    append_instructions: function(cmd_json_str) {
        //setCommandString(cmd_json_str)
    }
};

output.value = "Initializing... ";
// init Pyodide
async function main() {
    let pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install(window.location.origin+"/dist/architecture_simulator-0.1.0-py3-none-any.whl");
    pyodide.registerJsModule("archsim_js", archsim_js);
    await pyodide.runPython(`
from architecture_simulator.gui.webgui import *
sim_init()
    `);
    output.value += "Ready!\n";
    return pyodide;
}
let pyodideReadyPromise = main();

async function evaluatePython_step_sim() {
    let pyodide = await pyodideReadyPromise;
    alert("step")
    alert(input.value.split("\n"))
    cmd_json_str = JSON.stringify(input.value.split("\n"))
    try {
        step_sim = pyodide.globals.get("step_sim");
        let output = step_sim(cmd_json_str);
        addToOutput(output);
    } catch (err) {
        addToOutput(err);
    }
}

async function evaluatePython_run_sim() {
    let pyodide = await pyodideReadyPromise;
    alert("run")
    alert(input.value.split("\n"))
    cmd_json_str = JSON.stringify(input.value.split("\n"))
    alert(cmd_json_str)
    try {
        run_sim = pyodide.globals.get("run_sim");
        let output = run_sim(cmd_json_str);
        addToOutput(output);
    } catch (err) {
        addToOutput(err);
    }
}

async function evaluatePython_reset_sim() {
    let pyodide = await pyodideReadyPromise;
    registers.innerHTML = ""
    memory.innerHTML = ""
    try {
        reset_sim = pyodide.globals.get("reset_sim");
        let output = reset_sim();
        addToOutput(output);
    } catch (err) {
        addToOutput(err);
    }
}
