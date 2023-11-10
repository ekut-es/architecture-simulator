/**
 * Turns an HTML string into a Node.
 * @param {string} string A valid HTML string.
 * @returns {Node} The corresponding Node object.
 */
function createNode(string) {
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = string;
    return tempDiv.firstChild;
}

// used for template strings so that the extension knows it's a html string. This function itself doesn't do anything except string interpolation I think.
const html = (strings, ...values) => String.raw({ raw: strings }, ...values);

const instructionArrow = html`<span title="current instruction"
    ><svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        fill="currentColor"
        class="bi bi-arrow-right"
        viewBox="0 0 16 16"
    >
        <path
            fill-rule="evenodd"
            d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z"
        />
    </svg>
</span>`;
