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
