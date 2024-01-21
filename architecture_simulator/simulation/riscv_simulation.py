from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Any

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
    SingleStagePipelineRegister,
)

if TYPE_CHECKING:
    from architecture_simulator.uarch.riscv.riscv_performance_metrics import (
        RiscvPerformanceMetrics,
    )
from architecture_simulator.gui.riscv_fiveStage_svg_directives import (
    RiscvFiveStageIFSvgDirectives,
    RiscvFiveStageIDSvgDirectives,
    RiscvFiveStageEXSvgDirectives,
    RiscvFiveStageMEMSvgDirectives,
    RiscvFiveStageWBSvgDirectives,
    RiscvFiveStageOTHERSvgDirectives,
)

from architecture_simulator.gui.riscv_single_stage_svg_directives import (
    RiscvSingleStageSvgDirectives,
)


def save_to_str(input: Any) -> str:
    return str(input) if input is not None else ""


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
            self.state.previous_program_counter = (
                self.state.program_counter
            )  # maybe this should not go here
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
        Resets the state before loading the new program.

        Args:
            program (str): A program which complies with (a subset of) the RISC-V syntax.
        """
        self.state.memory.reset()
        self.state.instruction_memory.reset()
        parser = RiscvParser()
        parser.parse(program=program, state=self.state)

    def is_done(self):
        return self.state.pipeline.is_done()

    def has_instructions(self) -> bool:
        return bool(self.state.instruction_memory.instructions)

    def get_performance_metrics(self) -> RiscvPerformanceMetrics:
        return self.state.performance_metrics

    def get_register_entries(self) -> list[tuple[str, str, str, str]]:
        """Returns the contents of the register file as bin, udec, hex, sdec values.

        Returns:
            list[tuple[str, str, str, str]]: Register values as tuples of (bin, udec, hex, sdec)
        """
        return self.state.register_file.reg_repr()

    def get_instruction_memory_entries(self) -> list[tuple[str, str, str]]:
        """Returns a list of the address (in hex), instruction and pipeline stage of the instruction for all instructions in the instruction memory.

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
                "0x" + "{:03X}".format(address),
                instruction,
                pipeline_stages_addresses[address]
                if address in pipeline_stages_addresses
                else "",
            )
            for address, instruction in self.state.instruction_memory.get_representation()
        ]

    def get_data_memory_entries(
        self,
    ) -> list[tuple[tuple[int, str], tuple[str, str, str, str]]]:
        memory_repr = self.state.memory.wordwise_repr()
        result = []
        for key, values in sorted(memory_repr.items()):
            result.append(((key, "0x" + "{:08X}".format(key)), values))
        return result

    def get_riscv_five_stage_svg_update_values(self) -> list[tuple[str, str, Any]]:
        """Returns all information needed to update the svg.

        Returns:
            list[tuple[str, str, Any]]: each tuple is [svg-id, what update function to use, argument for update function (Any)].
            They can be one of ("<id>","highlight", <#hexcolor>), ("<id>", "write-center", <content>), ("<id>", "write-left", <content>), ("<id>", "write-right", <content>)
        """
        assert self.mode == "five_stage_pipeline"
        return (
            self._get_riscv_five_stage_IF_svg_update_values()
            + self._get_riscv_five_stage_ID_svg_update_values()
            + self._get_riscv_five_stage_EX_svg_update_values()
            + self._get_riscv_five_stage_MEM_svg_update_values()
            + self._get_riscv_five_stage_WB_svg_update_values()
            + self._get_riscv_five_stage_OTHER_svg_update_values()
        )

    def _get_riscv_five_stage_IF_svg_update_values(self) -> list[tuple[str, str, Any]]:
        """Returns all information needed to update IF stage part of svg."""
        result = RiscvFiveStageIFSvgDirectives()
        pipeline_register = self.state.pipeline.pipeline_registers[0]

        result.Fetch.text = pipeline_register.instruction.mnemonic
        result.PC.text = self.state.previous_program_counter

        if isinstance(pipeline_register, InstructionFetchPipelineRegister):
            result.InstructionMemoryInstrText.text = (
                pipeline_register.instruction.__repr__()
            )
            result.InstructionMemory.do_highlight = bool(
                result.InstructionMemoryInstrText.text
            )

            result.InstructionReadAddressText.text = save_to_str(
                pipeline_register.address_of_instruction
            )
            result.FetchPCOut.do_highlight = bool(
                result.InstructionReadAddressText.text
            )

            result.FetchAddOutText.text = save_to_str(
                pipeline_register.pc_plus_instruction_length
            )
            result.FetchAddOut.do_highlight = bool(result.FetchAddOutText.text)

            result.I_LengthText.text = save_to_str(pipeline_register.instruction.length)
            result.FetchI_Length.do_highlight = bool(result.I_LengthText.text)

        return result.export()

    def _get_riscv_five_stage_ID_svg_update_values(self) -> list[tuple[str, str, Any]]:
        """Returns all information needed to update ID stage part of svg."""
        result = RiscvFiveStageIDSvgDirectives()
        pipeline_register = self.state.pipeline.pipeline_registers[1]

        result.Decode.text = pipeline_register.instruction.mnemonic

        if isinstance(pipeline_register, InstructionDecodePipelineRegister):
            result.RegisterFileReadAddress1Text.text = save_to_str(
                pipeline_register.register_read_addr_1
            )
            result.DecodeInstructionMemory1.do_highlight = bool(
                result.RegisterFileReadAddress1Text.text
            )

            result.RegisterFileReadAddress2Text.text = save_to_str(
                pipeline_register.register_read_addr_2
            )
            result.DecodeInstructionMemory2.do_highlight = bool(
                result.RegisterFileReadAddress2Text.text
            )

            result.RegisterFileReadData1Text.text = save_to_str(
                pipeline_register.register_read_data_1
            )
            result.RegisterFileReadData1.do_highlight = bool(
                result.RegisterFileReadData1Text.text
            )

            result.RegisterFileReadData2Text.text = save_to_str(
                pipeline_register.register_read_data_2
            )
            result.RegisterFileReadData2.do_highlight = bool(
                result.RegisterFileReadData2Text.text
            )

            result.ImmGenText.text = save_to_str(pipeline_register.imm)
            result.ImmGenOut.do_highlight = bool(result.ImmGenText.text)
            result.DecodeInstructionMemory3.do_highlight = bool(result.ImmGenText.text)

            result.DecodeInstructionMemory4Text.text = save_to_str(
                pipeline_register.write_register
            )
            result.DecodeInstructionMemory4.do_highlight = bool(
                result.DecodeInstructionMemory4Text.text
            )

            result.DecodeFetchAddOutText.text = save_to_str(
                pipeline_register.pc_plus_instruction_length
            )
            result.DecodeFetchAddOut.do_highlight = bool(
                result.DecodeFetchAddOutText.text
            )

            result.DecodeUpperFetchPCOutText.text = save_to_str(
                pipeline_register.address_of_instruction
            )
            result.DecodeLowerFetchPCOutText.text = save_to_str(
                pipeline_register.address_of_instruction
            )

            result.DecodeUpperFetchPCOut.do_highlight = bool(
                result.DecodeLowerFetchPCOutText.text
            )
            result.DecodeLowerFetchPCOut.do_highlight = bool(
                result.DecodeLowerFetchPCOutText.text
            )
            result.DecodeInstructionMemory.do_highlight = bool(
                result.DecodeLowerFetchPCOutText.text
            )

        return result.export()

    def _get_riscv_five_stage_EX_svg_update_values(self) -> list[tuple[str, str, Any]]:
        """Returns all information needed to update EX stage part of svg."""
        result = RiscvFiveStageEXSvgDirectives()
        pipeline_register = self.state.pipeline.pipeline_registers[2]

        result.Execute.text = pipeline_register.instruction.mnemonic

        if isinstance(pipeline_register, ExecutePipelineRegister):
            result.ExecuteRightMuxOutText.text = save_to_str(pipeline_register.alu_in_1)
            result.ExecuteRightMuxOut.do_highlight = bool(
                result.ExecuteRightMuxOutText.text
            )

            result.ExecuteLeftMuxOutText.text = save_to_str(pipeline_register.alu_in_2)
            result.ExecuteLeftMuxOut.do_highlight = bool(
                result.ExecuteLeftMuxOutText.text
            )

            result.ExecuteRegisterFileReadData1.do_highlight = bool(
                save_to_str(pipeline_register.register_read_data_1)
            )

            result.ExecuteRegisterFileReadData2Text2.text = save_to_str(
                pipeline_register.register_read_data_2
            )
            result.ExecuteRegisterFileReadData2.do_highlight = bool(
                result.ExecuteRegisterFileReadData2Text2.text
            )

            result.ExecuteImmGenText1.text = save_to_str(pipeline_register.imm)
            result.ExecuteImmGenText3.text = save_to_str(pipeline_register.imm)
            result.ExecuteImmGen.do_highlight = bool(result.ExecuteImmGenText3.text)

            result.ALUResultText.text = save_to_str(pipeline_register.result)
            result.ExecuteAluResult.do_highlight = bool(result.ALUResultText.text)

            result.ExecuteInstructionMemory4Text.text = save_to_str(
                pipeline_register.write_register
            )
            result.ExecuteInstructionMemory4.do_highlight = bool(
                result.ExecuteInstructionMemory4Text.text
            )

            result.ExecuteAddText.text = save_to_str(pipeline_register.pc_plus_imm)
            result.ExecuteAdd.do_highlight = bool(result.ExecuteAddText.text)

            result.ExecuteFetchAddOutText.text = save_to_str(
                pipeline_register.pc_plus_instruction_length
            )
            result.ExecuteFetchAddOut.do_highlight = bool(
                result.ExecuteFetchAddOutText.text
            )

            result.ExecuteUpperFetchPCOutText.text = save_to_str(
                pipeline_register.address_of_instruction
            )
            result.ExecuteUpperFetchPCOut.do_highlight = bool(
                result.ExecuteUpperFetchPCOutText.text
            )
            result.ExecuteLowerFetchPCOut.do_highlight = bool(
                result.ExecuteUpperFetchPCOutText.text
            )

            result.ALUComparison.do_highlight = bool(pipeline_register.comparison)

            result.ControlUnitLeftRight3.do_highlight = bool(
                pipeline_register.control_unit_signals.alu_src_1
            )
            result.ControlUnitLeftRight4.do_highlight = bool(
                pipeline_register.control_unit_signals.alu_src_2
            )

            result.AluControl.do_highlight = bool(
                save_to_str(pipeline_register.control_unit_signals.alu_op)
            )

        return result.export()

    def _get_riscv_five_stage_MEM_svg_update_values(self) -> list[tuple[str, str, Any]]:
        """Returns all information needed to update MEM stage part of svg."""
        result = RiscvFiveStageMEMSvgDirectives()
        pipeline_register = self.state.pipeline.pipeline_registers[3]

        result.Memory.text = pipeline_register.instruction.mnemonic

        if isinstance(pipeline_register, MemoryAccessPipelineRegister):
            result.DataMemoryAddressText.text = save_to_str(
                pipeline_register.memory_address
            )

            result.MemoryExecuteAluResultText.text = save_to_str(
                pipeline_register.result
            )
            result.MemoryExecuteAluResultText2.text = save_to_str(
                pipeline_register.result
            )

            result.MemoryExecuteAluResult.do_highlight = bool(
                result.MemoryExecuteAluResultText.text
            ) and bool(result.DataMemoryAddressText.text)

            result.DataMemoryWriteDataText.text = save_to_str(
                pipeline_register.memory_write_data
            )
            result.MemoryRegisterFileReadData2.do_highlight = bool(
                result.DataMemoryWriteDataText.text
            )

            result.DataMemoryReadDataText.text = save_to_str(
                pipeline_register.memory_read_data
            )
            result.DataMemoryReadData.do_highlight = bool(
                result.DataMemoryReadDataText.text
            )

            result.MemoryInstructionMemory4Text.text = save_to_str(
                pipeline_register.write_register
            )
            result.MemoryInstructionMemory4.do_highlight = bool(
                result.MemoryInstructionMemory4Text.text
            )

            result.MemoryALUComparison.do_highlight = bool(pipeline_register.comparison)

            result.MemoryJumpOut.do_highlight = bool(
                pipeline_register.comparison_or_jump
            )

            result.MemoryExecuteAddOutText.text = save_to_str(
                pipeline_register.pc_plus_imm
            )
            result.MemoryExecuteAddOut.do_highlight = bool(
                result.MemoryExecuteAddOutText.text
            )

            result.MemoryFetchAddOutText.text = save_to_str(
                pipeline_register.pc_plus_instruction_length
            )
            result.MemoryFetchAddOut.do_highlight = bool(
                result.MemoryFetchAddOutText.text
            )

            result.MemoryImmGenText.text = save_to_str(pipeline_register.imm)
            result.MemoryImmGen.do_highlight = bool(result.MemoryImmGenText.text)

            result.ControlUnitLeftRight.do_highlight = bool(
                pipeline_register.control_unit_signals.jump
            )

            result.ControlUnitLeft.do_highlight = bool(
                pipeline_register.control_unit_signals.alu_to_pc
            )

        return result.export()

    def _get_riscv_five_stage_WB_svg_update_values(self) -> list[tuple[str, str, Any]]:
        """Returns all information needed to update WB stage part of svg."""
        result = RiscvFiveStageWBSvgDirectives()
        pipeline_register = self.state.pipeline.pipeline_registers[4]

        result.WriteBack.text = pipeline_register.instruction.mnemonic

        if isinstance(pipeline_register, RegisterWritebackPipelineRegister):
            result.RegisterFileWriteDataText.text = save_to_str(
                pipeline_register.register_write_data
            )
            result.WriteBackMuxOut.do_highlight = bool(
                result.RegisterFileWriteDataText.text
            )

            result.RegisterFileWriteRegisterText.text = save_to_str(
                pipeline_register.write_register
            )
            result.WriteBackInstructionMemory4.do_highlight = bool(
                result.RegisterFileWriteRegisterText.text
            )

            result.WriteBackDataMemoryReadDataText.text = save_to_str(
                pipeline_register.memory_read_data
            )
            result.WriteBackDataMemoryReadData.do_highlight = bool(
                result.WriteBackDataMemoryReadDataText.text
            )

            result.WriteBackExecuteAluResultText.text = save_to_str(
                pipeline_register.alu_result
            )
            result.WriteBackExecuteAluResult.do_highlight = bool(
                result.WriteBackExecuteAluResultText.text
            )

            result.WriteBackFetchAddOutText.text = save_to_str(
                pipeline_register.pc_plus_instruction_length
            )
            result.WriteBackFetchAddOut.do_highlight = bool(
                result.WriteBackFetchAddOutText.text
            )

            result.WriteBackImmGenText.text = save_to_str(pipeline_register.imm)
            result.WriteBackImmGen.do_highlight = bool(result.WriteBackImmGenText.text)

            result.wbsrc.text = save_to_str(
                pipeline_register.control_unit_signals.wb_src
            )
            result.ControlUnitLeftRight2.do_highlight = bool(result.wbsrc.text)
        return result.export()

    def _get_riscv_five_stage_OTHER_svg_update_values(
        self,
    ) -> list[tuple[str, str, Any]]:
        """Returns all information needed to do svg updates not covered by stage related directives."""
        result = RiscvFiveStageOTHERSvgDirectives()
        try:
            if_pipeline_register = self.state.pipeline.pipeline_registers[0]
            mem_pipeline_register = self.state.pipeline.pipeline_registers[3]
        except:
            return result.export()

        # pc_plus_imm_or_pc_plus_instruction_length
        pc_pl_imm_or_il = None
        # pc_plus_imm_or_pc_plus_instruction_length_or_ALU_result
        pc_pl_imm_or_il_or_alures = None

        if isinstance(mem_pipeline_register, MemoryAccessPipelineRegister):
            if mem_pipeline_register.comparison_or_jump:
                pc_pl_imm_or_il = mem_pipeline_register.pc_plus_imm
            elif isinstance(if_pipeline_register, InstructionFetchPipelineRegister):
                pc_pl_imm_or_il = if_pipeline_register.pc_plus_instruction_length

            if mem_pipeline_register.control_unit_signals.alu_to_pc:
                pc_pl_imm_or_il_or_alures = mem_pipeline_register.result
            else:
                pc_pl_imm_or_il_or_alures = pc_pl_imm_or_il

        result.FetchRightMuxOutText.text = save_to_str(pc_pl_imm_or_il)
        result.FetchLeftMuxOutText.text = save_to_str(pc_pl_imm_or_il_or_alures)

        result.FetchRightMuxOut.do_highlight = bool(result.FetchRightMuxOutText.text)

        result.path2453_0_7_7_9.do_highlight = bool(result.FetchLeftMuxOutText.text)
        result.path2453_2_5_7_0_7_5_1_0_4.do_highlight = bool(
            result.FetchLeftMuxOutText.text
        )
        result.path2453_2_5_7_0_7_6_2_29.do_highlight = bool(
            result.FetchLeftMuxOutText.text
        )

        return result.export()

    def get_riscv_single_stage_svg_update_values(self) -> list[tuple[str, str, Any]]:
        """Returns all information needed to update the svg.

        Returns:
            list[tuple[str, str, Any]]: each tuple is [svg-id, what update function to use, argument for update function (Any)].
            They can be one of ("<id>","highlight", <#hexcolor>), ("<id>", "write", <content>)
        """
        assert self.mode == "single_stage_pipeline"

        p_reg = self.state.pipeline.pipeline_registers[0]
        result = RiscvSingleStageSvgDirectives()

        if not isinstance(p_reg, SingleStagePipelineRegister):
            return result.export()
        # Text Fields

        result.add_imm_text.text = save_to_str(p_reg.pc_plus_imm)
        result.add_instr_len_text.text = save_to_str(p_reg.pc_plus_instruction_length)
        result.instr_len_text.text = save_to_str(p_reg.instruction.length)

        result.pc_text.text = save_to_str(p_reg.address_of_instruction)

        result.instr_mem_instr_text.text = save_to_str(p_reg.instruction.__repr__())
        result.instr_mem_read_addr_text.text = result.pc_text.text

        result.reg_file_read_addr1_text.text = save_to_str(p_reg.register_read_addr_1)
        result.reg_file_read_addr2_text.text = save_to_str(p_reg.register_read_addr_2)
        result.reg_file_read_data_1_text.text = save_to_str(p_reg.register_read_data_1)
        result.reg_file_read_data_2_text.text = save_to_str(p_reg.register_read_data_2)
        result.reg_file_write_reg_text.text = save_to_str(p_reg.register_write_register)
        result.reg_file_write_data_text.text = save_to_str(p_reg.register_write_data)

        result.imm_gen_value_text.text = save_to_str(p_reg.imm)

        result.alu_result_text.text = save_to_str(p_reg.alu_result)

        result.data_memory_address_text.text = save_to_str(p_reg.memory_address)
        result.data_memory_read_data_text.text = save_to_str(p_reg.memory_read_data)
        result.data_memory_write_data_value_text.text = save_to_str(
            p_reg.memory_write_data
        )

        # Paths

        # Control Unit paths

        # Binary signals

        result.control_unit_2mux_pc_path.do_highlight = (
            not p_reg.control_unit_signals.pc_from_alu_res
        )
        result.control_unit_to_and_path.do_highlight = p_reg.control_unit_signals.branch
        result.alu_control_to_read_data_2mux_path.do_highlight = (
            p_reg.control_unit_signals.alu_src_2
        )
        result.alu_control_to_read_data_1_mux_path.do_highlight = (
            not p_reg.control_unit_signals.alu_src_1
        )

        # Non Binary signals

        result.control_unit_to_4mux_path.do_highlight = (
            p_reg.control_unit_signals.wb_src
        )
        result.alu_control_to_alu_path.do_highlight = (
            p_reg.control_unit_signals.alu_control
        )

        # Other paths

        result.pc_to_add_instr_len_path.do_highlight = bool(
            result.add_instr_len_text.text
        )
        result.pc_to_add_imm_path.do_highlight = bool(result.add_imm_text.text)
        result.pc_to_2mux_path.do_highlight = p_reg.control_unit_signals.alu_src_1
        result.pc_to_instr_mem_path.do_highlight = bool(result.pc_text.text)
        result.pc_out_path.do_highlight = bool(result.pc_text.text)

        result.instr_mem_to_read_addr1_path.do_highlight = bool(
            result.reg_file_read_addr1_text.text
        )
        result.instr_mem_to_read_addr2_path.do_highlight = bool(
            result.reg_file_read_addr2_text.text
        )
        result.instr_mem_to_write_reg_path.do_highlight = bool(
            result.reg_file_write_reg_text.text
        )
        result.instr_mem_to_imm_gen_path.do_highlight = bool(
            result.imm_gen_value_text.text
        )
        result.instr_mem_to_control_unit_path.do_highlight = bool(
            result.instr_mem_instr_text.text
        )

        result.imm_gen_out_path.do_highlight = bool(result.imm_gen_value_text.text)
        result.imm_gen_to_add_path.do_highlight = bool(result.add_imm_text.text)
        result.imm_gen_to_4mux_path.do_highlight = (
            p_reg.control_unit_signals.wb_src_int == 3
        )
        result.imm_gen_to_2mux_path.do_highlight = (
            p_reg.control_unit_signals.alu_src_2
            or result.pc_to_add_imm_path.do_highlight
        )

        return result.export()
