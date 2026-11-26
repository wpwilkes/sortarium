"""Bucket sort's integer-key domain and allocation regressions."""

import pytest

from sortarium import bucket_sort


@pytest.mark.parametrize("reverse", [False, True])
def test_wide_integer_range(reverse):
    data = [-(10**100), 0, 10**100, 1, -1]
    assert bucket_sort(data, reverse=reverse, inplace=False) == sorted(
        data, reverse=reverse
    )


@pytest.mark.parametrize("inplace", [False, True])
@pytest.mark.parametrize("data", [[1.5], [1, "a"], [None]])
def test_invalid_values(data, inplace):
    original = data.copy()
    with pytest.raises(TypeError, match="integer-valued keys"):
        bucket_sort(data, inplace=inplace)
    assert data == original


def test_invalid_projected_key():
    data = ["a", "bb"]
    with pytest.raises(TypeError, match="integer-valued keys"):
        bucket_sort(data, key=lambda word: float(len(word)))
    assert data == ["a", "bb"]
