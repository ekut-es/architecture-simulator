/**
 * @returns {Node} A Node containing the TOY accu and memory table.
 */
function getMemoryAndAccuColumn() {
    return createNode(html`<div
        id="toy-accu-memory-container-id"
        class="main-content-column"
    >
        <div>
            <table
                class="table table-sm table-hover table-bordered mono-table mb-3"
            >
                <thead>
                    <tr>
                        <th>ACCU</th>
                        <th id="toy-accu-id">0</th>
                    </tr>
                </thead>
            </table>
        </div>
        <div style="overflow: scroll;">
            <table
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
        <img src="svg/double-step.svg" />
    </button>`);
}

/**
 * Inserts all of TOY's coustom elements into the DOM.
 */
function insertToyElements() {
    document
        .getElementById("codemirror-container")
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
    document.getElementById("toy-accu-memory-container-id").remove();
    document.getElementById("button-double-step-simulation-id").remove();
}

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

function disable_double_step() {
    document.getElementById("button-double-step-simulation-id").disabled = true;
}

function enable_double_step() {
    document.getElementById(
        "button-double-step-simulation-id"
    ).disabled = false;
}

function toy_svg_highlight(id, doHighlight) {
    const color = doHighlight ? "#ff3300" : "#5f5f5f";
    const svg = document.getElementById("toy-visualization").contentDocument;
    svg.getElementById(id).setAttribute("style", "fill: " + color);
}

function toy_svg_set_text(id, text) {
    const svg = document.getElementById("toy-visualization").contentDocument;
    svg.getElementById(id).textContent = text;
}

function toy_svg_show(id, doShow) {
    const display = doShow ? "block" : "none";
    const svg = document.getElementById("toy-visualization").contentDocument;
    svg.getElementById(id).style.display = display;
}
