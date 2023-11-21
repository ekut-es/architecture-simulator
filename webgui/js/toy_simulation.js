/**
 * @returns {Node} A Node containing the TOY accu and memory table.
 */
function getMemoryAndAccuColumn() {
    return createNode(html`<div
        id="toy-main-text-container-id"
        class="d-flex flex-column"
    >
        <div class="mb-3" id="toy-registers-wrapper">
            <table
                class="table table-sm table-hover table-bordered mono-table mb-0"
                id="toy-register-table"
            >
                <colgroup>
                    <col />
                    <col id="toy-registers-second-column" />
                    <col />
                </colgroup>
                <tr>
                    <td>ACCU</td>
                    <td colspan="2" id="toy-accu-id">0</td>
                </tr>
                <tr>
                    <td>PC</td>
                    <td colspan="2" id="toy-pc-id"></td>
                </tr>
                <tr>
                    <td>IR</td>
                    <td id="toy-ir-instruction-id"></td>
                    <td id="toy-ir-value-id"></td>
                </tr>
            </table>
        </div>
        <div class="mb-3" id="toy-memory-wrapper">
            <table
                id="toy-memory-table-id"
                class="table table-sm table-hover table-bordered mono-table mb-0"
            >
                <thead>
                    <tr>
                        <th>Address</th>
                        <th>Value</th>
                        <th>Instruction</th>
                    </tr>
                </thead>
                <tbody id="toy-memory-table-body-id"></tbody>
            </table>
        </div>
        <div id="toy-output-wrapper">
            <div
                id="output-field-id"
                class="flex-shrink-0 archsim-default-border"
            ></div>
        </div>
    </div>`);
}

/**
 * @returns {Node} A Node containing the double step button.
 */
function getDoubleStepButton() {
    return createNode(html`<button
        id="button-double-step-simulation-id"
        class="btn btn-primary btn-sm control-button me-1"
        title="double step"
    >
        <img src="img/double-step.svg" />
    </button>`);
}

/**
 * Inserts all of TOY's coustom elements into the DOM.
 */
function insertToyElements() {
    document
        .getElementById("text-editor-separator")
        .after(getMemoryAndAccuColumn());
    const doubleStepButton = getDoubleStepButton();
    document
        .getElementById("button-step-simulation-id")
        .after(doubleStepButton);
    doubleStepButton.addEventListener("click", doubleStep);
    document.getElementById("page-heading-id").innerText = "TOY Simulator";
    document.title = "TOY Simulator";
}

/**
 * Removes all of TOY's custom elements from the DOM.
 */
function destroyToyElements() {
    document.getElementById("toy-main-text-container-id").remove();
    document.getElementById("button-double-step-simulation-id").remove();
}

/**
 * Executes the first cycle step and the second cycle step.
 */
function doubleStep() {
    is_run_simulation = false;
    manual_run = true;
    editor.save();
    disable_editor();
    evaluatePython_step_sim();
    enable_run();
    disable_pause();
    enable_step();
}

/**
 * Disables the double step button.
 */
function disable_double_step() {
    document.getElementById("button-double-step-simulation-id").disabled = true;
}

/**
 * Enables the double step button.
 */
function enable_double_step() {
    document.getElementById(
        "button-double-step-simulation-id"
    ).disabled = false;
}

/**
 * Sets the fill color of an element.
 * @param {string} id target id.
 * @param {string} color hex color string.
 */
function toySvgHighlight(id, color) {
    const svg = document.getElementById("toy-visualization").contentDocument;
    svg.getElementById(id).setAttribute("style", "fill: " + color);
}

/**
 * Sets the text content of an element.
 * @param {string} id target id.
 * @param {string} text text to set as the content of the element.
 */
function toySvgSetText(id, text) {
    const svg = document.getElementById("toy-visualization").contentDocument;
    svg.getElementById(id).textContent = text;
}

/**
 * Shows or hides an element.
 * @param {string} id target id.
 * @param {boolean} doShow Whether to show the element (display: block). Else it will be hidden (display: none)
 */
function toySvgShow(id, doShow) {
    const display = doShow ? "block" : "none";
    const svg = document.getElementById("toy-visualization").contentDocument;
    svg.getElementById(id).style.display = display;
}
