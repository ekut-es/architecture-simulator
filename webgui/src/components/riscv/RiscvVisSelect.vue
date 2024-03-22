<script setup>
import { watch } from "vue";
import { riscvSettings } from "@/js/riscv_settings";
// Select the processor view if the user disables the cache he is currently viewing.
watch(
    () => [
        riscvSettings.dataCache.value.enable,
        riscvSettings.instructionCache.value.enable,
        riscvSettings.dataCacheTooBig.value,
        riscvSettings.instructionCacheTooBig.value,
    ],
    ([
        enableDataCache,
        enableInstructionCache,
        dataCacheTooBig,
        instructionCacheTooBig,
    ]) => {
        const selected = riscvSettings.visContainerSelection.value;
        if (
            ((!enableDataCache || dataCacheTooBig) &&
                selected === "Data Cache") ||
            ((!enableInstructionCache || instructionCacheTooBig) &&
                selected === "Instruction Cache")
        ) {
            riscvSettings.visContainerSelection.value = "Processor";
        }
    }
);
</script>

<template>
    <div>
        Visualization:
        <select
            v-model="riscvSettings.visContainerSelection.value"
            aria-label="Select the element to be displayed on the right side"
        >
            <option>None</option>
            <option>Processor</option>
            <option
                v-if="
                    riscvSettings.dataCache.value.enable &&
                    !riscvSettings.dataCacheTooBig.value
                "
            >
                Data Cache
            </option>
            <option
                v-if="
                    riscvSettings.instructionCache.value.enable &&
                    !riscvSettings.instructionCacheTooBig.value
                "
            >
                Instruction Cache
            </option>
        </select>
    </div>
</template>
