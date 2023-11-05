function getRiscvRegisterTable() {
    return createNode(html`<div
        id="riscv-register-table-container-id"
        class="main-content-column"
    >
        <table
            class="table table-sm table-hover table-bordered mono-table mb-0"
        >
            <thead>
                <tr>
                    <th colspan="2">Register</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody id="riscv-register-table-body-id"></tbody>
        </table>
    </div>`);
}

function getRiscvInstructionTable() {
    return createNode(html`<div
        id="riscv-instruction-table-container-id"
        class="main-content-column"
    >
        <table
            id="riscv-instruction-table-id"
            class="table table-sm table-hover table-bordered mono-table mb-0"
        >
            <thead>
                <tr>
                    <th>Address</th>
                    <th>Command</th>
                    <th>Stage</th>
                </tr>
            </thead>
            <tbody id="riscv-instruction-table-body-id"></tbody>
        </table>
    </div>`);
}

function getRiscvMemoryTable() {
    return createNode(html`<div
        id="riscv-memory-table-container-id"
        class="main-content-column"
    >
        <table
            class="table table-sm table-hover table-bordered mono-table mb-0"
        >
            <thead>
                <tr>
                    <th>Address</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody id="riscv-memory-table-body-id"></tbody>
        </table>
    </div>`);
}

function insertRiscvElements() {
    document
        .getElementById("codemirror-container")
        .after(
            getRiscvInstructionTable(),
            getRiscvRegisterTable(),
            getRiscvMemoryTable()
        );
}

function destroyRiscvElements() {
    document.getElementById("riscv-register-table-container-id").remove();
    document.getElementById("riscv-memory-table-container-id").remove();
    document.getElementById("riscv-instruction-table-container-id").remove();
}
