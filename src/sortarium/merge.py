"""Implementation of merge sort."""

from collections.abc import Callable, MutableSequence, Sequence
from typing import Literal, TypeVar, overload

from ._metrics import Counters
from ._ordering import SupportsLessThan, make_precedes
from ._sorting import run_sort

T = TypeVar("T")


@overload
def merge_sort(
    sequence: MutableSequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: Literal[True] = True,
) -> None: ...


@overload
def merge_sort(
    sequence: Sequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: Literal[False],
) -> list[T]: ...


@overload
def merge_sort(
    sequence: MutableSequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: bool,
) -> list[T] | None: ...


def merge_sort(
    sequence: Sequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: bool = True,
) -> list[T] | None:
    """Sort a sequence using merge sort.

    Return None after mutating the sequence, or a new sorted list when
    inplace=False. Stable; O(n log n) time, O(n) auxiliary space.
    """
    precedes = make_precedes(key, reverse)
    return run_sort(
        sequence,
        inplace,
        lambda data, metrics: _merge_sort(data, precedes, metrics),
    )


def _merge_sort(
    sequence: MutableSequence[T],
    precedes: Callable[[T, T], bool],
    metrics: Counters | None,
) -> None:
    buffer = list(sequence)
    if metrics is not None:
        metrics.auxiliary_writes += len(buffer)

    def sort(lo: int, hi: int, depth: int) -> None:
        if metrics is not None:
            metrics.recursion_depth = max(metrics.recursion_depth, depth)
        if hi - lo < 2:
            return
        mid = (lo + hi) // 2
        sort(lo, mid, depth + 1)
        sort(mid, hi, depth + 1)

        i, j = lo, mid
        for k in range(lo, hi):
            if i == mid or (j < hi and precedes(sequence[j], sequence[i])):
                buffer[k] = sequence[j]
                j += 1
            else:
                buffer[k] = sequence[i]
                i += 1
            if metrics is not None:
                metrics.auxiliary_writes += 1
        for k in range(lo, hi):
            sequence[k] = buffer[k]
            if metrics is not None:
                metrics.writes += 1

    sort(0, len(sequence), 1)
