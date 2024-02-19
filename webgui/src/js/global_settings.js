import { reactive } from "vue";

/**
 * Holds settings (and status variables) needed for the simulation/the app,
 * not for an individual ISA.
 */
export let globalSettings = reactive({
    /**
     * The selected isa, without whitespaces or special characters ('riscv' or 'toy' at the moment).
     */
    selectedIsa: "",
    /**
     * A display name for the current ISA ('RISC-V' or 'TOY' at the moment).
     */
    selectedIsaName: "",
    /**
     * Set the new, currently selected isa.
     * Also updates the display name (`this.selectedIsaName`).
     * @param {String} name Name of the isa ('riscv' or 'toy').
     */
    setSelectedIsa(name) {
        switch (name) {
            case "riscv":
                this.selectedIsa = "riscv";
                this.selectedIsaName = "RISC-V";
                break;
            case "toy":
                this.selectedIsa = "toy";
                this.selectedIsaName = "TOY";
                break;
            default:
                throw Error(`ISA ${name} does not exist`);
        }
    },
    /**
     * The loading status of the app. Will be displayed on the loading screen.
     */
    loadingStatus: "",
});
