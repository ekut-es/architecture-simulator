import "./scss/styles.scss";
import "./css/main.css";
import "./css/splitjs.css";
import architectureSimulatorPackageUrl from "../../dist/architecture_simulator-1.3.1-py3-none-any.whl";

import { createApp } from "vue";

import App from "./App.vue";
import LoadingScreen from "@/components/LoadingScreen.vue";

import * as bootstrap from "bootstrap";
import { loadPyodide } from "pyodide";

import { globalSettings } from "./js/global_settings";

import { setPyodide as setRiscvPyodide } from "@/js/riscv_simulation_store";
import { setPyodide as setToyPyodide } from "@/js/toy_simulation_store";

/**
 * Loads the pyodide runtime. Installs micropip and archsim.
 * Does the necessary python imports. Returns the pyodide Interface.
 *
 * @returns {PyodideInterface} The loaded pyodide interface.
 */
async function initializePyodide() {
    const pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.22.1/full/",
    });
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install(architectureSimulatorPackageUrl);
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
    // display a loading screen
    let loadingScreen = createApp(LoadingScreen);
    loadingScreen.mount("#app");
    globalSettings.loadingStatus = "Loading pyodide...";
    try {
        // load pyodide
        const pyodide = await initializePyodide();
        // initialize stuff
        globalSettings.loadingStatus = "Initializing...";
        setToyPyodide(pyodide);
        setRiscvPyodide(pyodide);
        globalSettings.setSelectedIsa(getDefaultIsa());
        // unmount the loading screen and mount the actual app
        globalSettings.loadingStatus = "Mounting the app...";
        let app = createApp(App);
        loadingScreen.unmount();
        app.mount("#app");
    } catch (error) {
        globalSettings.loadingStatus = `An error occured during the following step: ${globalSettings.loadingStatus}`;
        throw error;
    }
}

main();
