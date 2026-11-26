"""Shared input handling for sorting algorithms."""

from collections.abc import Callable, MutableSequence, Sequence
from typing import TypeVar

from ._metrics import Counters, active_metrics

T = TypeVar("T")


def run_sort(
    sequence: Sequence[T],
    inplace: bool,
    kernel: Callable[[MutableSequence[T], Counters | None], None],
) -> list[T] | None:
    """Run a mutating kernel on the original sequence or a copy."""
    if inplace:
        if not isinstance(sequence, MutableSequence):
            raise TypeError("In-place sorting requires a mutable sequence.")
        data = sequence
    else:
        data = list(sequence)

    metrics = active_metrics.get()
    if metrics is None:
        kernel(data, None)
    else:
        # Consume the collector for this call only. User-defined key functions
        # may themselves invoke a sort without contaminating our counters.
        token = active_metrics.set(None)
        try:
            kernel(data, metrics)
        finally:
            active_metrics.reset(token)

    if inplace:
        return None
    # The non-in-place branch constructed a list above.
    assert isinstance(data, list)
    return data
