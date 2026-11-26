"""Paired, reproducible sorting benchmarks with separate timing and counts."""

import csv
import platform
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from random import Random
from statistics import mean, median, stdev
from time import perf_counter_ns
from typing import Literal

from ._metrics import active_metrics
from .analysis import _ALGORITHMS, SortMetrics, analyze
from .distributions import DISTRIBUTIONS, Distribution, generate_input

Metric = Literal[
    "elapsed_time",
    "comparisons",
    "swaps",
    "writes",
    "auxiliary_writes",
    "key_evaluations",
    "recursion_depth",
]
METRICS = (
    "elapsed_time",
    "comparisons",
    "swaps",
    "writes",
    "auxiliary_writes",
    "key_evaluations",
    "recursion_depth",
)
Algorithm = Callable[..., object]


@dataclass(frozen=True)
class BenchmarkObservation:
    """One paired trial; elapsed_time is measured with counters disabled."""

    algorithm: str
    input_size: int
    trial: int
    elapsed_time: float
    metrics: SortMetrics

    def value(self, metric: Metric) -> float:
        """Return the selected measurement (seconds for elapsed_time)."""
        if metric not in METRICS:
            raise ValueError(f"Unknown metric: {metric!r}")
        if metric == "elapsed_time":
            return self.elapsed_time
        return float(getattr(self.metrics, metric))


@dataclass(frozen=True)
class BenchmarkSummary:
    """Descriptive statistics for an algorithm and input size."""

    algorithm: str
    input_size: int
    metric: Metric
    trials: int
    mean: float
    median: float
    stdev: float | None
    minimum: float
    maximum: float


@dataclass(frozen=True)
class BenchmarkResult:
    """Raw observations, experiment settings, and execution environment."""

    algorithms: tuple[str, ...]
    sizes: tuple[int, ...]
    distribution: Distribution
    trials: int
    warmups: int
    seed: int
    reverse: bool
    python_version: str
    platform: str
    observations: tuple[BenchmarkObservation, ...]

    def summary(self, metric: Metric = "elapsed_time") -> tuple[BenchmarkSummary, ...]:
        """Summarize each algorithm/size group; stdev is None for one trial."""
        if metric not in METRICS:
            raise ValueError(f"Unknown metric: {metric!r}")
        groups: dict[tuple[str, int], list[float]] = {}
        for observation in self.observations:
            group = (observation.algorithm, observation.input_size)
            groups.setdefault(group, []).append(observation.value(metric))
        return tuple(
            BenchmarkSummary(
                algorithm=algorithm,
                input_size=size,
                metric=metric,
                trials=len(values),
                mean=mean(values),
                median=median(values),
                stdev=stdev(values) if len(values) > 1 else None,
                minimum=min(values),
                maximum=max(values),
            )
            for (algorithm, size), values in groups.items()
        )

    def to_csv(self, path: str | Path) -> None:
        """Export one row per observation, with settings and environment."""
        columns = (
            "algorithm",
            "input_size",
            "trial",
            "distribution",
            "seed",
            "reverse",
            "trials",
            "warmups",
            "python_version",
            "platform",
            *METRICS,
            "instrumented_elapsed_time",
        )
        with Path(path).open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            for observation in self.observations:
                writer.writerow(
                    {
                        "algorithm": observation.algorithm,
                        "input_size": observation.input_size,
                        "trial": observation.trial,
                        "distribution": self.distribution,
                        "seed": self.seed,
                        "reverse": self.reverse,
                        "trials": self.trials,
                        "warmups": self.warmups,
                        "python_version": self.python_version,
                        "platform": self.platform,
                        "elapsed_time": observation.elapsed_time,
                        "comparisons": observation.metrics.comparisons,
                        "swaps": observation.metrics.swaps,
                        "writes": observation.metrics.writes,
                        "auxiliary_writes": observation.metrics.auxiliary_writes,
                        "key_evaluations": observation.metrics.key_evaluations,
                        "recursion_depth": observation.metrics.recursion_depth,
                        "instrumented_elapsed_time": observation.metrics.elapsed_time,
                    }
                )


def _time_sort(algorithm: Algorithm, values: list[int], reverse: bool) -> float:
    """Time sorting a fresh copy with instrumentation inactive."""
    data = values.copy()
    token = active_metrics.set(None)
    try:
        start = perf_counter_ns()
        algorithm(data, reverse=reverse, inplace=True)
        elapsed = perf_counter_ns() - start
    finally:
        active_metrics.reset(token)
    return elapsed / 1_000_000_000


def benchmark(
    algorithms: Sequence[Algorithm],
    sizes: Sequence[int],
    *,
    distribution: Distribution = "uniform",
    trials: int = 30,
    warmups: int = 1,
    seed: int = 42,
    reverse: bool = False,
) -> BenchmarkResult:
    """Benchmark built-in algorithms on paired, reproducible integer inputs.

    Generate inputs outside the measured interval. Perform unrecorded warmups,
    followed by trials. Randomize timing order using an independent RNG.
    Measure operation counts separately via analyze(). All times are seconds.
    """
    algs = tuple(algorithms)
    lengths = tuple(sizes)
    if not algs or any(not any(a is b for b in _ALGORITHMS) for a in algs):
        raise ValueError("algorithms must contain supported Sortarium functions")
    if len(set(algs)) != len(algs):
        raise ValueError("algorithms must be unique")
    if not lengths or any(type(n) is not int or n < 0 for n in lengths):
        raise ValueError("sizes must contain nonnegative integers")
    if len(set(lengths)) != len(lengths):
        raise ValueError("sizes must be unique")
    if distribution not in DISTRIBUTIONS:
        raise ValueError(f"Unknown distribution: {distribution!r}")
    if type(trials) is not int or trials < 1:
        raise ValueError("trials must be a positive integer")
    if type(warmups) is not int or warmups < 0:
        raise ValueError("warmups must be a nonnegative integer")
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    if type(reverse) is not bool:
        raise ValueError("reverse must be a boolean")

    rng = Random(seed)
    warmup_rng = Random(seed + 1)
    order_rng = Random(seed + 2)
    observations: list[BenchmarkObservation] = []
    for size in lengths:
        for _ in range(warmups):
            values = generate_input(size, distribution, warmup_rng)
            order = list(algs)
            order_rng.shuffle(order)
            for algorithm in order:
                _time_sort(algorithm, values, reverse)

        for trial in range(trials):
            values = generate_input(size, distribution, rng)
            order = list(algs)
            order_rng.shuffle(order)
            timings = {
                algorithm: _time_sort(algorithm, values, reverse) for algorithm in order
            }
            for algorithm in algs:
                result = analyze(algorithm, values, reverse=reverse)
                observations.append(
                    BenchmarkObservation(
                        algorithm=result.algorithm,
                        input_size=size,
                        trial=trial,
                        elapsed_time=timings[algorithm],
                        metrics=result.metrics,
                    )
                )

    return BenchmarkResult(
        algorithms=tuple(a.__name__ for a in algs),
        sizes=lengths,
        distribution=distribution,
        trials=trials,
        warmups=warmups,
        seed=seed,
        reverse=reverse,
        python_version=platform.python_version(),
        platform=platform.platform(),
        observations=tuple(observations),
    )
