<!-- Base component for bootstrap modals -->
<script setup>
const props = defineProps({
    baseId: String,
    iconName: String,
    title: String,
    showGithubLink: Boolean,
    modalSize: String,
});
</script>
<template>
    <div
        class="modal fade"
        :id="props.baseId"
        tabindex="-1"
        :aria-labelledby="`${props.baseId}-label`"
        aria-hidden="true"
    >
        <div :class="`modal-dialog modal-${props.modalSize}`">
            <div class="modal-content">
                <div class="modal-header">
                    <h1
                        class="modal-title fs-2 text-light"
                        :id="`${props.baseId}-label`"
                    >
                        <i :class="`bi ${props.iconName}`"></i>
                        <span class="ms-2">{{ props.title }}</span>
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
                    <slot></slot>
                </div>
                <div class="modal-footer">
                    <a
                        v-if="props.showGithubLink"
                        href="https://github.com/ekut-es/architecture-simulator"
                        class="link-light"
                        target="_blank"
                        rel="noreferrer noopener"
                        >GitHub</a
                    >
                    <button
                        class="btn btn-secondary ms-auto"
                        data-bs-dismiss="modal"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
