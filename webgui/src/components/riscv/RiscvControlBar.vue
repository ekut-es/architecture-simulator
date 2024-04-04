<!-- The control buttons (step, run, ...) for RISC-V -->
<script setup>
import RiscvElementToggle from "./RiscvElementToggle.vue";
import RiscvControlButtons from "./RiscvControlButtons.vue";
import RiscvVisSelect from "./RiscvVisSelect.vue";
import PerformanceMetrics from "../PerformanceMetrics.vue";
import { useRiscvSimulationStore } from "@/js/riscv_simulation_store";

const simulationStore = useRiscvSimulationStore();

let additionalMessageGetter = () => {
    let message = "";
    if (simulationStore.dataCacheStats !== null) {
        const hits = simulationStore.dataCacheStats.get("hits");
        const misses = simulationStore.dataCacheStats.get("accesses") - hits;
        message += `Data Cache Hits: ${hits}\nData Cache Misses: ${misses}`;
    }
    if (simulationStore.instructionCacheStats !== null) {
        const hits = simulationStore.instructionCacheStats.get("hits");
        const misses =
            simulationStore.instructionCacheStats.get("accesses") - hits;
        if (message !== "") {
            message += "\n";
        }
        message += `Instruction Cache Hits: ${hits}\nInstruction Cache Misses: ${misses}`;
    }
    return message;
};
</script>

<template>
    <nav id="nav-bar" class="py-1 px-2">
        <RiscvControlButtons />
        <RiscvElementToggle class="ms-3" />
        <RiscvVisSelect class="ms-auto me-3" />
        <PerformanceMetrics
            :simulation-store="simulationStore"
            :additional-message-getter
            class="performance-metrics me-3"
        />
        <button
            class="archsim-icon-button settings-button"
            title="settings"
            data-bs-toggle="modal"
            data-bs-target="#settings-modal"
        >
            <i class="bi bi-gear-fill"></i>
        </button>
    </nav>
</template>

<style scoped>
.settings-button,
.performance-metrics {
    font-size: 1.5rem;
}

#nav-bar {
    background-color: var(--bs-secondary-bg);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
</style>
