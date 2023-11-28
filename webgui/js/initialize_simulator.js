/**@type{ToySimulation} Holds the JS Simulation object.*/
var simulation;

/**
 * Loads pyodide, installs the archsim package and creates a ToySimulation.
 */
async function initialize() {
    // Load pyodide and install the package
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
    // Register all the relevant non-isa-specific nodes in an object.
    const domNodes = {
        runButton: document.getElementById("button-run-simulation"),
        pauseButton: document.getElementById("button-pause-simulation"),
        stepButton: document.getElementById("button-step-simulation"),
        resetButton: document.getElementById("button-reset-simulation"),
        uploadButton: document.getElementById("upload-button"),
        downloadButton: document.getElementById("download-button"),
        loadingIcon: document.getElementById("loading-spinner"),
        customSettingsContainer: document.getElementById(
            "isa-specific-settings-container"
        ),
        helpModalHeading: document.getElementById("help-modal-heading"),
        helpModalBody: document.getElementById("help-modal-body"),
        textContentContainer: document.getElementById("text-content-container"),
        visualizationsContainer: document.getElementById(
            "visualizations-container"
        ),
        textEditorSeparator: document.getElementById("text-editor-separator"),
        pageHeading: document.getElementById("page-heading"),
        mainContentContainer: document.getElementById("main-content-container"),
    };
    getPythonSimulation = pyodide.globals.get("get_simulation");
    // Create a JS Simulation object.
    simulation = new ToySimulation(getPythonSimulation("toy"), { ...domNodes }); // TODO: Allow other ISAs
}

/**
 * Tells the current Simulation object to reset and take a new ToySimulation pyProxy (because we dont reset those, we just throw them away).
 */
function resetSimulation() {
    simulation.reset(getPythonSimulation("toy")); // TODO: Allow other ISAs
}

initialize();
