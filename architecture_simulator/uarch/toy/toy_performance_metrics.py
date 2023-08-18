from dataclasses import dataclass
from ..performance_metrics import PerformanceMetrics


@dataclass
class ToyPerformanceMetrics(PerformanceMetrics):
    branch_count: int = 0

    def __repr__(self):
        execution_time = self.get_execution_time()
        instructions_per_second = (
            (self.instruction_count / execution_time) if execution_time else -1
        )
        representation = f"execution time: {execution_time:.2f}s\n"
        if instructions_per_second != -1:
            representation += (
                f"instructions per second: {instructions_per_second:.2f}\n"
            )
        representation += f"instructions: {self.instruction_count} \n"
        representation += f"branches: {self.branch_count}\n"
        return representation
