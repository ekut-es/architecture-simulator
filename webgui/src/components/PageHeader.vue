<script setup>
import { globalSettings } from "@/js/global_settings";
</script>

<template>
    <header id="header" class="archsim-main-bg px-2">
        <div id="page-heading" class="h1 mb-0 col-auto">
            {{ globalSettings.selectedIsaName }} Simulator
        </div>
        <div class="col-auto ms-auto">
            <button
                id="help-button"
                class="archsim-icon-button"
                title="help"
                data-bs-toggle="modal"
                data-bs-target="#help-modal"
            >
                <i class="bi bi-question-circle-fill"></i>
            </button>
        </div>
    </header>
</template>

<style scoped>
#header {
    background-color: var(--main-accent-color);
    color: white;
    display: flex;
    justify-content: space-between;
}

#help-button {
    color: white;
    font-size: 2rem;
}
</style>
