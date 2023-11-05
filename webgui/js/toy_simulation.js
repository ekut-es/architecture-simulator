function createNode(string) {
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = string;
    return tempDiv.firstChild;
}

function getToyMemoryTable() {
    return createNode(html`<div
        id="toy-memory-table-container-id"
        class="main-content-column"
    >
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
    </div>`);
}

function getToyAccuTable() {
    return createNode(html`<div
        id="toy-accu-table-container-id"
        class="main-content-column"
    >
        <table
            class="table table-sm table-hover table-bordered mono-table mb-0"
        >
            <thead>
                <tr>
                    <th>ACCU</th>
                    <th id="toy-accu-id">0</th>
                </tr>
            </thead>
        </table>
    </div>`);
}

function insertToyElements() {
    document
        .getElementById("codemirror-container")
        .after(getToyMemoryTable(), getToyAccuTable());
}

function destroyToyElements() {
    document.getElementById("toy-memory-table-container-id").remove();
    document.getElementById("toy-accu-table-container-id").remove();
}
