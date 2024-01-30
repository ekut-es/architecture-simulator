<!-- The control bar for TOY -->
<script setup>
import ToyElementToggle from "./ToyElementToggle.vue";
import ToyControlButtons from "./ToyControlButtons.vue";
</script>

<template>
    <nav id="nav-bar" class="container-fluid py-1">
        <div class="row">
            <ToyControlButtons class="col" />
            <ToyElementToggle class="col" />
            <div class="d-flex justify-content-end col">
                <button
                    class="archsim-icon-button settings-button"
                    title="settings"
                    data-bs-toggle="modal"
                    data-bs-target="#settings-modal"
                >
                    <i class="bi bi-gear-fill"></i>
                </button>
            </div>
        </div>
    </nav>
</template>

<style scoped>
.settings-button {
    font-size: 1.5rem;
}

nav {
    background-color: var(--bs-secondary-bg);
}
</style>
