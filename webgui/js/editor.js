// initialize codemirror textarea
const editor = CodeMirror.fromTextArea(document.getElementById("input"), {
    lineNumbers: true,
    styleActiveLine: true,
    mode: {
        name: "gas",
        architecture: "ARM",
    },
});
editor.getWrapperElement().id = "codemirror-id";
editor.getWrapperElement().classList.add("archsim-default-border");

/**
 * Downloads the content of the editor.
 */
function saveTextAsFile() {
    // thanks to https://stackoverflow.com/questions/51315044/how-do-i-save-the-content-of-the-editor-not-the-whole-html-page
    var textToWrite = editor.getValue();
    var textFileAsBlob = new Blob([textToWrite], {
        type: "text/plain;charset=utf-8",
    });
    var fileNameToSaveAs = "my_program.asm";

    var downloadLink = document.createElement("a");
    downloadLink.download = fileNameToSaveAs;
    downloadLink.innerHTML = "Download File";
    if (window.webkitURL != null) {
        // Chrome allows the link to be clicked
        // without actually adding it to the DOM.
        downloadLink.href = window.webkitURL.createObjectURL(textFileAsBlob);
    } else {
        // Firefox requires the link to be added to the DOM
        // before it can be clicked.
        downloadLink.href = window.URL.createObjectURL(textFileAsBlob);
        downloadLink.onclick = destroyClickedElement;
        downloadLink.style.display = "none";
        document.body.appendChild(downloadLink);
    }

    downloadLink.click();
}

// thanks to https://stackoverflow.com/a/60279187
document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        saveTextAsFile();
    }
});

/**
 * Pastes the file from the event into the editor.
 */
function uploadFile(event) {
    // thanks to https://stackoverflow.com/a/40971885
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.readAsText(file, "UTF-8");
    reader.onload = (readerEvent) => {
        const content = readerEvent.target.result;
        editor.setValue(content);
    };
}

// thanks to https://www.richardkotze.com/top-tips/how-to-open-file-dialogue-just-using-javascript
// create a file upload element that wont be shown because it's ugly
const fileSelector = document.createElement("input");
fileSelector.setAttribute("type", "file");
fileSelector.onchange = uploadFile;
// make the pretty button click the ugly button
document.getElementById("upload-button-id").onclick = () => {
    fileSelector.click();
};
