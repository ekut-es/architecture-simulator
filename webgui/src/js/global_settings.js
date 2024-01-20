import { reactive } from "vue";

export let globalSettings = reactive({
    selectedIsa: "",
    selectedIsaName: "",
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
});
