"""Implementation of insertion sort."""

from collections.abc import Callable, MutableSequence, Sequence
from typing import Literal, TypeVar, overload

from ._metrics import Counters
from ._ordering import SupportsLessThan, make_precedes
from ._sorting import run_sort

T = TypeVar("T")


@overload
def insertion_sort(
    sequence: MutableSequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: Literal[True] = True,
) -> None: ...


@overload
def insertion_sort(
    sequence: Sequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: Literal[False],
) -> list[T]: ...


@overload
def insertion_sort(
    sequence: MutableSequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: bool,
) -> list[T] | None: ...


def insertion_sort(
    sequence: Sequence[T],
    *,
    key: Callable[[T], SupportsLessThan] | None = None,
    reverse: bool = False,
    inplace: bool = True,
) -> list[T] | None:
    """Sort a sequence using insertion sort.

    Return None after mutating the sequence, or a new sorted list when
    inplace=False. Stable; best O(n), worst O(n^2).
    """
    precedes = make_precedes(key, reverse)
    return run_sort(
        sequence,
        inplace,
        lambda data, metrics: _insertion_sort(data, precedes, metrics),
    )


def _insertion_sort(
    sequence: MutableSequence[T],
    precedes: Callable[[T, T], bool],
    metrics: Counters | None,
) -> None:
    for i in range(1, len(sequence)):
        value = sequence[i]
        j = i
        while j > 0 and precedes(value, sequence[j - 1]):
            sequence[j] = sequence[j - 1]
            if metrics is not None:
                metrics.writes += 1
            j -= 1
        sequence[j] = value
        if metrics is not None:
            metrics.writes += 1
