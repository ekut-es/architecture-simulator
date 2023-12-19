import { html, createNode } from "../util";
import doubleStepIconPath from "bootstrap-icons/icons/skip-forward-fill.svg";

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
 * An event listener has to be attached manually.
 * @returns {Node} A Node containing the double step button.
 */
function toyGetDoubleStepButton() {
    return createNode(html`<button
        id="button-double-step-simulation"
        class="btn btn-primary btn-sm control-button me-1"
        title="double step"
    >
        <img src="${doubleStepIconPath}" />
    </button>`);
}

export { toyGetDoubleStepButton, toyGetMainColumn };
