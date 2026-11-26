# Sortarium

![CI](https://github.com/wpwilkes/sortarium/actions/workflows/python-package.yml/badge.svg?branch=develop)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-GPL--3.0-blue)

**A Laboratory for Sorting Algorithms**

Sortarium is an open-source Python library dedicated to the implementation, mathematical analysis, empirical benchmarking, and visualization of sorting algorithms.

## Features

### Current

- Classical sorting algorithm implementations
- In-place and non-in-place sorting interfaces
- Type annotations
- Automated testing

### Planned

- Algorithm instrumentation
- Empirical performance benchmarking
- Computational complexity analysis
- Input distribution generation
- Algorithm visualization
- Mathematical documentation

## Implemented Algorithms

| Algorithm | Paradigm |
|---|---|
| Bubble Sort | Exchange |
| Selection Sort | Selection |
| Insertion Sort | Insertion |
| Merge Sort | Divide and Conquer |
| Quick Sort | Divide and Conquer |
| Heap Sort | Selection |
| Bucket Sort | Distribution |

## Installation

Install directly from the repository:

```bash
git clone https://github.com/wpwilkes/sortarium.git
cd sortarium
pip install -e .
```

## Usage

```python
from sortarium import merge_sort

sequence = [5, 3, 8, 1, 2]

result = merge_sort(sequence, inplace=False)

print(result)
# [1, 2, 3, 5, 8]
```

## Algorithm Analysis

Sortarium provides an instrumentation framework for analyzing the computational behavior of sorting algorithms.

```python
from sortarium import analyze, insertion_sort

result = analyze(insertion_sort, [5, 3, 8, 1, 2])

print(result.output)
# [1, 2, 3, 5, 8]

print(result.metrics.comparisons)
# 9

print(result.metrics.writes)
# 11
```

The analysis framework records:

- Ordering comparisons
- Element swaps
- Primary sequence writes
- Auxiliary storage writes
- Key function evaluations
- Maximum recursion depth
- Instrumented execution time

Analysis is non-destructive and supports custom key functions and reverse ordering.

The collected metrics enable empirical investigation of algorithmic complexity and computational trade-offs.

## Empirical Benchmarking

Sortarium provides a framework for reproducible computational experiments comparing sorting algorithms across input sizes and distributions.

```python
from sortarium import benchmark, merge_sort, quick_sort

results = benchmark(
    algorithms=[merge_sort, quick_sort],
    sizes=[100, 500, 1000, 5000],
    distribution="uniform",
    trials=30,
    seed=42,
)

for row in results.summary("elapsed_time"):
    print(row.algorithm, row.input_size, row.median)

results.to_csv("benchmark.csv")
```

### Supported Input Distributions

- Uniform
- Normal
- Sorted
- Reverse
- Nearly sorted
- Few unique values

The benchmarking framework supports seeded input generation, paired experimental trials, preliminary warmup executions, independent timing and instrumentation measurements, descriptive statistics, and CSV export.

Each algorithm receives the same input sequence within a given experimental trial, allowing controlled comparisons of computational performance.

## Testing

```bash
python -m pip install pytest
python -m pytest
```

## Project Objectives

Sortarium aims to provide a reproducible computational environment for studying the correctness, complexity, and empirical performance of sorting algorithms.

The project is intended primarily for educational and experimental use rather than as a replacement for optimized production sorting libraries.

## License

Sortarium is distributed under the GNU General Public License v3.0. See [LICENSE](LICENSE) for details.
