"""Public API for instrumented sorting."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from time import perf_counter
from typing import Generic, TypeVar

from ._metrics import Counters, active_metrics
from ._ordering import SupportsLessThan
from .bubble import bubble_sort
from .bucket import bucket_sort
from .heap import heap_sort
from .insertion import insertion_sort
from .merge import merge_sort
from .quick import quick_sort
from .selection import selection_sort

T = TypeVar("T")

_ALGORITHMS = (
    bubble_sort,
    bucket_sort,
    heap_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    selection_sort,
)


@dataclass(frozen=True)
class SortMetrics:
    """Operation counts and instrumented wall-clock seconds."""

    comparisons: int
    swaps: int
    writes: int
    auxiliary_writes: int
    key_evaluations: int
    recursion_depth: int
    elapsed_time: float


@dataclass(frozen=True)
class AnalysisResult(Generic[T]):
    """Sorted output and measurements for one execution."""

    algorithm: str
    input_size: int
    output: list[T]
    metrics: SortMetrics


def analyze(
    algorithm: Callable[..., object],
    sequence: Sequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
) -> AnalysisResult[T]:
    """Instrument a supported Sortarium function without mutating the input.

    Bucket sort requires integer-valued keys. The initial input copy is
    excluded from all metrics, including elapsed time. Timing includes
    instrumentation overhead; use uninstrumented sorting for benchmarking.
    """
    if not any(algorithm is supported for supported in _ALGORITHMS):
        raise ValueError("analyze requires a supported Sortarium algorithm.")

    data = list(sequence)
    counters = Counters()
    token = active_metrics.set(counters)
    try:
        start = perf_counter()
        algorithm(data, key=key, reverse=reverse, inplace=True)
        elapsed = perf_counter() - start
    finally:
        active_metrics.reset(token)

    return AnalysisResult(
        algorithm=algorithm.__name__,
        input_size=len(data),
        output=data,
        metrics=SortMetrics(
            comparisons=counters.comparisons,
            swaps=counters.swaps,
            writes=counters.writes,
            auxiliary_writes=counters.auxiliary_writes,
            key_evaluations=counters.key_evaluations,
            recursion_depth=counters.recursion_depth,
            elapsed_time=elapsed,
        ),
    )
