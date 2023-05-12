from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    execution_time_s: float
    instruction_count: int
    instructions_per_second: float
    branch_count: int
