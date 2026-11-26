"""Verify instrumentation against independent operation counts."""

from dataclasses import FrozenInstanceError
from math import comb

import pytest

from sortarium import (
    analyze,
    bubble_sort,
    bucket_sort,
    heap_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    selection_sort,
)


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("values", [(), (1,), (3, -1, 3, 0, 1)])
def test_analysis_contract(algorithm, values, reverse):
    data = list(values)
    result = analyze(algorithm, data, reverse=reverse)
    assert result.output == sorted(values, reverse=reverse)
    assert result.output is not data
    assert data == list(values)
    assert result.input_size == len(values)
    assert result.algorithm == algorithm.__name__
    assert result.metrics.elapsed_time >= 0
    assert result.metrics.writes >= 2 * result.metrics.swaps
    assert result.metrics.key_evaluations == 0


@pytest.mark.parametrize("n", [0, 1, 2, 10, 30])
def test_selection_comparisons(n):
    for data in (list(range(n)), list(reversed(range(n))), [0] * n):
        assert analyze(selection_sort, data).metrics.comparisons == comb(n, 2)


@pytest.mark.parametrize("n", [0, 1, 2, 10, 30])
def test_bubble_counts(n):
    best = analyze(bubble_sort, list(range(n))).metrics
    assert best.comparisons == max(0, n - 1)
    assert best.swaps == best.writes == 0
    worst = analyze(bubble_sort, list(reversed(range(n)))).metrics
    assert worst.comparisons == worst.swaps == comb(n, 2)
    assert worst.writes == 2 * comb(n, 2)


@pytest.mark.parametrize("n", [0, 1, 2, 10, 30])
def test_insertion_counts(n):
    best = analyze(insertion_sort, list(range(n))).metrics
    assert best.comparisons == best.writes == max(0, n - 1)
    worst = analyze(insertion_sort, list(reversed(range(n)))).metrics
    assert worst.comparisons == comb(n, 2)
    assert worst.writes == comb(n, 2) + max(0, n - 1)
    assert best.swaps == worst.swaps == 0


def test_merge_counts():
    m = analyze(merge_sort, [1, 2, 3, 4]).metrics
    assert m.comparisons == 4
    assert m.writes == 8
    assert m.auxiliary_writes == 12
    assert m.recursion_depth == 3
    assert m.swaps == 0


def test_quick_equal_keys():
    m = analyze(quick_sort, [4] * 10).metrics
    assert m.comparisons == 20
    assert m.swaps == m.writes == 0
    assert m.recursion_depth == 2


def test_quick_self_swap():
    m = analyze(quick_sort, [1, 2]).metrics
    assert m.swaps == 1  # The greater partition exchanges index 1 with itself.
    assert m.writes == 2


def test_heap_counts():
    m = analyze(heap_sort, [1, 2]).metrics
    assert m.comparisons == 1
    assert m.swaps == 2
    assert m.writes == 4
    assert m.recursion_depth == 0


@pytest.mark.parametrize("reverse", [False, True])
def test_bucket_counts(reverse):
    m = analyze(bucket_sort, [0, 1, 2, 3], reverse=reverse).metrics
    assert m.comparisons == 6  # min and max, one key per bucket
    assert m.writes == 4
    assert m.auxiliary_writes == 8  # four pairs and four bucket insertions
    assert m.swaps == m.recursion_depth == 0


def test_bucket_internal_shifts():
    m = analyze(bucket_sort, [3, 2, 1, 100]).metrics
    assert m.comparisons == 9  # six range comparisons plus three insertion comparisons
    assert m.auxiliary_writes == 13  # eight appends, three shifts, two placements
    assert m.writes == 4


def test_key_counts(algorithm):
    calls = []

    def key(value):
        calls.append(value)
        return -value

    result = analyze(algorithm, [5, 2, 1, 4], key=key)
    assert result.output == [5, 4, 2, 1]
    assert result.metrics.key_evaluations == len(calls)
    if algorithm is bucket_sort:
        assert len(calls) == 4
    else:
        assert len(calls) == 2 * result.metrics.comparisons


def test_custom_key_nested_sorts_are_isolated():
    def key(value):
        nested = analyze(selection_sort, [3, 2, 1])
        assert nested.metrics.comparisons == 3
        plain = [3, 2, 1]
        bubble_sort(plain)
        assert plain == [1, 2, 3]
        return value

    result = analyze(bubble_sort, [2, 1], key=key)
    assert result.metrics.comparisons == 1
    assert result.metrics.swaps == 1
    assert result.metrics.key_evaluations == 2


def test_exception_cleanup():
    def key(value):
        raise RuntimeError("bad key")

    with pytest.raises(RuntimeError, match="bad key"):
        analyze(bubble_sort, [2, 1], key=key)
    with pytest.raises(TypeError):
        analyze(bucket_sort, [1.5])
    assert analyze(bubble_sort, [2, 1]).metrics.comparisons == 1


def test_unsupported_algorithm():
    with pytest.raises(ValueError, match="supported"):
        analyze(sorted, [2, 1])


def test_metrics_are_frozen():
    metrics = analyze(bubble_sort, []).metrics
    with pytest.raises(FrozenInstanceError):
        metrics.comparisons = 1
