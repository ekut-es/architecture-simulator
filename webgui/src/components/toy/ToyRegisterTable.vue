<!-- The register table for TOY -->
<script setup>
import { useToySimulationStore } from "@/js/toy_simulation_store";
import { toySettings } from "@/js/toy_settings";

const simulationStore = useToySimulationStore();
</script>

<template>
    <div class="mb-3" id="toy-registers-wrapper">
        <span class="archsim-text-element-heading">Registers</span>
        <table
            class="table table-sm table-hover table-bordered archsim-mono-table mb-0"
            id="toy-register-table"
        >
            <tbody>
                <tr>
                    <td>ACCU</td>
                    <td>
                        {{
                            simulationStore.registerTableEntries.get("accu")[
                                toySettings.registerRepresentation.value
                            ]
                        }}
                    </td>
                </tr>
                <tr>
                    <td>PC</td>
                    <td>
                        {{
                            simulationStore.registerTableEntries.get("pc")[
                                toySettings.registerRepresentation.value
                            ]
                        }}
                    </td>
                </tr>
                <tr>
                    <td>IR</td>
                    <td>
                        {{
                            simulationStore.registerTableEntries.get("ir")[
                                toySettings.registerRepresentation.value
                            ]
                        }}
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<style scoped>
#toy-register-table td:first-child {
    font-weight: bold;
}

#toy-register-table td:last-child {
    text-align: right;
    width: 100%;
}

#toy-registers-wrapper {
    flex: 0 0 auto;
}
</style>
