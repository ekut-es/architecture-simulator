import "./scss/styles.scss";
import "./css/main.css";
import "./css/splitjs.css";

import { createApp } from "vue";

import App from "./App.vue";

import * as bootstrap from "bootstrap";
import { loadPyodide } from "pyodide";

import { globalSettings } from "./js/global_settings";

import { setPyodide as setRiscvPyodide } from "@/js/riscv_simulation_store";
import { setPyodide as setToyPyodide } from "@/js/toy_simulation_store";

async function initializePyodide() {
    const pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.22.1/full/",
    });
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install("architecture_simulator-0.1.0-py3-none-any.whl");
    await pyodide.runPython(`
from architecture_simulator.gui.webgui import *
`);
    return pyodide;
}

/**
 * Returns the default ISA ('riscv' right now) or what was specified in the
 * 'isa' GET parameter if it is a valid ISA.
 * @returns {String} the name of the chosen ISA.
 */
function getDefaultIsa() {
    const urlParams = new URLSearchParams(window.location.search);
    const isaParam = urlParams.get("isa");
    const supportedIsas = ["riscv", "toy"];
    let chosenIsa = "riscv";
    if (isaParam !== null) {
        const loweredIsaParam = isaParam.toLowerCase();
        if (supportedIsas.includes(loweredIsaParam.toLowerCase())) {
            chosenIsa = isaParam.toLowerCase();
        } else {
            console.warn(
                `Specified isa '${loweredIsaParam}' is invalid. Valid options are [${supportedIsas}]. Selecting ${chosenIsa} now.`
            );
        }
    }
    return chosenIsa;
}

async function main() {
    const pyodide = await initializePyodide();
    setToyPyodide(pyodide);
    setRiscvPyodide(pyodide);
    // set the initial ISA here
    globalSettings.setSelectedIsa(getDefaultIsa());
    let app = createApp(App);
    app.mount("#app");
}

main();
