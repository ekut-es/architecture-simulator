const output = document.getElementById("output");
const code = document.getElementById("code");
const registers = document.getElementById("registers");


function addToOutput(s) {
    output.value += ">>>" + code.value + "\n" + s + "\n";
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

async function evaluatePython() {
    let pyodide = await pyodideReadyPromise;
    try {
        exec_instr = pyodide.globals.get("exec_instr");
        let output = exec_instr(code.value);
        addToOutput(output);
    } catch (err) {
        addToOutput(err);
    }
}
