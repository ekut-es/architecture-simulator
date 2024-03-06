from __future__ import annotations
import sys
from typing import TYPE_CHECKING

from architecture_simulator.simulation.toy_simulation import ToySimulation
from architecture_simulator.simulation.riscv_simulation import RiscvSimulation
from architecture_simulator.isa.parser_exceptions import ParserException
from architecture_simulator.simulation.runtime_errors import (
    InstructionExecutionException,
)

if TYPE_CHECKING:
    from architecture_simulator.uarch.memory.cache import CacheOptions


def get_riscv_simulation(
    pipeline_mode: str,
    data_hazard_detection: bool,
    data_cache_options: CacheOptions,
    instruction_cache_options: CacheOptions,
) -> RiscvSimulation:
    """Creates a new RiscvSimulation.

    Args:
        pipeline_mode (str): "five_stage_pipeline" or "single_stage_pipeline"
        data_hazard_detection (bool): Whether to enable data hazard detection (only relevant for five stage pipeline)

    Returns:
        RiscvSimulation: The Simulation object.
    """
    return RiscvSimulation(
        mode=pipeline_mode,
        detect_data_hazards=data_hazard_detection,
        data_cache=data_cache_options,
        instruction_cache=instruction_cache_options,
    )


def get_toy_simulation() -> ToySimulation:
    """Creates a new ToySimulation
    Returns:
        ToySimulation: The simulation object.
    """
    return ToySimulation()


def get_last_error() -> tuple[str, str, int] | tuple[str, str]:
    """Returns the last error.

    Returns:
        tuple[str, str, int] | tuple[str, str]: Either ("ParserException", error message, line number),
        ("InstructionExecutionException", error message, address) or ("Unknown", error message)
    """
    error = sys.last_value
    if isinstance(error, ParserException):
        return ("ParserException", error.__repr__(), error.line_number)
    if isinstance(error, InstructionExecutionException):
        return ("InstructionExecutionException", error.__repr__(), error.address)
    return ("Unknown", error.__repr__())
