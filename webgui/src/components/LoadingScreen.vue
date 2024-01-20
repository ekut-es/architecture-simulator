<script setup>
import { globalSettings } from "../js/global_settings";
</script>

<template>
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <div>
            <h1 class="fs-2">
                {{ globalSettings.loadingStatus }}
            </h1>
        </div>
    </div>
</template>

<style scoped>
.loading-container {
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 2em;
}

.loading-spinner {
    border: 16px solid var(--main-accent-color);
    border-radius: 50%;
    border-top: 16px solid transparent;
    width: 8em;
    height: 8em;
    animation: spin 1.5s linear infinite;
    -webkit-animation: spin 1.5s linear infinite;
}

@-webkit-keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}
</style>
