/**
 * Builds a Node containnig the accu and memory table and the output field.
 * @returns {Object} An object containing the outer container, the accu and memory table and the output field.
 */
function toyGetMainColumn() {
    const column = createNode(html`<div
        id="toy-main-text-container"
        class="d-flex flex-column"
    >
        <div class="mb-3" id="toy-registers-wrapper">
            <span class="text-element-heading">Registers</span>
            <table
                class="table table-sm table-hover table-bordered mono-table mb-0"
                id="toy-register-table"
            >
                <tr>
                    <td>ACCU</td>
                    <td id="toy-accu">0</td>
                </tr>
                <tr>
                    <td>PC</td>
                    <td id="toy-pc"></td>
                </tr>
                <tr>
                    <td>IR</td>
                    <td id="toy-ir"></td>
                </tr>
            </table>
        </div>
        <div class="mb-3" id="toy-memory-wrapper">
            <span class="text-element-heading">Memory</span>
            <table
                id="toy-memory-table"
                class="table table-sm table-hover table-bordered mono-table mb-0"
            >
                <thead>
                    <tr>
                        <th>Address</th>
                        <th>Value</th>
                        <th>Instruction</th>
                    </tr>
                </thead>
                <tbody id="toy-memory-table-body"></tbody>
            </table>
        </div>
        <div id="toy-output-wrapper">
            <span class="text-element-heading">Output</span>
            <div
                class="flex-shrink-0 archsim-default-border output-field"
            ></div>
        </div>
    </div>`);
    return {
        accu: column.querySelector("#toy-accu"),
        pc: column.querySelector("#toy-pc"),
        ir: column.querySelector("#toy-ir"),
        memoryTableBody: column.querySelector("#toy-memory-table-body"),
        outputField: column.querySelector(".output-field"),
        mainColumn: column,
    };
}

/**
 * Returns a Node containing the double step button.
 * @returns {Node} A Node containing the double step button.
 */
function toyGetDoubleStepButton() {
    return createNode(html`<button
        id="button-double-step-simulation"
        class="btn btn-primary btn-sm control-button me-1"
        title="double step"
        onclick="simulation.doubleStep();"
    >
        <img src="img/double-step.svg" />
    </button>`);
}

/**
 * Generates a Node for selecting the representation (bin, udec, sdec, hex) of some setting.
 * Adds an event listener and calls the given function with the selected value (bin: "0", udec: "1", sdec: "3", hex: "2").
 * The listener will NOT cause a UI update.
 * The provided default mode will be used to check one option but it will not trigger the event listener.
 *
 * @param {string} displayName Name to display next to the buttons.
 * @param {string} id A unique id. Several ids will be generated from this base string.
 * @param {function(string):void} callback The function to call after a button was clicked.
 * @param {string} defaultMode The default representation mode.
 * @returns {Node} The Node to insert into the settings.
 */
function getRepresentationsSettingsRow(displayName, id, callback, defaultMode) {
    return getRadioSettingsRow(
        displayName,
        ["binary", "unsigned decimal", "signed decimal", "hexadecimal"],
        ["0", "1", "3", "2"],
        id,
        callback,
        defaultMode
    );
}

/**
 * Creates the Toy SVG Element. Once the svg has loaded, the given function will be called.
 *
 */
/**
 *
 * @param {function(): void} onLoad function that gets called when the svg has loaded
 * @returns {Node} The svg object node.
 */
function toyGetVisualization(onLoad) {
    const toySvgElement = document.createElement("object");
    toySvgElement.data = "img/toy_structure.svg";
    toySvgElement.type = "image/svg+xml";
    toySvgElement.id = "toy-visualization";
    toySvgElement.addEventListener("load", onLoad);
    return toySvgElement;
}
