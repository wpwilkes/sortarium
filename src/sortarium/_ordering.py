from collections.abc import Callable
from typing import Any, Protocol, TypeVar, cast

from ._metrics import active_metrics

T = TypeVar("T")


class SupportsLessThan(Protocol):
    def __lt__(self, other: Any, /) -> bool: ...


def make_precedes(
    key: Callable[[T], SupportsLessThan] | None,
    reverse: bool,
) -> Callable[[T, T], bool]:
    """Construct a strict ordering predicate."""
    metrics = active_metrics.get()

    def project(value: T) -> SupportsLessThan:
        if key is None:
            return cast(SupportsLessThan, value)
        if metrics is not None:
            metrics.key_evaluations += 1
        return key(value)

    def precedes(left: T, right: T) -> bool:
        a, b = project(left), project(right)
        if metrics is not None:
            metrics.comparisons += 1
        return b < a if reverse else a < b

    return precedes
