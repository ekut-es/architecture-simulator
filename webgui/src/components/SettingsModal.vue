<!-- The settings modal. ISAs need to insert their custom settings here. -->
<script setup>
import ToySettingsPage from "./toy/ToySettingsPage.vue";
import RiscvSettingsPage from "./riscv/RiscvSettingsPage.vue";
import RadioSettingsRow from "./RadioSettingsRow.vue";

import { globalSettings } from "@/js/global_settings";
import { ref, watch } from "vue";

// this ref is just required so we can pass it to the settings row
// and then change the settings in the globalSettings on mutation
const selectedIsa = ref("");
watch(selectedIsa, (selection) => {
    globalSettings.setSelectedIsa(selection);
});
</script>

<template>
    <div
        class="modal fade"
        id="settings-modal"
        tabindex="-1"
        aria-labelledby="settings-modal-label"
        aria-hidden="true"
    >
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h1
                        class="modal-title text-light fs-2"
                        id="settingsModalLabel"
                    >
                        <i class="bi bi-gear-fill"></i>
                        <span> Settings </span>
                    </h1>
                    <button
                        class="ms-auto archsim-icon-button fs-2 text-light"
                        data-bs-dismiss="modal"
                        title="exit"
                    >
                        <i class="bi bi-x-circle"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div
                        id="isa-selector-settings-container"
                        class="border-bottom mb-2"
                    >
                        <RadioSettingsRow
                            v-model="selectedIsa"
                            :default-selection="globalSettings.selectedIsa"
                            :option-names="['RISC-V', 'Toy']"
                            :option-values="['riscv', 'toy']"
                            :base-id="'isa-selector'"
                            :display-name="'ISA'"
                        >
                        </RadioSettingsRow>
                    </div>
                    <div id="isa-specific-settings-container">
                        <!--Insert custom settings pages here-->
                        <ToySettingsPage
                            v-if="globalSettings.selectedIsa === 'toy'"
                        />
                        <RiscvSettingsPage
                            v-if="globalSettings.selectedIsa === 'riscv'"
                        />
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" data-bs-dismiss="modal">
                        Close
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
