// initialize codemirror textarea
const editor = CodeMirror.fromTextArea(document.getElementById("input"), {
    lineNumbers: true,
    styleActiveLine: true,
    mode: {
        name: "gas",
        architecture: "ARM",
    },
});
editor.setSize(null, "88vh");

// initialize codemirror textarea
const editor_vis = CodeMirror.fromTextArea(
    document.getElementById("vis_input"),
    {
        lineNumbers: true,
        styleActiveLine: true,
        mode: {
            name: "gas",
            architecture: "ARM",
        },
    }
);
editor_vis.setSize(null, "57vh");

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

CodeMirror.commands.save = function () {
    saveTextAsFile();
};
