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
