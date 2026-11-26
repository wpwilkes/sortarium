"""Deterministic stability checks, including descending order."""

from operator import itemgetter

import pytest


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("inplace", [False, True])
@pytest.mark.parametrize("keys", [(2, 1, 2, 1, 0), (3, 3, 3, 3)])
def test_stability(stable_algorithm, keys, inplace, reverse):
    original = list(enumerate(keys))
    data = original.copy()
    key = itemgetter(1)
    expected = sorted(original, key=key, reverse=reverse)
    result = stable_algorithm(data, key=key, reverse=reverse, inplace=inplace)
    if inplace:
        assert result is None
        assert data == expected
    else:
        assert result == expected
        assert data == original
