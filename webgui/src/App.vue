<!-- The Main App component -->
<script setup>
import PageHeader from "@/components/PageHeader.vue";
import HelpModal from "./components/HelpModal.vue";
import SettingsModal from "./components/SettingsModal.vue";
import ToyMain from "./components/toy/ToyMain.vue";
import RiscvMain from "./components/riscv/RiscvMain.vue";

import { globalSettings } from "./js/global_settings";
</script>

<template>
    <PageHeader />
    <ToyMain v-if="globalSettings.selectedIsa === 'toy'" />
    <RiscvMain v-if="globalSettings.selectedIsa === 'riscv'" />
    <HelpModal />
    <SettingsModal />
</template>

<style scoped></style>
