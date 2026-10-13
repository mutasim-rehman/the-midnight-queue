"""
Naive QuickSort implementation from scratch.
Uses Lomuto partition scheme with the last element as pivot.
Uses simple, standard Python with zero external libraries.

Failure & Crash Handling:
- On sorted (C3) or reverse-sorted (C4) arrays, Lomuto with last element pivot
  creates an unbalanced recursion tree of depth n.
- In Python, this crashes with RecursionError when n >= 1000.
- Handling: We support both native recursion (which triggers and documents RecursionError)
  and an explicit list-based stack (which avoids Python's call stack limit, allowing
  the algorithm to run up to the 5-minute DNF threshold).
"""
from src.triage_record import comes_before


def _lomuto_partition(arr, low, high, metrics=None, band_only=False):
    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if comes_before(arr[j], pivot, metrics, band_only):
            i += 1
            if i != j:
                arr[i], arr[j] = arr[j], arr[i]
                if metrics is not None:
                    metrics.moves += 2

    if i + 1 != high:
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        if metrics is not None:
            metrics.moves += 2

    return i + 1


def quick_sort_naive(arr, metrics=None, band_only=False, use_explicit_stack=True):
    """
    Naive QuickSort using Lomuto partition with last element as pivot.
    
    Time Complexity:
      - Best/Average: O(n log n)
      - Worst: O(n^2)
    Space Complexity:
      - O(n) call stack or explicit stack in worst case.
    """
    n = len(arr)
    if n <= 1:
        return arr

    if not use_explicit_stack:
        # Recursive version to demonstrate call-stack crash on large sorted data
        def _recursive_qs(low, high):
            if low < high:
                p = _lomuto_partition(arr, low, high, metrics, band_only)
                _recursive_qs(low, p - 1)
                _recursive_qs(p + 1, high)

        try:
            _recursive_qs(0, n - 1)
        except RecursionError as e:
            if metrics is not None:
                metrics.dnf = True
            raise RecursionError(
                f"Naive QuickSort crashed with RecursionError on size n={n}. "
                "Lomuto partition on sorted data degrades to O(n) call-stack depth."
            ) from e
        return arr

    # Iterative version using a simple Python list as a stack
    stack = [(0, n - 1)]
    while len(stack) > 0:
        low, high = stack.pop()
        if low < high:
            p = _lomuto_partition(arr, low, high, metrics, band_only)
            stack.append((low, p - 1))
            stack.append((p + 1, high))

    return arr
