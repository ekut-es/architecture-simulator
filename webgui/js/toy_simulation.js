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
 * Inserts all of TOY's coustom elements into the DOM.
 */
function insertToyElements() {
    document
        .getElementById("codemirror-container")
        .after(getMemoryAndAccuColumn());
}

/**
 * Removes all of TOY's custom elements from the DOM.
 */
function destroyToyElements() {
    document.getElementById("toy-accu-memory-container-id").remove();
}
