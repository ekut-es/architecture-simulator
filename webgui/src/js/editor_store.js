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
import { defaultKeymap, indentWithTab } from "@codemirror/commands";
import { linter, lintGutter } from "@codemirror/lint";
import { ref, watch } from "vue";

/**
 * Associative array that holds the editor store for each ISA.
 * Use `useEditorStore` to access.
 */
const editorStores = [];

/**
 * Get the editor store for the given ISA.
 *
 * @param {BaseSimulationStore} simulationStore The simulation store the editor shall access.
 * Will only be used if no editor store was created for that ISA yet.
 * @param {String} isaName The name of the ISA.
 * @returns {EditorStore}
 */
export function useEditorStore(simulationStore, isaName) {
    if (!(isaName in editorStores)) {
        editorStores[isaName] = new EditorStore(simulationStore);
    }
    return editorStores[isaName];
}

/**
 * Holds the state of the editor, provides functions for interacting with the editor
 * and does editor related interactions with the simulation store.
 *
 * Each ISA needs their own editor store.
 */
class EditorStore {
    /**
     * @param {BaseSimulationStore} simulationStore The simulation store that this editor store
     * shall interact with.
     */
    constructor(simulationStore) {
        /**
         * The simulation store that this editor store shall interact with.
         */
        this.simulationStore = simulationStore;
        /**
         * Compartment for dynamically making the editor read only.
         */
        let readOnlyCompartment = new Compartment();
        /**
         * Compartment that is used for auto parsing.
         */
        let onViewChangeCompartment = new Compartment();
        /**
         * Compartment for the linter.
         */
        this.linterCompartment = new Compartment();
        /**
         * Whether the editor contents have changed since the last parsing.
         */
        this.hasUnparsedChanges = ref(false);
        /**
         * Timer for auto parsing.
         */
        this.timer = null;

        // Create the editor itself
        this.editorView = new EditorView({
            extensions: [
                lineNumbers(),
                highlightActiveLine(),
                readOnlyCompartment.of(EditorState.readOnly.of(false)),
                onViewChangeCompartment.of(
                    EditorView.updateListener.of((v) => {})
                ), // for auto parsing
                StreamLanguage.define(gasArm),
                syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
                EditorView.editorAttributes.of({
                    class: "archsim-default-border archsim-editor",
                }),
                keymap.of([...defaultKeymap, indentWithTab]), // new lines at end of doc don't work without this
                lintGutter(),
                this.linterCompartment.of([]),
            ],
        });

        // tell the editor to auto parse on modification
        this.editorView.dispatch({
            effects: onViewChangeCompartment.reconfigure(
                EditorView.updateListener.of((v) => {
                    if (v.docChanged) {
                        this.hasUnparsedChanges.value = true;
                        this.debounceAutoParsing();
                        this.clearLinterError(); // remove error linting immediately
                    }
                })
            ),
        });

        // make the editor read only if the simulation has started
        watch(
            () => this.simulationStore.hasStarted,
            (hasStarted) => {
                this.editorView.dispatch({
                    effects: readOnlyCompartment.reconfigure(
                        EditorState.readOnly.of(hasStarted)
                    ),
                });
            }
        );

        // Add key binding for downloading the editor content as file.
        // thanks to https://stackoverflow.com/a/60279187
        document.addEventListener("keydown", (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === "s") {
                e.preventDefault();
                this.saveTextAsFile();
            }
        });

        // create a file upload element that wont be shown because it's ugly.
        // thanks to https://www.richardkotze.com/top-tips/how-to-open-file-dialogue-just-using-javascript
        this.fileSelector = document.createElement("input");
        this.fileSelector.setAttribute("type", "file");
        this.fileSelector.onchange = this.uploadFile.bind(this);
    }

    /**
     * Replaces the existing linter in the linterCompartment with one that lints
     * the specified line (lineNumber) and displays the provided errorMessage.
     */
    showLinterError(lineNumber, errorMessage) {
        this.editorView.dispatch({
            effects: this.linterCompartment.reconfigure(
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
                    { delay: 10 } // small delay so we can disable the linter on change
                )
            ),
        });
    }

    /**
     * Replaces the existing linter in the linterCompartment with one that essentially does nothing, thereby removing linting.
     */
    clearLinterError() {
        this.editorView.dispatch({
            effects: this.linterCompartment.reconfigure(
                linter((view) => [], { delay: 0 })
            ),
        });
    }

    /**
     * Triggers auto parsing.
     * This is debounced so that calling this function multiple times will
     * delay the previous timer instead of parsing twice.
     */
    debounceAutoParsing() {
        clearTimeout(this.timer);
        this.timer = setTimeout(() => {
            this.loadProgram();
        }, 500);
    }

    /**
     * Loads the content of the editor as program of the simulation.
     * Also clears the auto parsing timer, clears the hasUnparsedChanges variable
     * and syncs the simulationStore.
     */
    loadProgram() {
        // parse
        clearTimeout(this.timer);
        const input = this.editorView.state.doc.toString();
        this.clearLinterError();
        this.simulationStore.loadProgram(input);

        // show new error
        if (
            this.simulationStore.error &&
            this.simulationStore.error[0] === "ParserException"
        ) {
            this.showLinterError(
                this.simulationStore.error[2],
                this.simulationStore.error[1]
            );
        }

        this.hasUnparsedChanges.value = false;
        this.simulationStore.syncAll();
    }

    /**
     * Downloads the content of the editor.
     */
    saveTextAsFile() {
        // thanks to https://stackoverflow.com/questions/51315044/how-do-i-save-the-content-of-the-editor-not-the-whole-html-page
        var textToWrite = this.editorView.state.doc.toString();
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
            downloadLink.href =
                window.webkitURL.createObjectURL(textFileAsBlob);
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

    /**
     * Pastes the file from the event into the editor.
     * Immediately loads the new program.
     */
    uploadFile(event) {
        // thanks to https://stackoverflow.com/a/40971885
        const file = event.target.files[0];
        const reader = new FileReader();
        reader.readAsText(file, "UTF-8");
        reader.onload = (readerEvent) => {
            const content = readerEvent.target.result;
            this.editorView.dispatch({
                changes: {
                    from: 0,
                    to: this.editorView.state.doc.length,
                    insert: content,
                },
            });
            this.loadProgram();
        };
    }

    /**
     * Opens the file explorer and lets the user upload a program.
     */
    clickFileSelector() {
        this.fileSelector.click();
    }
}
