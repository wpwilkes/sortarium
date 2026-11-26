"""Implementation of quick sort."""

from collections.abc import Callable, MutableSequence, Sequence
from typing import Literal, TypeVar, overload

from ._metrics import Counters
from ._ordering import SupportsLessThan, make_precedes
from ._sorting import run_sort

T = TypeVar("T")


@overload
def quick_sort(
    sequence: MutableSequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: Literal[True] = True,
) -> None: ...


@overload
def quick_sort(
    sequence: Sequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: Literal[False],
) -> list[T]: ...


@overload
def quick_sort(
    sequence: MutableSequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: bool,
) -> list[T] | None: ...


def quick_sort(
    sequence: Sequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: bool = True,
) -> list[T] | None:
    """Sort a sequence using quick sort.

    Return None after mutating the sequence, or a new sorted list when
    inplace=False. Unstable; average O(n log n), worst O(n^2); O(log n) stack.
    """
    precedes = make_precedes(key, reverse)
    return run_sort(
        sequence,
        inplace,
        lambda data, metrics: _quick_sort(data, precedes, metrics),
    )


def _quick_sort(
    sequence: MutableSequence[T],
    precedes: Callable[[T, T], bool],
    metrics: Counters | None,
) -> None:
    def sort(lo: int, hi: int, depth: int) -> None:
        if metrics is not None:
            metrics.recursion_depth = max(metrics.recursion_depth, depth)
        while lo < hi:
            pivot = sequence[(lo + hi) // 2]
            left, i, right = lo, lo, hi
            while i <= right:
                if precedes(sequence[i], pivot):
                    sequence[left], sequence[i] = sequence[i], sequence[left]
                    if metrics is not None:
                        metrics.record_swap()
                    left += 1
                    i += 1
                elif precedes(pivot, sequence[i]):
                    sequence[i], sequence[right] = sequence[right], sequence[i]
                    if metrics is not None:
                        metrics.record_swap()
                    right -= 1
                else:
                    i += 1

            # Recurse only on the smaller partition.
            if left - lo < hi - right:
                sort(lo, left - 1, depth + 1)
                lo = right + 1
            else:
                sort(right + 1, hi, depth + 1)
                hi = left - 1

    sort(0, len(sequence) - 1, 1)
