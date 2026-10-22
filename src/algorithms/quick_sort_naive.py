"""Quicksort with the last item as pivot. Sorted inputs can take O(n squared)."""
from src.triage_record import comes_before


def _lomuto_partition(arr, low, high, metrics=None, band_only=False, rule="standard"):
    """Move items that rank before the pivot to the left. Return the pivot index."""
    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if comes_before(arr[j], pivot, metrics, band_only, rule):
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


def quick_sort_naive(arr, metrics=None, band_only=False, rule="standard", use_explicit_stack=True):
    """Use a list of pending ranges, or recursion to demonstrate its depth limit."""
    n = len(arr)
    if n <= 1:
        return arr

    if not use_explicit_stack:
        # This version can hit Python's recursion limit.
        def _recursive_qs(low, high):
            if low < high:
                p = _lomuto_partition(arr, low, high, metrics, band_only, rule)
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

    # Save ranges in a list instead of using recursive calls.
    stack = [(0, n - 1)]
    while len(stack) > 0:
        low, high = stack.pop()
        if low < high:
            p = _lomuto_partition(arr, low, high, metrics, band_only, rule)
            stack.append((low, p - 1))
            stack.append((p + 1, high))

    return arr

