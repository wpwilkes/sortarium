"""Compare sorting algorithms on shared random inputs."""

from sortarium import benchmark, heap_sort, merge_sort, quick_sort


def main() -> None:
    results = benchmark(
        algorithms=[merge_sort, quick_sort, heap_sort],
        sizes=[100, 500, 1000, 5000, 10000],
        distribution="uniform",
        trials=30,
        warmups=1,
        seed=42,
    )

    print(f"{'Algorithm':<16} {'Size':>8} {'Median (ms)':>14}")
    for row in results.summary():
        print(f"{row.algorithm:<16} {row.input_size:>8} {row.median * 1000:>14.3f}")

    results.to_csv("benchmark.csv")


if __name__ == "__main__":
    main()
