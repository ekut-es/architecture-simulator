<!-- The control buttons (step, run, ...) for RISC-V -->
<script setup>
import RiscvElementToggle from './RiscvElementToggle.vue';
import RiscvControlButtons from './RiscvControlButtons.vue';
</script>

<template>
    <nav id="nav-bar" class="container-fluid py-1">
        <div class="row">
            <RiscvControlButtons class="col"/>
            <RiscvElementToggle class="col"/>
            <div class="d-flex justify-content-end col">
                <button class="btn" title="settings" data-bs-toggle="modal" data-bs-target="#settings-modal">
                    <i class="bi bi-gear-fill"></i>
                </button>
            </div>
        </div>
    </nav>
</template>

<style scoped>
button {
    font-size: 1.5rem;
    padding: 0px 6px;
}

nav {
    background-color: var(--bs-secondary-bg);
}
</style>
