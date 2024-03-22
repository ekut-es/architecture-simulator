<!-- The control buttons (step, run, ...) for RISC-V -->
<script setup>
import RiscvElementToggle from "./RiscvElementToggle.vue";
import RiscvControlButtons from "./RiscvControlButtons.vue";
import RiscvVisSelect from "./RiscvVisSelect.vue";
</script>

<template>
    <nav id="nav-bar" class="py-1 px-2">
        <RiscvControlButtons />
        <RiscvElementToggle class="ms-3" />
        <RiscvVisSelect class="ms-auto me-3" />
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
.settings-button {
    font-size: 1.5rem;
}

#nav-bar {
    background-color: var(--bs-secondary-bg);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
</style>
