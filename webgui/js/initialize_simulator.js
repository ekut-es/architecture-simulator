var simulation;

async function initialize() {
    const pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    if (window.location.origin == "http://127.0.0.1:3000") {
        await micropip.install(
            window.location.origin +
                "/dist/architecture_simulator-0.1.0-py3-none-any.whl"
        );
    } else {
        // Find out the URL of the server, but dont include any parameters or index.html
        let url = window.location.origin + window.location.pathname;
        if (url.endsWith("index.html")) {
            url = url.slice(0, -10);
        }
        await micropip.install(
            url + "/dist/architecture_simulator-0.1.0-py3-none-any.whl"
        );
    }
    await pyodide.runPython(`
from architecture_simulator.gui.new_webgui import *
    `);
    getPythonSimulation = pyodide.globals.get("get_simulation");
    simulation = new ToySimulation(getPythonSimulation("toy")); // TODO: Allow other ISAs
}

function resetSimulation() {
    simulation.reset(getPythonSimulation("toy")); // TODO: Allow other ISAs
}

initialize();
