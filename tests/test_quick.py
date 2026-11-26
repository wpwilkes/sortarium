"""Quicksort partition and recursion regressions."""

import pytest

from sortarium import quick_sort


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize(
    "data",
    [
        list(range(3000)),
        list(range(3000, 0, -1)),
        [1] * 3000,
        [i % 5 for i in range(3000)],
        list(range(1500)) + list(range(1500, 0, -1)),
    ],
    ids=["sorted", "reversed", "equal", "duplicates", "organ-pipe"],
)
def test_large_inputs(data, reverse):
    assert quick_sort(data, reverse=reverse, inplace=False) == sorted(
        data, reverse=reverse
    )
