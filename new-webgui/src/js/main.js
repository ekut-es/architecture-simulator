import "/src/css/styles.css";
import "/src/css/splitjs.css";
import { ToySimulation } from "./toy/toy_simulation";
import { RiscvSimulation } from "./riscv/riscv_simulation";
import { getRadioSettingsRow } from "./util";
import "/src/scss/bootstrap.scss";
import * as bootstrap from "bootstrap";
import { loadPyodide } from "pyodide";
import { editorView } from "./editor";
import { saveTextAsFile } from "./editor";

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

/**@type{function():string} Returns the last error message from python. */
let getLastPythonError;

/**
 * Loads pyodide, installs the archsim package and creates a ToySimulation.
 */
async function initialize() {
    // Load pyodide and install the package
    const pyodide = await initializePyodide();
    getRiscvPythonSimulation = pyodide.globals.get("get_riscv_simulation");
    getToyPythonSimulation = pyodide.globals.get("get_toy_simulation");
    getLastPythonError = pyodide.globals.get("get_last_error");

    updateCurrentIsa();

    const isaSelector = installIsaSelectorSettings();

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
        editor: editorView,
    };
    switchIsa(currentISA);

    addButtonEventListeners(domNodes);
}

function updateCurrentIsa() {
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
}

async function initializePyodide() {
    const pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.22.1/full/",
    });
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    if (
        window.location.origin == "http://127.0.0.1:3000" ||
        window.location.origin == "http://127.0.0.1:5173" ||
        window.location.origin == "http://127.0.0.1:4173" ||
        window.location.origin == "http://localhost:5173"
    ) {
        await micropip.install(
            window.location.origin +
                //"http://127.0.0.1:3000" +
                //    "/dist/architecture_simulator-0.1.0-py3-none-any.whl"
                "/architecture_simulator-0.1.0-py3-none-any.whl"
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
    return pyodide;
}

function installIsaSelectorSettings() {
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
    return isaSelector;
}

function addButtonEventListeners(domNodes) {
    domNodes.runButton.addEventListener("click", () => simulation.run());
    domNodes.pauseButton.addEventListener("click", () => simulation.pause());
    domNodes.stepButton.addEventListener("click", () => simulation.step());
    domNodes.resetButton.addEventListener("click", () => simulation.reset());
    domNodes.downloadButton.addEventListener("click", () => saveTextAsFile());
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
            simulation = new RiscvSimulation(
                {
                    ...domNodes,
                },
                getRiscvPythonSimulation,
                getLastPythonError
            );
            break;
        case "toy":
            simulation = new ToySimulation(
                {
                    ...domNodes,
                },
                getToyPythonSimulation,
                getLastPythonError
            );
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
