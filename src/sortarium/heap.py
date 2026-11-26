"""Implementation of heap sort."""

from collections.abc import Callable, MutableSequence, Sequence
from typing import Literal, TypeVar, overload

from ._metrics import Counters
from ._ordering import SupportsLessThan, make_precedes
from ._sorting import run_sort

T = TypeVar("T")


@overload
def heap_sort(
    sequence: MutableSequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: Literal[True] = True,
) -> None: ...


@overload
def heap_sort(
    sequence: Sequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: Literal[False],
) -> list[T]: ...


@overload
def heap_sort(
    sequence: MutableSequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: bool,
) -> list[T] | None: ...


def heap_sort(
    sequence: Sequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: bool = True,
) -> list[T] | None:
    """Sort a sequence using heap sort.

    Return None after mutating the sequence, or a new sorted list when
    inplace=False. Unstable; O(n log n) worst-case time and O(1) auxiliary space.
    """
    precedes = make_precedes(key, reverse)
    return run_sort(
        sequence,
        inplace,
        lambda data, metrics: _heap_sort(data, precedes, metrics),
    )


def _heap_sort(
    sequence: MutableSequence[T],
    precedes: Callable[[T, T], bool],
    metrics: Counters | None,
) -> None:
    def sift_down(root: int, end: int) -> None:
        while 2 * root + 1 < end:
            child = 2 * root + 1
            if child + 1 < end and precedes(sequence[child], sequence[child + 1]):
                child += 1
            if not precedes(sequence[root], sequence[child]):
                break
            sequence[root], sequence[child] = sequence[child], sequence[root]
            if metrics is not None:
                metrics.record_swap()
            root = child

    n = len(sequence)
    for root in range(n // 2 - 1, -1, -1):
        sift_down(root, n)
    for end in range(n - 1, 0, -1):
        sequence[0], sequence[end] = sequence[end], sequence[0]
        if metrics is not None:
            metrics.record_swap()
        sift_down(0, end)
