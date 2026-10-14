"""
Merge Sort implementation from scratch.
Uses simple, standard Python with zero external libraries.
Preallocates a single auxiliary buffer for high performance and stability.
"""
from src.triage_record import comes_before


def merge_sort(arr, metrics=None, band_only=False, rule="standard"):
    """
    Sorts arr using Divide-and-Conquer Merge Sort.
    
    Time Complexity:
      - Best, Worst, Average: O(n log n)
    Space Complexity:
      - O(n) auxiliary list buffer
    Stability:
      - Stable
    """
    n = len(arr)
    if n <= 1:
        return arr

    if metrics is not None:
        metrics.peak_extra_memory = max(metrics.peak_extra_memory, n)

    # Preallocate auxiliary buffer of size n
    aux = [None] * n

    def _merge(left, mid, right):
        i = left
        j = mid + 1
        k = left

        while i <= mid and j <= right:
            # For stability on equal keys: prefer arr[i] from left subarray
            if comes_before(arr[j], arr[i], metrics, band_only, rule):
                aux[k] = arr[j]
                j += 1
            else:
                aux[k] = arr[i]
                i += 1
            if metrics is not None:
                metrics.moves += 1
            k += 1

        while i <= mid:
            aux[k] = arr[i]
            if metrics is not None:
                metrics.moves += 1
            i += 1
            k += 1

        while j <= right:
            aux[k] = arr[j]
            if metrics is not None:
                metrics.moves += 1
            j += 1
            k += 1

        # Copy back merged items into arr
        for p in range(left, right + 1):
            arr[p] = aux[p]
            if metrics is not None:
                metrics.moves += 1

    def _sort(left, right):
        if left >= right:
            return
        mid = (left + right) // 2
        _sort(left, mid)
        _sort(mid + 1, right)
        _merge(left, mid, right)

    _sort(0, n - 1)
    return arr
