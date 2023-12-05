from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from architecture_simulator.settings.settings import Settings
from architecture_simulator.uarch.riscv.riscv_architectural_state import (
    RiscvArchitecturalState,
)
from architecture_simulator.isa.riscv.riscv_parser import RiscvParser
from .simulation import Simulation
from architecture_simulator.uarch.riscv.pipeline_registers import (
    InstructionDecodePipelineRegister,
    InstructionFetchPipelineRegister,
    ExecutePipelineRegister,
    MemoryAccessPipelineRegister,
    RegisterWritebackPipelineRegister,
    PipelineRegister,
)

if TYPE_CHECKING:
    from architecture_simulator.uarch.riscv.riscv_performance_metrics import (
        RiscvPerformanceMetrics,
    )


class RiscvSimulation(Simulation):
    """A Simulation for the RISC-V architecture.
    Currently supports single_stage_pipeline and five_stage_pipeline.

    Args:
        mode : "single_stage_pipeline" (=default) | "five_stage_pipeline"
    """

    def __init__(
        self,
        state: Optional[RiscvArchitecturalState] = None,
        mode: str = Settings().get()["default_pipeline_mode"],
        detect_data_hazards: bool = Settings().get()["hazard_detection"],
    ) -> None:
        """Constructor for RISC-V simulations.

        Args:
            state (Optional[ArchitecturalState], optional): The state to use. Creates a sensible default.
            mode (str, optional): Can be one of "single_stage_pipeline" (default) or "five_stage_pipeline".
            detect_data_hazards (bool, optional): Turn data hazard detection on or off. Defaults to True.
        """
        self.state = (
            RiscvArchitecturalState(
                pipeline_mode=mode, detect_data_hazards=detect_data_hazards
            )
            if state is None
            else state
        )
        self.mode = mode
        super().__init__()

    def step(self) -> bool:
        if not self.is_done():
            self.state.pipeline.step()
            self.has_started = True
        return not self.is_done()

    def run(self):
        self.state.performance_metrics.resume_timer()
        while not self.state.pipeline.is_done():
            self.step()
        self.state.performance_metrics.stop_timer()

    def load_program(self, program: str):
        """Loads a text form program into the simulation.

        Args:
            program (str): A program which complies with (a subset of) the RISC-V syntax.
        """
        parser = RiscvParser()
        parser.parse(program=program, state=self.state)

    def is_done(self):
        return self.state.pipeline.is_done()

    def has_instructions(self) -> bool:
        return bool(self.state.instruction_memory.instructions)

    def get_performance_metrics(self) -> RiscvPerformanceMetrics:
        return self.state.performance_metrics

    def get_instruction_memory_repr(self) -> list[tuple[str, str, str]]:
        """Returns a list of the address (in hex), instruction and stage of the instruction for all instructions in the instruction memory.

        Returns:
            list[tuple[str, str, str]]: List of (address, instruction, stage).
        """
        pipeline_stages_addresses: dict[int, str] = {}
        for pipeline_register in self.state.pipeline.pipeline_registers:
            if pipeline_register.address_of_instruction is not None:
                pipeline_stages_addresses[
                    pipeline_register.address_of_instruction
                ] = pipeline_register.abbreviation

        return [
            (
                "0x" + "{:x}".format(address),
                instruction,
                pipeline_stages_addresses[address]
                if address in pipeline_stages_addresses
                else "",
            )
            for address, instruction in self.state.instruction_memory.get_representation()
        ]

    # TODO: Replace all the code below.

    def update_IF_Stage(self):
        """
        Updates the IF Stage of the visualization and all elements withing this stage.
        To do this, the archsim.js function update_IF_Stage is called with all relevant arguments.

        Raises:
            StateNotInitializedError: Throws an error if the simulation has not yet been initialized.
        """
        IF_pipeline_register = self.state.pipeline.pipeline_registers[0]
        # parameters = vars(IF_pipeline_register)
        if isinstance(IF_pipeline_register, InstructionFetchPipelineRegister):
            parameters = {
                "mnemonic": IF_pipeline_register.instruction.mnemonic,
                "instruction": IF_pipeline_register.instruction.__repr__(),
                "address_of_instruction": IF_pipeline_register.address_of_instruction,
                "PC": self.state.program_counter,
                "pc_plus_instruction_length": IF_pipeline_register.pc_plus_instruction_length,
                "i-length": IF_pipeline_register.instruction.length,
            }
        # this case only applies if the Pipeline Register is flushed
        elif isinstance(IF_pipeline_register, PipelineRegister):
            parameters_2 = vars(IF_pipeline_register)
            parameters = dict()
            parameters["PC"] = self.state.program_counter
            parameters["mnemonic"] = parameters_2["instruction"].mnemonic
        return parameters

    def update_ID_Stage(self):
        """
        Updates the ID Stage of the visualization and all elements withing this stage.
        To do this, the archsim.js function update_ID_Stage is called with all relevant arguments.

        Raises:
            StateNotInitializedError: Throws an error if the simulation has not yet been initialized.
        """
        ID_pipeline_register = self.state.pipeline.pipeline_registers[1]
        if isinstance(ID_pipeline_register, InstructionDecodePipelineRegister):
            control_unit_signals = vars(ID_pipeline_register.control_unit_signals)
            parameters = vars(ID_pipeline_register)
            parameters["mnemonic"] = ID_pipeline_register.instruction.mnemonic
        # this case only applies if the Pipeline Register is flushed or reset
        elif isinstance(ID_pipeline_register, PipelineRegister):
            parameters = vars(ID_pipeline_register)
            control_unit_signals = dict()
            parameters["mnemonic"] = ID_pipeline_register.instruction.mnemonic
        return parameters, control_unit_signals

    def update_EX_Stage(self):
        """
        Updates the EX Stage of the visualization and all elements withing this stage.
        To do this, the archsim.js function update_EX_Stage is called with all relevant arguments.

        Raises:
        StateNotInitializedError: Throws an error if the simulation has not yet been initialized.
        """
        EX_pipeline_register = self.state.pipeline.pipeline_registers[2]
        if isinstance(EX_pipeline_register, ExecutePipelineRegister):
            control_unit_signals = vars(EX_pipeline_register.control_unit_signals)
            parameters = vars(EX_pipeline_register)
            parameters["mnemonic"] = EX_pipeline_register.instruction.mnemonic
        # this case only applies if the Pipeline Register is flushed or reset
        elif isinstance(EX_pipeline_register, PipelineRegister):
            parameters = vars(EX_pipeline_register)
            control_unit_signals = dict()
            parameters["mnemonic"] = EX_pipeline_register.instruction.mnemonic
        return parameters, control_unit_signals

    def update_MEM_Stage(self):
        """
        Updates the MEM Stage of the visualization and all elements withing this stage.
        To do this, the archsim.js function update_MEM_Stage is called with all relevant arguments.

        Raises:
        StateNotInitializedError: Throws an error if the simulation has not yet been initialized.
        """
        MEM_pipeline_register = self.state.pipeline.pipeline_registers[3]
        if isinstance(MEM_pipeline_register, MemoryAccessPipelineRegister):
            control_unit_signals = vars(MEM_pipeline_register.control_unit_signals)
            parameters = vars(MEM_pipeline_register)
            parameters["mnemonic"] = MEM_pipeline_register.instruction.mnemonic

        # this case only applies if the Pipeline Register is flushed or reset
        elif isinstance(MEM_pipeline_register, PipelineRegister):
            parameters = vars(MEM_pipeline_register)
            control_unit_signals = dict()
            parameters["mnemonic"] = MEM_pipeline_register.instruction.mnemonic
        return parameters, control_unit_signals

    def update_WB_Stage(self):
        """Update WB Stage:
        Updates the WB Stage of the visualization and all elements withing this stage.
        To do this, the archsim.js function update_WB_Stage is called with all relevant arguments.

        Raises:
        StateNotInitializedError: Throws an error if the simulation has not yet been initialized.
        """
        WB_pipeline_register = self.state.pipeline.pipeline_registers[4]
        if isinstance(WB_pipeline_register, RegisterWritebackPipelineRegister):
            control_unit_signals = vars(WB_pipeline_register.control_unit_signals)
            parameters = vars(WB_pipeline_register)
            parameters["mnemonic"] = WB_pipeline_register.instruction.mnemonic

        # this case only applies if the Pipeline Register is flushed or reset
        elif isinstance(WB_pipeline_register, PipelineRegister):
            parameters = vars(WB_pipeline_register)
            control_unit_signals = dict()
            parameters["mnemonic"] = WB_pipeline_register.instruction.mnemonic
        return parameters, control_unit_signals

    def get_other_visualization_updates(self):
        """
        Updates visualization elements that need information from more than one stage.

        Raises:
        StateNotInitializedError: Throws an error if the simulation has not yet been initialized.
        """
        if len(self.state.pipeline.pipeline_registers) > 1:
            IF_pipeline_register = self.state.pipeline.pipeline_registers[0]
            MEM_pipeline_register = self.state.pipeline.pipeline_registers[3]
            if isinstance(
                IF_pipeline_register, InstructionFetchPipelineRegister
            ) and isinstance(MEM_pipeline_register, MemoryAccessPipelineRegister):
                pc_plus_imm_or_pc_plus_instruction_length = (
                    MEM_pipeline_register.pc_plus_imm
                    if MEM_pipeline_register.comparison_or_jump
                    else IF_pipeline_register.pc_plus_instruction_length
                )
            elif isinstance(IF_pipeline_register, PipelineRegister) and isinstance(
                MEM_pipeline_register, MemoryAccessPipelineRegister
            ):
                pc_plus_imm_or_pc_plus_instruction_length = (
                    MEM_pipeline_register.pc_plus_imm
                    if MEM_pipeline_register.comparison_or_jump
                    else None
                )
            else:
                pc_plus_imm_or_pc_plus_instruction_length = None
            if pc_plus_imm_or_pc_plus_instruction_length is not None and isinstance(
                MEM_pipeline_register, MemoryAccessPipelineRegister
            ):
                pc_plus_imm_or_pc_plus_instruction_length_or_ALU_result = (
                    MEM_pipeline_register.result
                    if MEM_pipeline_register.control_unit_signals.alu_to_pc
                    else pc_plus_imm_or_pc_plus_instruction_length
                )
            elif isinstance(MEM_pipeline_register, MemoryAccessPipelineRegister):
                pc_plus_imm_or_pc_plus_instruction_length_or_ALU_result = (
                    MEM_pipeline_register.result
                    if MEM_pipeline_register.control_unit_signals.alu_to_pc
                    else None
                )

            else:
                pc_plus_imm_or_pc_plus_instruction_length_or_ALU_result = None

            return (
                pc_plus_imm_or_pc_plus_instruction_length,
                pc_plus_imm_or_pc_plus_instruction_length_or_ALU_result,
            )
