import { EditorView, lineNumbers, highlightActiveLine } from "@codemirror/view";
import { EditorState, Compartment } from "@codemirror/state";

let readOnly = new Compartment();
let onViewChange = new Compartment();

export const editorView = new EditorView({
    extensions: [
        lineNumbers(),
        highlightActiveLine(),
        readOnly.of(EditorState.readOnly.of(false)),
        onViewChange.of(EditorView.updateListener.of((v) => {})),
    ],
    mode: {
        name: "gas",
        architecture: "ARM",
    },
});

document.getElementById("text-content-container").prepend(editorView.dom);
editorView.dom.id = "codemirror-input";
editorView.dom.classList.add("archsim-default-border");

export function setEditorReadOnly(setReadOnly) {
    editorView.dispatch({
        effects: readOnly.reconfigure(EditorState.readOnly.of(setReadOnly)),
    });
}

export function setEditorOnChangeListener(f) {
    editorView.dispatch({
        effects: onViewChange.reconfigure(
            EditorView.updateListener.of((v) => {
                if (v.docChanged) {
                    f();
                }
            })
        ),
    });
}

/**
 * Downloads the content of the editor.
 */
export function saveTextAsFile() {
    // thanks to https://stackoverflow.com/questions/51315044/how-do-i-save-the-content-of-the-editor-not-the-whole-html-page
    var textToWrite = editorView.state.doc.toString();
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
        editorView.dispatch({
            changes: {
                from: 0,
                to: editorView.state.doc.length,
                insert: content,
            },
        });
    };
}

// thanks to https://www.richardkotze.com/top-tips/how-to-open-file-dialogue-just-using-javascript
// create a file upload element that wont be shown because it's ugly
const fileSelector = document.createElement("input");
fileSelector.setAttribute("type", "file");
fileSelector.onchange = uploadFile;
// make the pretty button click the ugly button
document.getElementById("upload-button").onclick = () => {
    fileSelector.click();
};
