<!-- The memory table for data and instructions -->
<script setup>
import { watchEffect, watch, ref } from "vue";

import CurrentInstructionArrow from "../CurrentInstructionArrow.vue";

import { toySettings } from "@/js/toy_settings";
import { useToySimulationStore } from "@/js/toy_simulation_store";

const table = ref(null);

const simulationStore = useToySimulationStore();

// An array that we can nicely iteratve over in the template
const tableValues = ref(null);
// The row index of the current instruction
const currentInstructionRow = ref(0);
// Keep the table values and current instruction row index updated
watchEffect(() => {
    let result = [];
    // In case of a reset or when the user enters new instructions, the memory values change
    // but we don't want to scroll
    if (!simulationStore.hasStarted) {
        currentInstructionRow.value = -1;
    }

    for (const [index, entry] of simulationStore.memoryEntries.entries()) {
        const row = {
            hexAddress: entry[0][1],
            value: entry[1][toySettings.memoryRepresentation.value],
            instruction: entry[2],
            cycle: entry[3],
            doHighlight: simulationStore.hasStarted && entry[4],
        };
        // update the current instruction row if a current instruction can be found
        // else just keep the old row
        if (row.cycle !== "") {
            currentInstructionRow.value = index + 1; // +1 because of the head row
        }
        result.push(row);
    }
    tableValues.value = result;
});

// auto scroll to the current instruction
watch(
    [currentInstructionRow, toySettings.followCurrentInstruction],
    ([rowIndex, doFollow]) => {
        if (!doFollow || rowIndex < 0) {
            return;
        }
        const rows = table.value.rows;
        if (rows.length > rowIndex) {
            const scrollAmount =
                rows[rowIndex].offsetTop +
                rows[rowIndex].offsetHeight / 2 -
                table.value.parentNode.offsetHeight / 2;
            table.value.parentNode.scroll({
                // scrollIntoView also scrolls horizontally, so I dont use it here
                top: scrollAmount,
                left: 0,
                behavior: "smooth",
            });
        }
    }
);
</script>

<template>
    <div class="wrapper">
        <div class="header">
            <span class="archsim-text-element-heading">Memory</span>
            <label class="ms-auto" for="toy-follow-current-instruction">
                <input
                    ref="followCheckbox"
                    type="checkbox"
                    id="toy-follow-current-instruction"
                    v-model="toySettings.followCurrentInstruction.value"
                    :checked="toySettings.followCurrentInstruction.value"
                />
                Follow
            </label>
        </div>
        <div class="table-wrapper">
            <table
                ref="table"
                class="table table-sm table-hover table-bordered archsim-mono-table mb-0"
            >
                <thead>
                    <tr>
                        <th style="min-width: 7em">Address</th>
                        <th>Value</th>
                        <th>Instruction</th>
                    </tr>
                </thead>
                <tbody id="toy-memory-table-body">
                    <tr v-for="entry in tableValues">
                        <td>
                            <CurrentInstructionArrow v-if="entry.cycle">
                                {{ entry.cycle }}
                            </CurrentInstructionArrow>
                            {{ entry.hexAddress }}
                        </td>
                        <td :class="{ highlight: entry.doHighlight }">
                            {{ entry.value }}
                        </td>
                        <td>{{ entry.instruction }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<style scoped>
.wrapper {
    display: flex;
    flex-direction: column;
}

.table-wrapper {
    overflow-y: auto;
}

.highlight {
    background-color: var(--highlight-color) !important;
}

#toy-memory-table-body > tr > td:nth-child(1),
#toy-memory-table-body > tr > td:nth-child(2) {
    text-align: right;
}

.header {
    display: flex;
    align-items: end;
}
</style>
