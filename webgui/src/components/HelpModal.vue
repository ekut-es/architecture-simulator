<script setup>
import ToyHelp from "@/components/toy/ToyHelp.vue";
import RiscvHelp from "@/components/riscv/RiscvHelp.vue";

import { globalSettings } from "@/js/global_settings";
</script>

<template>
    <div
        class="modal fade"
        id="help-modal"
        tabindex="-1"
        aria-labelledby="help-modal-label"
        aria-hidden="true"
    >
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h1
                        class="modal-title fs-2 text-light"
                        id="help-modal-label"
                    >
                        <i
                            class="bi bi-question-circle-fill"
                            width="35px"
                            height="35px"
                        ></i>
                        <span> Help </span>
                    </h1>
                </div>
                <div id="help-modal-body" class="modal-body">
                    <!--Insert custom help pages here-->
                    <ToyHelp v-if="globalSettings.selectedIsa === 'toy'" />
                    <RiscvHelp v-if="globalSettings.selectedIsa === 'riscv'" />
                    <h1>Accessibility</h1>
                    <p>
                        To exit the editor without a mouse, you can press
                        ESC+Tab.
                    </p>
                </div>
                <div class="modal-footer">
                    <a
                        href="https://github.com/ekut-es/architecture-simulator"
                        class="me-auto link-light"
                        target="_blank"
                        rel="noreferrer noopener"
                        >GitHub</a
                    >
                    <button class="btn btn-secondary" data-bs-dismiss="modal">
                        Close
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
