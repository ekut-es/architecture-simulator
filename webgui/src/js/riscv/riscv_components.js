import { html, createNode } from "../util";

/**
 * @returns {Object} An Object containing the RISC-V register table container and tbody.
 */
function getRiscvRegisterTable() {
    const table = createNode(html`<div
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
            <tbody>
                <tr>
                    <td>zero</td>
                    <td>x0</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>ra</td>
                    <td>x1</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>sp</td>
                    <td>x2</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>gp</td>
                    <td>x3</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>tp</td>
                    <td>x4</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>t0</td>
                    <td>x5</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>t1</td>
                    <td>x6</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>t2</td>
                    <td>x7</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>s0/fp</td>
                    <td>x8</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>s1</td>
                    <td>x9</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>a0</td>
                    <td>x10</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>a1</td>
                    <td>x11</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>a2</td>
                    <td>x12</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>a3</td>
                    <td>x13</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>a4</td>
                    <td>x14</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>a5</td>
                    <td>x15</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>a6</td>
                    <td>x16</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>a7</td>
                    <td>x17</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>s2</td>
                    <td>x18</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>s3</td>
                    <td>x19</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>s4</td>
                    <td>x20</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>s5</td>
                    <td>x21</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>s6</td>
                    <td>x22</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>s7</td>
                    <td>x23</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>s8</td>
                    <td>x24</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>s9</td>
                    <td>x25</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>s10</td>
                    <td>x26</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>s11</td>
                    <td>x27</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>t3</td>
                    <td>x28</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>t4</td>
                    <td>x29</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>t5</td>
                    <td>x30</td>
                    <td>0</td>
                </tr>
                <tr>
                    <td>t6</td>
                    <td>x31</td>
                    <td>0</td>
                </tr>
            </tbody>
        </table>
    </div>`);
    return {
        registerTableContainer: table,
        registerTableBody: table.querySelector("tbody"),
    };
}

/**
 * @returns {Object} An object containing the RISC-V instruction table and table body.
 */
function getRiscvInstructionTable() {
    const table = createNode(html`<div
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
            <tbody></tbody>
        </table>
    </div>`);
    return {
        instructionTableContainer: table,
        instructionTableBody: table.querySelector("tbody"),
    };
}

/**
 * @returns {Object} An Object containing the memory table and tbody.
 */
function getRiscvMemoryTable() {
    const table = createNode(html`<div
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
            <tbody></tbody>
        </table>
    </div>`);
    return {
        memoryTableContainer: table,
        memoryTableBody: table.querySelector("tbody"),
    };
}

/**
 * @returns {Node} A Node containing the output field.
 */
function getRiscvOutputField() {
    return createNode(html`<div
        id="riscv-output-container"
        class="main-content-column height-100 archsim-default-border output-field"
    >
        <div id="output-field"></div>
    </div>`);
}

/**
 * Generates the row for enabling/disabling data hazard detection.
 * Attaches the given callback function to the state change event of the checkbox.
 *
 * @param {boolean} isEnabled Whether to check the settings by default.
 * @param {function(boolean):void} callback Function that gets called if the setting gets changed. arg0 is the state of the checkbox.
 * @returns {Node} The settings row.
 */
function getRiscvDataHazardSettings(isEnabled, callback) {
    const row = createNode(html`<div class="row">
        <div class="col-4"></div>
        <div class="col-8">
            <input
                id="button-data-hazard-detection"
                type="checkbox"
                checked=${isEnabled}
            />
            <label type="checkbox" for="button-data-hazard-detection">
                Data Hazard detection
            </label>
        </div>
    </div>`);
    row.querySelector("input").addEventListener("change", () => {
        callback(this.checked);
    });
    return row;
}

export {
    getRiscvDataHazardSettings,
    getRiscvInstructionTable,
    getRiscvMemoryTable,
    getRiscvOutputField,
    getRiscvRegisterTable,
};
