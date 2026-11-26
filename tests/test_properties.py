"""Property-based tests for sorting invariants."""

import itertools
from collections import Counter
from operator import itemgetter

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

VALUES = st.lists(st.integers(), max_size=64)
KEYS = st.lists(st.integers(-5, 5), max_size=64)


@pytest.mark.parametrize("reverse", [False, True])
@settings(max_examples=100, deadline=None)
@given(values=VALUES)
def test_ordering(algorithm, reverse, values):
    output = algorithm(values, reverse=reverse, inplace=False)
    pairs = itertools.pairwise(output)
    if reverse:
        assert all(a >= b for a, b in pairs)
    else:
        assert all(a <= b for a, b in pairs)


@settings(max_examples=100, deadline=None)
@given(values=VALUES, reverse=st.booleans())
def test_permutation(algorithm, values, reverse):
    output = algorithm(values, reverse=reverse, inplace=False)
    assert Counter(output) == Counter(values)


@settings(max_examples=100, deadline=None)
@given(values=VALUES, reverse=st.booleans())
def test_idempotence(algorithm, values, reverse):
    first = algorithm(values, reverse=reverse, inplace=False)
    second = algorithm(first, reverse=reverse, inplace=False)
    assert second == first


@settings(max_examples=100, deadline=None)
@given(values=VALUES, reverse=st.booleans())
def test_reference_and_mutation(algorithm, values, reverse):
    original = values.copy()
    expected = sorted(original, reverse=reverse)
    result = algorithm(values, reverse=reverse, inplace=False)
    assert type(result) is list
    assert result == expected
    assert result is not values
    assert values == original
    data = original.copy()
    assert algorithm(data, reverse=reverse, inplace=True) is None
    assert data == expected


@pytest.mark.parametrize("inplace", [False, True])
@settings(max_examples=100, deadline=None)
@given(keys=KEYS, reverse=st.booleans())
def test_key_order_and_identity(algorithm, inplace, keys, reverse):
    original = list(enumerate(keys))
    data = original.copy()
    key = itemgetter(1)
    result = algorithm(data, key=key, reverse=reverse, inplace=inplace)
    if inplace:
        assert result is None
        output = data
    else:
        assert data == original
        assert result is not data
        output = result
    assert Counter(map(id, output)) == Counter(map(id, original))
    assert list(map(key, output)) == sorted(keys, reverse=reverse)


@pytest.mark.parametrize("inplace", [False, True])
@pytest.mark.parametrize("reverse", [False, True])
@settings(max_examples=100, deadline=None)
@given(keys=KEYS)
def test_stable_keys(stable_algorithm, inplace, reverse, keys):
    original = list(enumerate(keys))
    data = original.copy()
    key = itemgetter(1)
    expected = sorted(original, key=key, reverse=reverse)
    result = stable_algorithm(data, key=key, reverse=reverse, inplace=inplace)
    if inplace:
        assert result is None
        assert data == expected
    else:
        assert data == original
        assert result == expected
