from dataclasses import dataclass

from ..performance_metrics import PerformanceMetrics


@dataclass
class RiscvPerformanceMetrics(PerformanceMetrics):
    branch_count: int = 0
    procedure_count: int = 0
    flushes: int = 0
    cycles: int = 0

    def __repr__(self) -> str:
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
        representation += f"procedures: {self.procedure_count}\n"
        representation += f"cycles: {self.cycles}\n"
        representation += f"flushes: {self.flushes}\n"
        if not self.instruction_count == 0:
            representation += f"cycles per instruction: {(self.cycles / self.instruction_count):.2f}\n"
        return representation
