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

/**
 * Creates a node for the visualization with the given path.
 *
 * @param {string} path path to the visualization.
 * @param {function():void} onLoad Callback that will be called when the visualization has loaded.
 * @returns {Node} The object node for the svg.
 */
function createVisualization(path, onLoad) {
    const svgElement = document.createElement("object");
    svgElement.data = path;
    svgElement.type = "image/svg+xml";
    svgElement.classList.add("visualization");
    svgElement.addEventListener("load", onLoad);
    return svgElement;
}

/**
 * Creates a radio settings row and attaches a listener to it.
 * The given callback will only be called if the user selects a different item,
 * not if the same item is clicked again.
 * @param {string} displayName Name to display next to the settings row.
 * @param {array<string>} optionNames The names to display next to each option.
 * @param {array<string>} optionValues
 * @param {string} id A unique id that will be used to create several other ids.
 * @param {function(str):void} callback A function that will be called if the user selects a different option.
 * @param {string} defaultSelection The value whose button should be selected by default.
 * @returns {Node} The entire settings row.
 */
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

    let lastSelected = defaultSelection;

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
            if (lastSelected !== selected) {
                lastSelected = selected;
                callback(selected);
            }
        }
    });
    return row;
}

/**
 * Creates a SplitJS split between the given elements
 * @param {Node} container Container of the split
 * @param {Node} firstElement First element to be resizable
 * @param {Node} secondElement Second element that should be resizable
 * @returns Split object
 */
function createSplit(container, firstElement, secondElement) {
    if (window.innerWidth < window.innerHeight) {
        // Vertical split
        container.classList.add("vertical-split");
        return Split(["#" + firstElement.id, "#" + secondElement.id], {
            direction: "vertical",
            minSize: 200,
            sizes: [60, 40],
            snapOffset: 0,
        });
    } else {
        // Horizontal split
        container.classList.add("horizontal-split");
        return Split(["#" + firstElement.id, "#" + secondElement.id], {
            minSize: 200,
            sizes: [35, 65],
            snapOffset: 0,
        });
    }
}

/**
 * Check the viewport dimensions and switch between vertical and horizontal split if applicable.
 */
function handleResize() {
    var mainContentContainer = document.getElementById(
        "main-content-container"
    );
    if (
        (mainContentContainer.classList.contains("vertical-split") &&
            window.innerWidth >= window.innerHeight) ||
        (mainContentContainer.classList.contains("horizontal-split") &&
            window.innerWidth < window.innerHeight)
    ) {
        destroySplit();
        createSplit();
    }
}
