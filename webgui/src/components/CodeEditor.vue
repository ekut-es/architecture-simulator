<script setup>
import { ref, onMounted } from "vue";

import { useEditorStore } from "@/js/editor_store";

const props = defineProps(["simulationStore", "isaName"]);
const editorStore = useEditorStore(props.simulationStore, props.isaName);

const inputWrapper = ref(null);

onMounted(() => {
    inputWrapper.value.replaceWith(editorStore.editorView.dom);
});

</script>

<template>
    <div id="codemirror-input" ref="inputWrapper"></div>
</template>

<style>
#codemirror-input {
    flex: 1 0 5em;
    height: 100%;
}
</style>
