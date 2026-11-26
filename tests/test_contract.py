"""Verify common public sorting API semantics."""

from collections import UserList

import pytest


@pytest.mark.parametrize("values", [[], [1], [3, 1, 2]])
@pytest.mark.parametrize("reverse", [False, True])
def test_inplace(algorithm, values, reverse):
    data = list(values)
    alias = data
    result = algorithm(data, reverse=reverse)
    assert result is None
    assert alias == sorted(values, reverse=reverse)


@pytest.mark.parametrize("values", [[], [1], [3, 1, 2]])
@pytest.mark.parametrize("reverse", [False, True])
def test_non_inplace(algorithm, values, reverse):
    data = list(values)
    result = algorithm(data, reverse=reverse, inplace=False)
    assert type(result) is list
    assert result is not data
    assert data == values
    assert result == sorted(values, reverse=reverse)


def test_immutable_input(algorithm):
    assert algorithm((3, 1, 2), inplace=False) == [1, 2, 3]
    with pytest.raises(TypeError, match="mutable sequence"):
        algorithm((3, 1, 2))


def test_mutable_sequence(algorithm):
    data = UserList([3, 1, 2])
    assert algorithm(data, inplace=True) is None
    assert data == [1, 2, 3]
    result = algorithm(data, inplace=False, reverse=True)
    assert type(result) is list
    assert result == [3, 2, 1]
    assert data == [1, 2, 3]


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("inplace", [False, True])
def test_key_function(algorithm, reverse, inplace):
    original = [("a", 2), ("b", -1), ("c", 2), ("d", 0)]
    data = original.copy()

    def key(item):
        return item[1]

    result = algorithm(data, key=key, reverse=reverse, inplace=inplace)
    if inplace:
        assert result is None
        output = data
    else:
        assert result is not data
        assert data == original
        output = result
    assert sorted(map(id, output)) == sorted(map(id, original))
    assert list(map(key, output)) == sorted(map(key, original), reverse=reverse)


def test_keyword_only_options(algorithm):
    with pytest.raises(TypeError):
        algorithm([3, 1, 2], False)
