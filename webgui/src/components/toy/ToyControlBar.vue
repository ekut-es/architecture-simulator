<!-- The control bar for TOY -->
<script setup>
import ToyElementToggle from "./ToyElementToggle.vue";
import ToyControlButtons from "./ToyControlButtons.vue";
</script>

<template>
    <nav id="nav-bar" class="py-1 px-2">
        <ToyControlButtons />
        <ToyElementToggle />
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
}
</style>
