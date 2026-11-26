"""Implementation of selection sort."""

from collections.abc import Callable, MutableSequence, Sequence
from typing import Literal, TypeVar, overload

from ._metrics import Counters
from ._ordering import SupportsLessThan, make_precedes
from ._sorting import run_sort

T = TypeVar("T")


@overload
def selection_sort(
    sequence: MutableSequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: Literal[True] = True,
) -> None: ...


@overload
def selection_sort(
    sequence: Sequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: Literal[False],
) -> list[T]: ...


@overload
def selection_sort(
    sequence: MutableSequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: bool,
) -> list[T] | None: ...


def selection_sort(
    sequence: Sequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: bool = True,
) -> list[T] | None:
    """Sort a sequence using selection sort.

    Return None after mutating the sequence, or a new sorted list when
    inplace=False. Unstable; O(n^2) comparisons.
    """
    precedes = make_precedes(key, reverse)
    return run_sort(
        sequence,
        inplace,
        lambda data, metrics: _selection_sort(data, precedes, metrics),
    )


def _selection_sort(
    sequence: MutableSequence[T],
    precedes: Callable[[T, T], bool],
    metrics: Counters | None,
) -> None:
    n = len(sequence)
    for i in range(n - 1):
        best = i
        for j in range(i + 1, n):
            if precedes(sequence[j], sequence[best]):
                best = j
        if best != i:
            sequence[i], sequence[best] = sequence[best], sequence[i]
            if metrics is not None:
                metrics.record_swap()
