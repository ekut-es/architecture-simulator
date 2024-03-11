import { ref } from "vue";

/**
 * RISC-V specific settings.
 */
export const riscvSettings = {
    registerRepresentation: ref("3"),
    memoryRepresentation: ref("3"),
    pipelineMode: ref("single_stage_pipeline"),
    dataHazardDetection: ref(true),
    showInput: ref(true),
    showMemory: ref(true),
    showRegistersOutput: ref(true),
    dataCache: ref({
        enable: false,
        num_index_bits: 2,
        num_block_bits: 0,
        associativity: 4,
        miss_penalty: 0,
        replacement_strategy: "lru",
        cache_type: "wt",
    }),
    instructionCache: ref({
        enable: false,
        num_index_bits: 2,
        num_block_bits: 0,
        associativity: 4,
        miss_penalty: 0,
        replacement_strategy: "lru",
        cache_type: "wb",
    }),
    visContainerSelection: ref("Processor"),
};
