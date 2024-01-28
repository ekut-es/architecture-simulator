<script setup>
import { ref, onMounted } from "vue";

import { useEditorStore } from "@/js/editor_store";

/**
 * Pass the simulation store to use and the name of the isa for which this component is.
 * Needed for creating/using the editor store.
 */
const props = defineProps(["simulationStore", "isaName"]);

const editorStore = useEditorStore(props.simulationStore, props.isaName);

const inputWrapper = ref(null);

onMounted(() => {
    // Insert the editor into the DOM once Vue has mounted this component
    inputWrapper.value.appendChild(editorStore.editorView.dom);
});
</script>

<template>
    <div id="codemirror-wrapper" ref="inputWrapper"></div>
</template>

<style>
#codemirror-wrapper {
    flex: 1 0 5em;
    height: 100%;
}

.archsim-editor {
    height: 100%;
}
</style>
