<script setup>
import ToyHelp from "@/components/toy/ToyHelp.vue";
import RiscvHelp from "@/components/riscv/RiscvHelp.vue";
import ArchsimModal from "@/components/ArchsimModal.vue";

import { globalSettings } from "@/js/global_settings";
const modalProps = {
    baseId: "help-modal",
    iconName: "bi-question-circle-fill",
    title: "Help",
    showGithubLink: true,
    modalSize: "xl",
};
</script>

<template>
    <ArchsimModal v-bind="modalProps">
        <div id="help-modal-body" class="modal-body">
            <!--Insert custom help pages here-->
            <ToyHelp v-if="globalSettings.selectedIsa === 'toy'" />
            <RiscvHelp v-if="globalSettings.selectedIsa === 'riscv'" />
            <h1>Accessibility</h1>
            <p>To exit the editor without a mouse, you can press ESC+Tab.</p>
        </div>
    </ArchsimModal>
</template>
