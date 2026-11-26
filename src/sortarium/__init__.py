"""Public sorting algorithm API."""

from .analysis import AnalysisResult, SortMetrics, analyze
from .benchmarking import (
    BenchmarkObservation,
    BenchmarkResult,
    BenchmarkSummary,
    benchmark,
)
from .bubble import bubble_sort
from .bucket import bucket_sort
from .distributions import generate_input
from .heap import heap_sort
from .insertion import insertion_sort
from .merge import merge_sort
from .quick import quick_sort
from .selection import selection_sort

__all__ = [
    "AnalysisResult",
    "BenchmarkObservation",
    "BenchmarkResult",
    "BenchmarkSummary",
    "SortMetrics",
    "analyze",
    "benchmark",
    "bubble_sort",
    "bucket_sort",
    "generate_input",
    "heap_sort",
    "insertion_sort",
    "merge_sort",
    "quick_sort",
    "selection_sort",
]
