"""Deterministic correctness checks against Python's reference sort."""

from itertools import product

import pytest


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize(
    "values",
    [
        (),
        (1,),
        (2, 1),
        (1, 2, 3, 4),
        (4, 3, 2, 1),
        (3, 3, 3),
        (2, 1, 2, 0, 1),
        (-3, 0, -1, 2),
        (-(10**100), 0, 10**100),
    ],
)
def test_reference_sort(algorithm, values, reverse):
    assert algorithm(values, reverse=reverse, inplace=False) == sorted(
        values, reverse=reverse
    )


@pytest.mark.parametrize("reverse", [False, True])
def test_exhaustive_small_sequences(algorithm, reverse):
    for n in range(6):
        for values in product(range(-2, 3), repeat=n):
            expected = sorted(values, reverse=reverse)
            data = list(values)
            assert algorithm(data, reverse=reverse, inplace=False) == expected
            assert data == list(values)
            assert algorithm(data, reverse=reverse) is None
            assert data == expected


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("values", [("z", "ab", "a"), (1.5, -2.0, 0.0, 1.5)])
def test_comparison_types(comparison_algorithm, values, reverse):
    assert comparison_algorithm(values, reverse=reverse, inplace=False) == sorted(
        values, reverse=reverse
    )


class LessThanOnly:
    """A comparable object with no value-based equality or other ordering."""

    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        return self.value < other.value


@pytest.mark.parametrize("reverse", [False, True])
def test_less_than_only(comparison_algorithm, reverse):
    data = [LessThanOnly(i) for i in (2, 1, 2, -1)]
    result = comparison_algorithm(data, reverse=reverse, inplace=False)
    assert [x.value for x in result] == sorted([2, 1, 2, -1], reverse=reverse)
    assert sorted(map(id, result)) == sorted(map(id, data))
