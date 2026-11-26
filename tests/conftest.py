"""Shared algorithm registries and fixtures."""

import pytest

from sortarium import (
    bubble_sort,
    bucket_sort,
    heap_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    selection_sort,
)

ALGORITHMS = (
    bubble_sort,
    bucket_sort,
    heap_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    selection_sort,
)
COMPARISON_ALGORITHMS = tuple(a for a in ALGORITHMS if a is not bucket_sort)
STABLE_ALGORITHMS = (bubble_sort, bucket_sort, insertion_sort, merge_sort)


@pytest.fixture(scope="session", params=ALGORITHMS, ids=lambda a: a.__name__)
def algorithm(request):
    return request.param


@pytest.fixture(scope="session", params=COMPARISON_ALGORITHMS, ids=lambda a: a.__name__)
def comparison_algorithm(request):
    return request.param


@pytest.fixture(scope="session", params=STABLE_ALGORITHMS, ids=lambda a: a.__name__)
def stable_algorithm(request):
    return request.param
