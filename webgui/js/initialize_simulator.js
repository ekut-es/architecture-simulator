/**@type{ToySimulation} Holds the JS Simulation object.*/
let simulation = null;

/**@type{string} The name of the ISA that is currently loaded.*/
let currentISA = "riscv";

/**@type{Object} Stores some nodes that the simulations can use.*/
let domNodes;

/**@type{function():pyProxy} Returns a pyProxy Toy Simulation object.*/
let getToyPythonSimulation;

/**@type{function(string, boolean):pyProxy} Returns a pyProxy RiscvSimulation object. arg0 is the pipeline mode,
 * which must be either "five_stage_pipeline" or "single_stage_pipeline".
 * arg1 is whether to enable data hazard detection or not (only relevant for five_stage_pipeline)
 */
let getRiscvPythonSimulation;

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

    const urlParams = new URLSearchParams(window.location.search);
    const isaParam = urlParams.get("isa");
    if (isaParam !== null) {
        switch (isaParam.toLowerCase()) {
            case "riscv":
                currentISA = "riscv";
                break;
            default:
                currentISA = "toy";
        }
    }

    const isaSelector = getRadioSettingsRow(
        "ISA",
        ["RISC-V", "TOY"],
        ["riscv", "toy"],
        "select-isa",
        switchIsa,
        currentISA
    );
    document
        .getElementById("isa-selector-settings-container")
        .append(isaSelector);

    // Register all the relevant non-isa-specific nodes in an object.
    domNodes = {
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
        isaSelector: isaSelector,
    };
    getRiscvPythonSimulation = pyodide.globals.get("get_riscv_simulation");
    getToyPythonSimulation = pyodide.globals.get("get_toy_simulation");
    switchIsa(currentISA);
}

/**
 * Tells the current Simulation object to reset.
 */
function resetSimulation() {
    simulation.resetCustom();
}

/**
 * Switches the ISA. Destroys the current Simulation and creates a new one of the specified type.
 * @param {string} isa Name of the ISA.
 */
function switchIsa(isa) {
    if (simulation !== null) {
        simulation.removeContentFromDOM();
    }
    currentISA = isa;

    switch (isa) {
        case "riscv":
            simulation = new RiscvSimulation({
                ...domNodes,
            });
            break;
        case "toy":
            simulation = new ToySimulation({
                ...domNodes,
            });
            break;
        default:
            console.error(`Specified isa '${isa}' does not exist.`);
    }
}

/**
 * Enables or disables all ISA selector buttons.
 * @param {boolean} doEnable Whether to enable or disable the buttons.
 */
function enableIsaSelector(doEnable = true) {
    const inputs = domNodes.isaSelector.children
        .item(1)
        .querySelectorAll("input");
    for (let input of inputs) {
        input.disable = !doEnable;
    }
}

initialize();
