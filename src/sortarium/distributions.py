"""Reproducible integer input models for sorting experiments."""

from random import Random
from typing import Literal

Distribution = Literal[
    "uniform", "normal", "sorted", "reverse", "nearly_sorted", "few_unique"
]
DISTRIBUTIONS = (
    "uniform",
    "normal",
    "sorted",
    "reverse",
    "nearly_sorted",
    "few_unique",
)


def generate_input(size: int, distribution: Distribution, rng: Random) -> list[int]:
    """Generate integer data using the caller's random number generator.

    Uniform: discrete uniform on [-size, size]. Normal: rounded normal with
    mean zero and standard deviation max(1, size / 6). Sorted/reverse:
    distinct integers in ascending/descending order. Nearly sorted: start
    with ascending integers and make max(1, size // 20) random adjacent
    exchanges if size >= 2. Few unique: uniform on {-2, -1, 0, 1, 2}.
    """
    if type(size) is not int or size < 0:
        raise ValueError("size must be a nonnegative integer")
    if distribution == "uniform":
        return [rng.randint(-size, size) for _ in range(size)]
    if distribution == "normal":
        return [round(rng.gauss(0, max(1, size / 6))) for _ in range(size)]
    if distribution == "sorted":
        return list(range(size))
    if distribution == "reverse":
        return list(range(size - 1, -1, -1))
    if distribution == "nearly_sorted":
        data = list(range(size))
        if size >= 2:
            for _ in range(max(1, size // 20)):
                i = rng.randrange(size - 1)
                data[i], data[i + 1] = data[i + 1], data[i]
        return data
    if distribution == "few_unique":
        return [rng.randint(-2, 2) for _ in range(size)]
    raise ValueError(f"Unknown distribution: {distribution!r}")
