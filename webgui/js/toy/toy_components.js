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
                id="output-field"
                class="flex-shrink-0 archsim-default-border"
            ></div>
        </div>
    </div>`);
    return {
        accu: column.querySelector("#toy-accu"),
        pc: column.querySelector("#toy-pc"),
        ir: column.querySelector("#toy-ir"),
        memoryTableBody: column.querySelector("#toy-memory-table-body"),
        outputField: column.querySelector("#output-field"),
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
 * Adds an event listener and calls the given function with the selected value (bin: 0, udec: 1, sdec: 3, hex: 2).
 * The listener will NOT cause a UI update.
 * The provided default mode will be used to check one option but it will not trigger the event listener.
 *
 * @param {string} displayName Name to display next to the buttons.
 * @param {string} id A unique id. Several ids will be generated from this base string.
 * @param {function(number):void} callback The function to call after a button was clicked.
 * @param {number} defaultMode The default representation mode.
 * @returns {Node} The Node to insert into the settings.
 */
function getRepresentationsSettingsRow(displayName, id, callback, defaultMode) {
    const row = createNode(html`<div class="row">
        <div class="col-4">
            <h3 class="fs-6">${displayName}:</h3>
        </div>
        <div id="${id}-container" class="col-8">
            <input
                type="radio"
                id="${id}-bin"
                name="${id}-group"
                value="0"
                ${defaultMode == 0 ? "checked" : ""}
            />
            <label for="${id}-bin"> binary </label>
            <input
                type="radio"
                id="${id}-udec"
                name="${id}-group"
                value="1"
                ${defaultMode == 1 ? "checked" : ""}
            />
            <label for="${id}-udec"> unsigned decimal </label>
            <input
                type="radio"
                id="${id}-sdec"
                name="${id}-group"
                value="3"
                ${defaultMode == 3 ? "checked" : ""}
            />
            <label for="${id}-sdec"> signed decimal </label>
            <input
                type="radio"
                id="${id}-hex"
                name="${id}-group"
                value="2"
                ${defaultMode == 2 ? "checked" : ""}
            />
            <label for="${id}-hex"> hexadecimal </label>
        </div>
    </div>`);
    row.querySelector(`#${id}-container`).addEventListener("click", (event) => {
        // make sure the user actually clicked an option, not just somewhere in the container
        if (event.target.matches("label") || event.target.matches("input")) {
            // the user might have clicked the label, but the value is only stored in the input
            let selectedMode;
            if (event.target.matches("label")) {
                const inputId = event.target.getAttribute("for");
                selectedMode = row.querySelector(`#${inputId}`).value;
            } else {
                selectedMode = event.target.value;
            }
            callback(Number(selectedMode));
        }
    });
    return row;
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

/**
 * Creates a SplitJS split between the given elements
 * @param {Node} container Container of the split
 * @param {Node} firstElement First element to be resizable
 * @param {Node} secondElement Second element that should be resizable
 * @returns Split object
 */
function createSplit(container, firstElement, secondElement) {
    container.classList.add("split");
    return Split(["#" + firstElement.id, "#" + secondElement.id], {
        minSize: 200,
        sizes: [35, 65],
        snapOffset: 0,
    });
}
