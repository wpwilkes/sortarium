"""Internal counters for a single sorting execution."""

from contextvars import ContextVar
from dataclasses import dataclass


@dataclass
class Counters:
    comparisons: int = 0
    swaps: int = 0
    writes: int = 0
    auxiliary_writes: int = 0
    key_evaluations: int = 0
    recursion_depth: int = 0

    def record_swap(self) -> None:
        self.swaps += 1
        self.writes += 2


active_metrics: ContextVar[Counters | None] = ContextVar(
    "sortarium_metrics", default=None
)
