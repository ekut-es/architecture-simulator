from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Any

from architecture_simulator.settings.settings import Settings
from architecture_simulator.uarch.riscv.riscv_architectural_state import (
    RiscvArchitecturalState,
)
from architecture_simulator.isa.riscv.instruction_types import EmptyInstruction
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
    from architecture_simulator.uarch.memory.cache import CacheOptions
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


def save_to_str(input: Any, input_valid=True) -> str:
    """Turns the input into a string. Will result in an empty string if the input is None or if the optional input_valid flag is False.

    Args:
        input (Any): Thing to be turned into a string.
        input_valid (bool, optional): Flag to indicate if the input is valid. The result will be an empty string if this is False. Defaults to True.

    Returns:
        str: The requested string.
    """
    return str(input) if input is not None and input_valid else ""


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
        data_cache: CacheOptions = Settings().get()["data_cache"],
        instruction_cache: CacheOptions = Settings().get()["instruction_cache"],
    ) -> None:
        """Constructor for RISC-V simulations.

        Args:
            state (Optional[ArchitecturalState], optional): The state to use. Creates a sensible default.
            mode (str, optional): Can be one of "single_stage_pipeline" (default) or "five_stage_pipeline".
            detect_data_hazards (bool, optional): Turn data hazard detection on or off. Defaults to True.
        """
        self.state = (
            RiscvArchitecturalState(
                pipeline_mode=mode,
                detect_data_hazards=detect_data_hazards,
                data_cache_options=data_cache,
                instruction_cache_options=instruction_cache,
            )
            if state is None
            else state
        )
        self.mode = mode
        super().__init__()

    def step(self) -> bool:
        if not self.is_done():
            self.has_started = True
            self.state.previous_program_counter = (
                self.state.program_counter
            )  # maybe this should not go here
            self.state.pipeline.step()
        return not self.is_done()

    def run(self):
        self.state.performance_metrics.resume_timer()
        while not self.is_done():
            self.step()
        self.state.performance_metrics.stop_timer()

    def get_exit_code(self):
        return self.state.exit_code

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
        return self.state.instruction_memory.has_instructions()

    def get_performance_metrics(self) -> RiscvPerformanceMetrics:
        return self.state.performance_metrics

    def get_output(self) -> str:
        return self.state.output

    def get_register_entries(self) -> list[tuple[str, str, str, str]]:
        """Returns the contents of the register file as bin, udec, hex, sdec values.

        Returns:
            list[tuple[str, str, str, str]]: Register values as tuples of (bin, udec, hex, sdec)
        """
        return self.state.register_file.reg_repr()

    def get_instruction_memory_entries(self) -> list[tuple[tuple[int, str], str, str]]:
        """Returns a list of the address (as int and as hex string),
        instruction and pipeline stage of the instruction for all instructions in the instruction memory.

        Returns:
            list[tuple[str, str, str]]: List of ((int_address, hex_address), instruction, stage).
        """
        pipeline_stages_addresses: dict[int, str] = {}
        for pipeline_register in self.state.pipeline.pipeline_registers:
            if pipeline_register.address_of_instruction is not None:
                pipeline_stages_addresses[
                    pipeline_register.address_of_instruction
                ] = pipeline_register.abbreviation

        return [
            (
                (address, "0x" + "{:08X}".format(address)),
                instruction,
                (
                    pipeline_stages_addresses[address]
                    if address in pipeline_stages_addresses
                    else ""
                ),
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

    def get_data_cache_entries(self):
        return self.state.memory.cache_repr()

    def get_data_cache_stats(self):
        """Returns the stats of the data cache (will be None if no cache is used).

        Returns:
            dict[str, Optional[str]] | None: The cache stats, plus the last address that was accessed under the key "address".
        """
        stats = self.state.memory.get_cache_stats()
        if stats is None:
            return None

        address = None
        if self.state.pipeline_mode == "five_stage_pipeline":
            pipeline_register = self.state.pipeline.pipeline_registers[3]
            if isinstance(pipeline_register, MemoryAccessPipelineRegister):
                # there might be an address even if the instruction doesn't access the memory
                if (
                    pipeline_register.control_unit_signals.mem_write
                    or pipeline_register.control_unit_signals.mem_read
                ):
                    address = pipeline_register.memory_address
        else:
            pipeline_register = self.state.pipeline.pipeline_registers[0]
            if isinstance(pipeline_register, SingleStagePipelineRegister):
                address = pipeline_register.memory_address

        if address is not None:
            address = "{:032b}".format(address % (2**32))  # address might be negative

        stats = self.state.memory.get_cache_stats()
        stats["address"] = address
        return stats

    def get_instruction_cache_entries(self):
        """Returns the instruction cache entries as a dict (deeply converted).

        Returns:
            dict[str, Any]: The instruction cache entries as dict.
        """
        return self.state.instruction_memory.cache_repr()

    def get_instruction_cache_stats(self):
        """Returns the stats of the instruction cache (will be None if no cache is used).

        Returns:
            dict[str, Optional[str]] | None: The cache stats, plus the last address that was accessed under the key "address".
        """
        stats = self.state.instruction_memory.get_cache_stats()
        if stats is None:
            return None

        pipeline_register = self.state.pipeline.pipeline_registers[0]
        if isinstance(
            pipeline_register, InstructionFetchPipelineRegister
        ) or isinstance(pipeline_register, SingleStagePipelineRegister):
            address = pipeline_register.address_of_instruction
            if address is not None:
                address = "{:032b}".format(
                    address % (2**32)
                )  # address shouldn't be negative, but lets check anyway
        else:
            address = None
        stats["address"] = address
        return stats

    def get_riscv_five_stage_svg_update_values(self) -> list[tuple[str, str, Any]]:
        """Returns all information needed to update the svg.

        Returns:
            list[tuple[str, str, Any]]: each tuple is [svg-id, what update function to use, argument for update function (Any)].
            They can be one of ("<id>","highlight", <#hexcolor>), ("<id>", "write-center", <content>),
            ("<id>", "write-left", <content>), ("<id>", "write-right", <content>)
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
        pr = self.state.pipeline.pipeline_registers[0]

        result.Fetch.text = pr.instruction.mnemonic
        result.PC.text = self.state.previous_program_counter

        if isinstance(pr, InstructionFetchPipelineRegister):
            csignals = pr.control_unit_signals
            result.InstructionMemoryInstrText.text = pr.instruction.__repr__()
            result.InstructionMemory.do_highlight = bool(
                result.InstructionMemoryInstrText.text
            )

            result.InstructionReadAddressText.text = save_to_str(
                pr.address_of_instruction
            )
            result.FetchPCOut.do_highlight = bool(
                result.InstructionReadAddressText.text
            )

            result.FetchAddOutToMux.do_highlight = (
                pr.pc_plus_instruction_length is not None
            )
            result.FetchAddOut.do_highlight = pr.pc_plus_instruction_length is not None

            result.FetchI_Length.do_highlight = not isinstance(
                pr.instruction, EmptyInstruction
            )
            result.I_LengthText.text = save_to_str(
                pr.instruction.length, result.FetchI_Length.do_highlight
            )
            result.PCFetchOutToExAdder.do_highlight = bool(csignals.jump) | bool(
                csignals.branch
            )
            result.PCFetchOutToExMux.do_highlight = (
                csignals.alu_src_1 is not None and not bool(csignals.alu_src_1)
            )
            result.FetchAddOutToPReg.do_highlight = csignals.wb_src == 0

        return result.export()

    def _get_riscv_five_stage_ID_svg_update_values(self) -> list[tuple[str, str, Any]]:
        """Returns all information needed to update ID stage part of svg."""
        result = RiscvFiveStageIDSvgDirectives()
        pr = self.state.pipeline.pipeline_registers[1]

        result.Decode.text = pr.instruction.mnemonic

        if isinstance(pr, InstructionDecodePipelineRegister):
            csignals = pr.control_unit_signals
            result.RegisterFileReadAddress1Text.text = save_to_str(
                pr.register_read_addr_1
            )
            result.DecodeInstructionMemory1.do_highlight = bool(
                result.RegisterFileReadAddress1Text.text
            )

            result.RegisterFileReadAddress2Text.text = save_to_str(
                pr.register_read_addr_2
            )
            result.DecodeInstructionMemory2.do_highlight = bool(
                result.RegisterFileReadAddress2Text.text
            )

            result.RegisterFileReadData1Text.text = save_to_str(pr.register_read_data_1)
            result.RegisterFileReadData1.do_highlight = bool(
                result.RegisterFileReadData1Text.text
            )

            result.RegisterFileReadData2Text.text = save_to_str(pr.register_read_data_2)
            result.RegisterFileReadData2.do_highlight = bool(
                result.RegisterFileReadData2Text.text
            )

            result.ImmGenText.text = save_to_str(pr.imm)
            result.ImmGenOut.do_highlight = bool(result.ImmGenText.text)
            result.DecodeInstructionMemory3.do_highlight = bool(result.ImmGenText.text)

            result.DecodeInstructionMemory4Text.text = save_to_str(pr.write_register)
            result.DecodeInstructionMemory4.do_highlight = bool(
                result.DecodeInstructionMemory4Text.text
            )

            result.DecodeFetchAddOut.do_highlight = csignals.wb_src == 0
            result.DecodeFetchAddOutText.text = save_to_str(
                pr.pc_plus_instruction_length, result.DecodeFetchAddOut.do_highlight
            )

            result.DecodeUpperFetchPCOut.do_highlight = bool(csignals.jump) | bool(
                csignals.branch
            )
            result.DecodeUpperFetchPCOutText.text = save_to_str(
                pr.address_of_instruction, result.DecodeUpperFetchPCOut.do_highlight
            )

            result.DecodeLowerFetchPCOut.do_highlight = csignals.alu_src_1 == 0
            result.DecodeLowerFetchPCOutText.text = save_to_str(
                pr.address_of_instruction, result.DecodeLowerFetchPCOut.do_highlight
            )

            result.DecodeInstructionMemory.do_highlight = not isinstance(
                pr.instruction, EmptyInstruction
            )
            result.ControlUnitLeftRight1_1.do_highlight = bool(csignals.jump)
            result.ControlUnitLeftRight2_1.do_highlight = csignals.wb_src is not None
            result.ControlUnitLeftRight3_1.do_highlight = bool(csignals.alu_src_1)
            result.ControlUnitLeftRight4_1.do_highlight = bool(csignals.alu_src_2)
            result.ControlUnitLeft_1.do_highlight = bool(csignals.alu_to_pc)
            result.ControlUnitRegWriteEnable_1.do_highlight = bool(csignals.reg_write)
            result.ControlUnitMemWriteEnable_1.do_highlight = bool(csignals.mem_write)
            result.ControlUnitMemReadEnable_1.do_highlight = bool(csignals.mem_read)

            result.DecodeInstructionMemoryIntermediate.do_highlight = bool(
                csignals.reg_write
            ) | (pr.imm is not None)

        return result.export()

    def _get_riscv_five_stage_EX_svg_update_values(self) -> list[tuple[str, str, Any]]:
        """Returns all information needed to update EX stage part of svg."""
        result = RiscvFiveStageEXSvgDirectives()
        pr = self.state.pipeline.pipeline_registers[2]

        result.Execute.text = pr.instruction.mnemonic

        if isinstance(pr, ExecutePipelineRegister):
            csignals = pr.control_unit_signals
            result.ExecuteRightMuxOutText.text = save_to_str(pr.alu_in_1)
            result.ExecuteRightMuxOut.do_highlight = bool(
                result.ExecuteRightMuxOutText.text
            )

            result.ExecuteLeftMuxOutText.text = save_to_str(pr.alu_in_2)
            result.ExecuteLeftMuxOut.do_highlight = bool(
                result.ExecuteLeftMuxOutText.text
            )

            result.ExecuteRegisterFileReadData1.do_highlight = bool(
                save_to_str(pr.register_read_data_1)
            )

            result.ExecuteRegisterFileReadData2Text2.text = save_to_str(
                pr.register_read_data_2
            )
            result.ExecuteRegisterFileReadData2.do_highlight = bool(
                result.ExecuteRegisterFileReadData2Text2.text
            )

            result.ExecuteImmGen.do_highlight = pr.imm is not None

            result.ALUResultText.text = save_to_str(pr.result)
            result.ExecuteAluResult.do_highlight = bool(result.ALUResultText.text)

            result.ExecuteInstructionMemory4Text.text = save_to_str(pr.write_register)
            result.ExecuteInstructionMemory4.do_highlight = bool(
                result.ExecuteInstructionMemory4Text.text
            )

            result.ExecuteFetchAddOut.do_highlight = csignals.wb_src == 0
            result.ExecuteFetchAddOutText.text = save_to_str(
                pr.pc_plus_instruction_length, result.ExecuteFetchAddOut.do_highlight
            )

            result.ALUComparison.do_highlight = bool(pr.comparison)

            result.ControlUnitLeftRight1_2.do_highlight = bool(csignals.jump)
            result.ControlUnitLeftRight2_2.do_highlight = csignals.wb_src is not None
            result.ControlUnitLeftRight3_2.do_highlight = bool(csignals.alu_src_1)
            result.ControlUnitLeftRight4_2.do_highlight = bool(csignals.alu_src_2)
            result.ControlUnitLeft_2.do_highlight = bool(csignals.alu_to_pc)

            result.AluControl.do_highlight = bool(save_to_str(csignals.alu_op))

            result.ExecuteImmediateToAdder.do_highlight = bool(csignals.jump) | bool(
                csignals.branch
            )
            result.ExecuteImmGenText1.text = save_to_str(
                pr.imm, result.ExecuteImmediateToAdder.do_highlight
            )

            result.ExecuteUpperFetchPCOut.do_highlight = (
                result.ExecuteImmediateToAdder.do_highlight
            )
            result.ExecuteUpperFetchPCOutText.text = save_to_str(
                pr.address_of_instruction, result.ExecuteUpperFetchPCOut.do_highlight
            )

            result.ExecuteAdd.do_highlight = result.ExecuteUpperFetchPCOut.do_highlight
            result.ExecuteAddText.text = save_to_str(
                pr.pc_plus_imm, result.ExecuteAdd.do_highlight
            )

            result.ExecuteLowerFetchPCOut.do_highlight = csignals.alu_src_1 is False

            result.ExecuteImmediateToMux.do_highlight = csignals.alu_src_2

            result.ExecuteImmediateToWbMux.do_highlight = csignals.wb_src == 3
            result.ExecuteImmGenText3.text = save_to_str(
                pr.imm, result.ExecuteImmediateToWbMux.do_highlight
            )

            result.ExecuteImmediateInterediate.do_highlight = (
                bool(csignals.alu_src_2) or result.ExecuteImmediateToAdder.do_highlight
            )

            result.ExecuteRegisterFileReadData2ToMux.do_highlight = (
                csignals.alu_src_2 is False
            )
            result.ExecuteRegisterFileReadData2ToMemory.do_highlight = bool(
                csignals.mem_write
            )

            result.ControlUnitRegWriteEnable_2.do_highlight = bool(csignals.reg_write)
            result.ControlUnitMemWriteEnable_2.do_highlight = bool(csignals.mem_write)
            result.ControlUnitMemReadEnable_2.do_highlight = bool(csignals.mem_read)

        return result.export()

    def _get_riscv_five_stage_MEM_svg_update_values(self) -> list[tuple[str, str, Any]]:
        """Returns all information needed to update MEM stage part of svg."""
        result = RiscvFiveStageMEMSvgDirectives()
        pr = self.state.pipeline.pipeline_registers[3]

        result.Memory.text = pr.instruction.mnemonic

        if isinstance(pr, MemoryAccessPipelineRegister):
            csignals = pr.control_unit_signals

            result.MemoryExecuteAluResult.do_highlight = pr.result is not None

            result.MemoryRegisterFileReadData2.do_highlight = bool(csignals.mem_write)
            result.DataMemoryWriteDataText.text = save_to_str(
                pr.memory_write_data, result.MemoryRegisterFileReadData2.do_highlight
            )

            result.DataMemoryReadDataText.text = save_to_str(pr.memory_read_data)
            result.DataMemoryReadData.do_highlight = bool(
                result.DataMemoryReadDataText.text
            )

            result.MemoryInstructionMemory4Text.text = save_to_str(pr.write_register)
            result.MemoryInstructionMemory4.do_highlight = bool(
                result.MemoryInstructionMemory4Text.text
            )

            result.MemoryALUComparison.do_highlight = bool(pr.comparison)

            result.MemoryJumpOut.do_highlight = bool(pr.comparison_or_jump)

            result.MemoryExecuteAddOut.do_highlight = result.MemoryJumpOut.do_highlight

            result.MemoryFetchAddOut.do_highlight = csignals.wb_src == 0
            result.MemoryFetchAddOutText.text = save_to_str(
                pr.pc_plus_instruction_length, result.MemoryFetchAddOut.do_highlight
            )

            result.MemoryImmGen.do_highlight = csignals.wb_src == 3
            result.MemoryImmGenText.text = save_to_str(
                pr.imm, result.MemoryImmGen.do_highlight
            )

            result.ControlUnitLeftRight1_3.do_highlight = bool(csignals.jump)
            result.ControlUnitLeftRight2_3.do_highlight = csignals.wb_src is not None
            result.ControlUnitLeft_3.do_highlight = bool(csignals.alu_to_pc)

            result.MemoryExecuteAluResultToMemory.do_highlight = bool(
                csignals.mem_read
            ) or bool(csignals.mem_write)
            result.DataMemoryAddressText.text = save_to_str(
                pr.memory_address, result.MemoryExecuteAluResultToMemory.do_highlight
            )
            result.MemoryExecuteAluResultToFetchMux.do_highlight = (
                csignals.alu_to_pc is True
            )
            result.MemoryExecuteAluResultIntermediate.do_highlight = (
                result.MemoryExecuteAluResultToMemory.do_highlight
                or result.MemoryExecuteAluResultToFetchMux.do_highlight
            )
            result.MemoryExecuteAluResultToWbMux.do_highlight = csignals.wb_src == 2
            result.MemoryExecuteAluResultText2.text = save_to_str(
                pr.result, result.MemoryExecuteAluResultToWbMux.do_highlight
            )

            result.ControlUnitRegWriteEnable_3.do_highlight = bool(csignals.reg_write)
            result.ControlUnitMemReadEnable_3.do_highlight = bool(csignals.mem_read)
            result.ControlUnitMemWriteEnable_3.do_highlight = bool(csignals.mem_write)
        return result.export()

    def _get_riscv_five_stage_WB_svg_update_values(self) -> list[tuple[str, str, Any]]:
        """Returns all information needed to update WB stage part of svg."""
        result = RiscvFiveStageWBSvgDirectives()
        pr = self.state.pipeline.pipeline_registers[4]

        result.WriteBack.text = pr.instruction.mnemonic

        if isinstance(pr, RegisterWritebackPipelineRegister):
            csignals = pr.control_unit_signals
            result.RegisterFileWriteDataText.text = save_to_str(pr.register_write_data)
            result.WriteBackMuxOut.do_highlight = bool(
                result.RegisterFileWriteDataText.text
            )

            result.RegisterFileWriteRegisterText.text = save_to_str(pr.write_register)
            result.WriteBackInstructionMemory4.do_highlight = bool(
                result.RegisterFileWriteRegisterText.text
            )

            result.WriteBackDataMemoryReadData.do_highlight = csignals.wb_src == 1

            result.WriteBackExecuteAluResult.do_highlight = (
                pr.control_unit_signals.wb_src == 2
            )

            result.WriteBackFetchAddOut.do_highlight = (
                pr.control_unit_signals.wb_src == 0
            )

            result.WriteBackImmGen.do_highlight = pr.control_unit_signals.wb_src == 3

            result.wbsrc.text = save_to_str(pr.control_unit_signals.wb_src)
            result.ControlUnitLeftRight2_4.do_highlight = (
                pr.control_unit_signals.wb_src is not None
            )

            result.ControlUnitRegWriteEnable_4.do_highlight = (
                pr.control_unit_signals.reg_write is True
            )
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

        result.FetchLeftMuxOutText.text = save_to_str(pc_pl_imm_or_il_or_alures)

        result.FetchRightMuxOut.do_highlight = pc_pl_imm_or_il is not None

        result.FetchPCIn.do_highlight = bool(result.FetchLeftMuxOutText.text)

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
        result.control_unit_to_and_path.do_highlight = p_reg.control_unit_signals.jump
        result.alu_control_to_read_data_2mux_path.do_highlight = bool(
            p_reg.control_unit_signals.alu_src_2
        )
        result.alu_control_to_read_data_1_mux_path.do_highlight = (
            p_reg.control_unit_signals.alu_src_1 is not None
        ) and (not p_reg.control_unit_signals.alu_src_1)

        # Non Binary signals

        result.control_unit_to_4mux_path.do_highlight = (
            p_reg.control_unit_signals.wb_src_int is not None
        )
        result.alu_control_to_alu_path.do_highlight = (
            p_reg.control_unit_signals.alu_control
        )

        # Other paths

        result.pc_to_add_instr_len_path.do_highlight = bool(
            result.add_instr_len_text.text
        )
        result.pc_to_add_imm_path.do_highlight = bool(result.add_imm_text.text)
        result.pc_to_2mux_path.do_highlight = bool(p_reg.control_unit_signals.alu_src_1)
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

        result.read_data2_to_mem_write_data_path.do_highlight = bool(
            result.data_memory_write_data_value_text.text
        )
        result.read_data_1_mux_to_alu_path.do_highlight = (
            p_reg.control_unit_signals.alu_src_1 is not None
        )
        result.read_data_1_to_2mux_path.do_highlight = bool(
            bool(result.reg_file_read_data_1_text.text)
        )
        result.read_data_2_2mux_to_alu_path.do_highlight = not (
            p_reg.control_unit_signals.alu_src_2 is None
        )
        result.read_data_2_to_2mux_path.do_highlight = bool(
            result.reg_file_read_data_2_text.text
        )

        result.alu_out_path.do_highlight = bool(result.alu_result_text.text)
        result.alu_to_data_memory_address_path.do_highlight = bool(
            result.data_memory_address_text.text
        )
        result.alu_out_to_4mux_path.do_highlight = (
            p_reg.control_unit_signals.wb_src_int == 2
        )
        result.alu_out_to_2mux_path.do_highlight = (
            result.alu_out_path.do_highlight
            and (not result.alu_to_data_memory_address_path.do_highlight)
            and (not result.alu_out_to_4mux_path.do_highlight)
        )
        result.alu_comparison_to_and_path.do_highlight = p_reg.alu_comparison

        result.and_to_mux_path.do_highlight = (
            result.control_unit_to_and_path.do_highlight
            or result.alu_comparison_to_and_path.do_highlight
        )

        result.add_imm_to_mux_path.do_highlight = bool(result.add_imm_text.text)
        result.add_instr_len_out_path.do_highlight = bool(
            result.add_instr_len_text.text
        )
        result.add_instr_len_to_4mux_path.do_highlight = (
            p_reg.control_unit_signals.wb_src_int == 0
        )
        result.add_instr_len_to_2mux_path.do_highlight = (
            result.add_instr_len_out_path.do_highlight
            and (not result.add_instr_len_to_4mux_path.do_highlight)
        )

        result.two_mux_2mux_path.do_highlight = (
            result.add_imm_to_mux_path.do_highlight
            or result.add_instr_len_to_2mux_path.do_highlight
        )
        result.two_mux_to_pc_path.do_highlight = (
            result.two_mux_2mux_path.do_highlight
            or result.alu_out_to_2mux_path.do_highlight
        )

        result.instr_len_to_add_path.do_highlight = bool(result.instr_len_text.text)

        result.four_mux_to_write_data_path.do_highlight = (
            p_reg.control_unit_signals.wb_src_int is not None
        )

        result.data_mem_read_data_to_4mux_path.do_highlight = bool(
            result.data_memory_read_data_text.text
        )
        return result.export()
