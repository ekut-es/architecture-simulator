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

const instructionArrow = html`<svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    fill="currentColor"
    class="bi bi-caret-right-fill"
    viewBox="0 0 16 16"
>
    <path
        d="m12.14 8.753-5.482 4.796c-.646.566-1.658.106-1.658-.753V3.204a1 1 0 0 1 1.659-.753l5.48 4.796a1 1 0 0 1 0 1.506z"
    />
</svg>`;

function createVisualization(path, onLoad) {
    const svgElement = document.createElement("object");
    svgElement.data = path;
    svgElement.type = "image/svg+xml";
    svgElement.classList.add("visualization");
    svgElement.addEventListener("load", onLoad);
    return svgElement;
}

function getRadioSettingsRow(
    displayName,
    optionNames,
    optionValues,
    id,
    callback,
    defaultSelection
) {
    let optionsString = "";
    for (let i = 0; i < optionNames.length; i++) {
        let name = optionNames[i];
        let value = optionValues[i];
        optionsString += html`<input
                type="radio"
                id="${id}-${value}"
                name="${id}-group"
                value="${value}"
                ${defaultSelection === value ? "checked" : ""}
            />
            <label for="${id}-${value}" class="pe-2"> ${name} </label>`;
    }
    const row = createNode(html`<div class="row">
        <div class="col-4">
            <h3 class="fs-6">${displayName}:</h3>
        </div>
        <div id="${id}-container" class="col-8">${optionsString}</div>
    </div>`);
    row.querySelector(`#${id}-container`).addEventListener("click", (event) => {
        // make sure the user actually clicked an option, not just somewhere in the container
        if (event.target.matches("label") || event.target.matches("input")) {
            // the user might have clicked the label, but the value is only stored in the input
            let selected;
            if (event.target.matches("label")) {
                const inputId = event.target.getAttribute("for");
                selected = row.querySelector(`#${inputId}`).value;
            } else {
                selected = event.target.value;
            }
            callback(selected);
        }
    });
    return row;
}
