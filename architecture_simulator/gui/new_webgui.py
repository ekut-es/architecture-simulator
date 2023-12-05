from architecture_simulator.simulation.toy_simulation import ToySimulation
from architecture_simulator.simulation.riscv_simulation import RiscvSimulation


def get_riscv_simulation(
    pipeline_mode: str, data_hazard_detection: bool
) -> RiscvSimulation:
    """Creates a new RiscvSimulation.

    Args:
        pipeline_mode (str): "five_stage_pipeline" or "single_stage_pipeline"
        data_hazard_detection (bool): Whether to enable data hazard detection (only relevant for five stage pipeline)

    Returns:
        RiscvSimulation: The Simulation object.
    """
    return RiscvSimulation(
        mode=pipeline_mode, detect_data_hazards=data_hazard_detection
    )


def get_toy_simulation() -> ToySimulation:
    """Creates a new ToySimulation
    Returns:
        ToySimulation: The simulation object.
    """
    return ToySimulation()
