"""Implementation of bucket sort."""

from collections.abc import Callable, MutableSequence, Sequence
from typing import Literal, TypeVar, overload

from ._metrics import Counters
from ._sorting import run_sort

T = TypeVar("T")


@overload
def bucket_sort(
    sequence: MutableSequence[T],
    *,
    key: Callable[[T], int] | None = None,
    reverse: bool = False,
    inplace: Literal[True] = True,
) -> None: ...


@overload
def bucket_sort(
    sequence: Sequence[T],
    *,
    key: Callable[[T], int] | None = None,
    reverse: bool = False,
    inplace: Literal[False],
) -> list[T]: ...


@overload
def bucket_sort(
    sequence: MutableSequence[T],
    *,
    key: Callable[[T], int] | None = None,
    reverse: bool = False,
    inplace: bool,
) -> list[T] | None: ...


def bucket_sort(
    sequence: Sequence[T],
    *,
    key: Callable[[T], int] | None = None,
    reverse: bool = False,
    inplace: bool = True,
) -> list[T] | None:
    """Sort a sequence using bucket sort.

    Return None after mutating the sequence, or a new sorted list when
    inplace=False. Stable; expected O(n) for well-distributed keys, worst O(n^2); O(n) auxiliary space.
    """
    return run_sort(
        sequence,
        inplace,
        lambda data, metrics: _bucket_sort(data, key, reverse, metrics),
    )


def _bucket_sort(
    sequence: MutableSequence[T],
    key: Callable[[T], int] | None,
    reverse: bool,
    metrics: Counters | None,
) -> None:
    pairs: list[tuple[int, T]] = []
    for value in sequence:
        if key is not None and metrics is not None:
            metrics.key_evaluations += 1
        projected = value if key is None else key(value)
        if not isinstance(projected, int):
            raise TypeError("Bucket sort requires integer-valued keys.")
        pairs.append((projected, value))
        if metrics is not None:
            metrics.auxiliary_writes += 1

    n = len(pairs)
    if n < 2:
        return
    low = min(k for k, _ in pairs)
    high = max(k for k, _ in pairs)
    if metrics is not None:
        # Each min/max pass compares n - 1 integer keys.
        metrics.comparisons += 2 * (n - 1)
    span = high - low + 1
    buckets: list[list[tuple[int, T]]] = [[] for _ in range(n)]
    for k, value in pairs:
        index = (k - low) * n // span
        buckets[index].append((k, value))
        if metrics is not None:
            metrics.auxiliary_writes += 1

    # Stable insertion sort within each bucket.
    for bucket in buckets:
        for i in range(1, len(bucket)):
            item = bucket[i]
            j = i
            while j > 0:
                previous = bucket[j - 1][0]
                comes_first = item[0] > previous if reverse else item[0] < previous
                if metrics is not None:
                    metrics.comparisons += 1
                if not comes_first:
                    break
                bucket[j] = bucket[j - 1]
                if metrics is not None:
                    metrics.auxiliary_writes += 1
                j -= 1
            bucket[j] = item
            if metrics is not None:
                metrics.auxiliary_writes += 1

    index = 0
    ordered = reversed(buckets) if reverse else iter(buckets)
    for bucket in ordered:
        for _, value in bucket:
            sequence[index] = value
            if metrics is not None:
                metrics.writes += 1
            index += 1
