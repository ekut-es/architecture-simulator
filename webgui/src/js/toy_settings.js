import { ref } from "vue";

/**
 * TOY specific settings.
 */
export const toySettings = {
    registerRepresentation: ref("1"),
    memoryRepresentation: ref("1"),
    showInput: ref(true),
    showMemory: ref(true),
    showRegistersOutput: ref(true),
    showVisualization: ref(true),
    followCurrentInstruction: ref(true),
};
