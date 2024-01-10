import { linter, lintGutter } from "@codemirror/lint";
import {
    EditorView,
    lineNumbers,
    highlightActiveLine,
    keymap,
} from "@codemirror/view";
import { EditorState, Compartment } from "@codemirror/state";
import {
    StreamLanguage,
    defaultHighlightStyle,
    syntaxHighlighting,
} from "@codemirror/language";
import { gasArm } from "@codemirror/legacy-modes/mode/gas";
import { defaultKeymap } from "@codemirror/commands";

let readOnly = new Compartment();
let onViewChange = new Compartment();
let linterCompartment = new Compartment();

export const editorView = new EditorView({
    extensions: [
        lineNumbers(),
        highlightActiveLine(),
        readOnly.of(EditorState.readOnly.of(false)),
        onViewChange.of(EditorView.updateListener.of((v) => {})), // for auto parsing
        StreamLanguage.define(gasArm),
        syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
        EditorView.editorAttributes.of({ class: "archsim-default-border" }),
        keymap.of(defaultKeymap), // new lines at end of doc don't work without this
        lintGutter(),
        linterCompartment.of([]),
    ],
});

document.getElementById("text-content-container").prepend(editorView.dom);
editorView.dom.id = "codemirror-input";

/**
 * Replaces the existing linter in the linterCompartment with one that lints the specified line (lineNumber) and displays the provided errorMessage.
 */
export function showLinterError(lineNumber, errorMessage) {
    editorView.dispatch({
        effects: linterCompartment.reconfigure(
            linter(
                (view) => {
                    const line = view.state.doc.line(lineNumber);
                    return [
                        {
                            from: line.from,
                            to: line.to,
                            severity: "warning",
                            message: errorMessage,
                        },
                    ];
                },
                { delay: 0 }
            )
        ),
    });
}

/**
 * Replaces the existing linter in the linterCompartment with one that essentially does nothing, thereby removing linting.
 */
export function clearLinterError() {
    editorView.dispatch({
        effects: linterCompartment.reconfigure(
            linter((view) => [], { delay: 0 })
        ),
    });
}

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
