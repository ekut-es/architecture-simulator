import { ref } from "vue";

export const riscvSettings = {
    registerRepresentation: ref("3"),
    memoryRepresentation: ref("3"),
    pipelineMode: ref("single_stage_pipeline"),
    dataHazardDetection: ref(true),
};
