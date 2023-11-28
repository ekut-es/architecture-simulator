/**
 * @returns {Node} A Node containing the RISC-V register table.
 */
function getRiscvRegisterTable() {
    return createNode(html`<div
        id="riscv-register-table-container"
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
            <tbody id="riscv-register-table-body"></tbody>
        </table>
    </div>`);
}

/**
 * @returns {Node} A Node containing the RISC-V instruction table.
 */
function getRiscvInstructionTable() {
    return createNode(html`<div
        id="riscv-instruction-table-container"
        class="main-content-column"
    >
        <table
            id="riscv-instruction-table"
            class="table table-sm table-hover table-bordered mono-table mb-0"
        >
            <thead>
                <tr>
                    <th>Address</th>
                    <th>Command</th>
                    <th>Stage</th>
                </tr>
            </thead>
            <tbody id="riscv-instruction-table-body"></tbody>
        </table>
    </div>`);
}

/**
 * @returns {Node} A Node containing the RISC-V memory table.
 */
function getRiscvMemoryTable() {
    return createNode(html`<div
        id="riscv-memory-table-container"
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
            <tbody id="riscv-memory-table-body"></tbody>
        </table>
    </div>`);
}

/**
 * @returns {Node} A Node containing the output field.
 */
function getRiscvOutputField() {
    return createNode(html`<div
        id="riscv-output-container"
        class="main-content-column height-100 archsim-default-border"
    >
        <div id="output-field"></div>
    </div>`);
}

/**
 * Inserts all of RISC-V's custom elements into the DOM.
 */
function insertRiscvElements() {
    document
        .getElementById("text-editor-separator")
        .after(
            getRiscvInstructionTable(),
            getRiscvRegisterTable(),
            getRiscvMemoryTable(),
            getRiscvOutputField()
        );
    document.getElementById("page-heading").innerText = "RISC-V Simulator";
    document.title = "RISC-V Simulator";
}

/**
 * Removes all of RISC-V's custom elements from the DOM.
 */
function destroyRiscvElements() {
    document.getElementById("riscv-register-table-container").remove();
    document.getElementById("riscv-memory-table-container").remove();
    document.getElementById("riscv-instruction-table-container").remove();
    document.getElementById("riscv-output-container").remove();
}
