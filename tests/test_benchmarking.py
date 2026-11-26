"""Benchmark reproducibility, metrics, timing isolation, and export tests."""

import csv
from random import Random
from unittest.mock import patch

import pytest

from sortarium import benchmark, bubble_sort, generate_input, merge_sort, selection_sort
from sortarium._metrics import Counters, active_metrics
from sortarium.benchmarking import _time_sort
from sortarium.distributions import DISTRIBUTIONS


@pytest.mark.parametrize("distribution", DISTRIBUTIONS)
@pytest.mark.parametrize("size", [0, 1, 20, 100])
def test_distribution(distribution, size):
    a = generate_input(size, distribution, Random(42))
    b = generate_input(size, distribution, Random(42))
    assert a == b
    assert len(a) == size
    assert all(type(x) is int for x in a)
    if distribution in ("sorted", "nearly_sorted", "reverse"):
        assert sorted(a) == list(range(size))
    if distribution == "sorted":
        assert a == list(range(size))
    if distribution == "reverse":
        assert a == list(range(size - 1, -1, -1))
    if distribution == "uniform":
        assert all(-size <= x <= size for x in a)
    if distribution == "few_unique":
        assert all(-2 <= x <= 2 for x in a)


@pytest.mark.parametrize("distribution", DISTRIBUTIONS)
def test_all_algorithms(algorithm, distribution):
    result = benchmark([algorithm], [0, 8], distribution=distribution, trials=2)
    assert len(result.observations) == 4
    assert all(o.elapsed_time >= 0 for o in result.observations)
    assert all(o.metrics.comparisons >= 0 for o in result.observations)


def test_reproducibility():
    def counts(result):
        return [
            (
                o.algorithm,
                o.input_size,
                o.trial,
                o.metrics.comparisons,
                o.metrics.swaps,
                o.metrics.writes,
            )
            for o in result.observations
        ]

    kwargs = dict(algorithms=[bubble_sort, merge_sort], sizes=[8, 16], trials=3)
    a = benchmark(**kwargs, seed=42, warmups=0)
    b = benchmark(**kwargs, seed=42, warmups=2)
    c = benchmark(**kwargs, seed=43, warmups=0)
    assert counts(a) == counts(b)
    assert counts(a) != counts(c)


def test_paired_inputs_and_warmups():
    from sortarium import benchmarking as module

    with patch.object(module, "_time_sort", wraps=module._time_sort) as timed:
        with patch.object(module, "analyze", wraps=module.analyze) as instrumented:
            result = benchmark([bubble_sort, merge_sort], [9], trials=3, warmups=2)
    assert len(result.observations) == 6
    assert timed.call_count == 10
    assert instrumented.call_count == 6
    for i in range(3):
        measured = timed.call_args_list[4 + 2 * i : 6 + 2 * i]
        counted = instrumented.call_args_list[2 * i : 2 * i + 2]
        values = [c.args[1] for c in measured + counted]
        assert all(v == values[0] for v in values)
        assert {c.args[0] for c in measured} == {bubble_sort, merge_sort}


def test_exact_counts_and_summary():
    result = benchmark(
        [selection_sort, bubble_sort], [10], distribution="reverse", trials=3
    )
    rows = result.summary("comparisons")
    assert len(rows) == 2
    for row in rows:
        assert row.mean == row.median == row.minimum == row.maximum == 45
        assert row.stdev == 0
        assert row.trials == 3
    assert result.summary("swaps")[1].mean == 45
    assert result.summary("writes")[1].mean == 90
    assert result.summary()[0].minimum >= 0


def test_single_trial_and_reverse():
    result = benchmark(
        [bubble_sort], [10], distribution="sorted", trials=1, reverse=True
    )
    assert result.reverse is True
    assert result.summary("comparisons")[0].mean == 45
    assert result.summary()[0].stdev is None
    for metric in ("auxiliary_writes", "key_evaluations", "recursion_depth"):
        assert result.summary(metric)[0].mean == 0


def test_timing_isolation():
    counters = Counters()
    token = active_metrics.set(counters)
    try:
        with patch("sortarium.benchmarking.perf_counter_ns", side_effect=[100, 250]):
            assert _time_sort(bubble_sort, [2, 1], False) == 150 / 1e9
        assert active_metrics.get() is counters
        assert counters.comparisons == 0
        assert counters.writes == 0

        def fail(*args, **kwargs):
            raise RuntimeError("failure")

        with pytest.raises(RuntimeError):
            _time_sort(fail, [], False)
        assert active_metrics.get() is counters
    finally:
        active_metrics.reset(token)


def test_csv(tmp_path):
    result = benchmark([selection_sort], [3], trials=2, warmups=0)
    path = tmp_path / "results.csv"
    result.to_csv(path)
    with path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 2
    assert rows[0]["comparisons"] == "3"
    assert rows[0]["seed"] == "42"
    assert rows[0]["distribution"] == "uniform"
    assert rows[0]["python_version"] == result.python_version
    assert rows[0]["platform"] == result.platform
    assert float(rows[0]["elapsed_time"]) == result.observations[0].elapsed_time
    assert "instrumented_elapsed_time" in rows[0]


@pytest.mark.parametrize(
    "overrides",
    [
        {"algorithms": []},
        {"algorithms": [sorted]},
        {"algorithms": [bubble_sort, bubble_sort]},
        {"sizes": []},
        {"sizes": [-1]},
        {"sizes": [True]},
        {"sizes": [1, 1]},
        {"distribution": "unknown"},
        {"trials": 0},
        {"trials": True},
        {"warmups": -1},
        {"warmups": True},
        {"seed": None},
        {"reverse": 1},
    ],
)
def test_invalid_settings(overrides):
    kwargs = dict(algorithms=[bubble_sort], sizes=[3], trials=1)
    kwargs.update(overrides)
    with pytest.raises(ValueError):
        benchmark(**kwargs)


def test_invalid_metrics_and_inputs():
    result = benchmark([bubble_sort], [2], trials=1)
    with pytest.raises(ValueError):
        result.summary("unknown")
    with pytest.raises(ValueError):
        result.observations[0].value("unknown")
    with pytest.raises(ValueError):
        generate_input(-1, "uniform", Random(0))
    with pytest.raises(ValueError):
        generate_input(1, "unknown", Random(0))
