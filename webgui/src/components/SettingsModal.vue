<!-- The settings modal. ISAs need to insert their custom settings here. -->
<script setup>
import ToySettingsPage from "./toy/ToySettingsPage.vue";
import RiscvSettingsPage from "./riscv/RiscvSettingsPage.vue";
import RadioSettingsRow from "./RadioSettingsRow.vue";
import ArchsimModal from "./ArchsimModal.vue";

import { globalSettings } from "@/js/global_settings";
import { ref, watch } from "vue";

// this ref is just required so we can pass it to the settings row
// and then change the settings in the globalSettings on mutation
const selectedIsa = ref("");
watch(selectedIsa, (selection) => {
    globalSettings.setSelectedIsa(selection);
});
const modalProps = {
    baseId: "settings-modal",
    iconName: "bi-gear-fill",
    title: "Settings",
    showGithubLink: false,
    modalSize: "lg",
};
</script>

<template>
    <ArchsimModal v-bind="modalProps">
        <div id="isa-selector-settings-container" class="border-bottom mb-2">
            <RadioSettingsRow
                v-model="selectedIsa"
                :default-selection="globalSettings.selectedIsa"
                :option-names="['RISC-V', 'Toy']"
                :option-values="['riscv', 'toy']"
                :base-id="'isa-selector'"
                :display-name="'ISA'"
            />
        </div>
        <div id="isa-specific-settings-container">
            <!--Insert custom settings pages here-->
            <ToySettingsPage v-if="globalSettings.selectedIsa === 'toy'" />
            <RiscvSettingsPage v-if="globalSettings.selectedIsa === 'riscv'" />
        </div>
    </ArchsimModal>
</template>
