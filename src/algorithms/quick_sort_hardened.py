"""
Hardened QuickSort implementation from scratch.
Uses simple, standard Python with zero external libraries.

Hardening mechanisms:
1. Median-of-Three pivot selection (defeats sorted/reverse inputs C3, C4, C5).
2. 3-Way Partitioning / Dutch National Flag (handles duplicates and C6 band-only in O(n)).
3. Tail-Call Optimization (recurses on smaller subarray first, bounding stack depth to O(log n) <= 20).
"""
from src.triage_record import comes_before


def _median_of_three(arr, low, high, metrics=None, band_only=False):
    """
    Selects median among arr[low], arr[mid], arr[high]
    and places it at index low to serve as the pivot.
    """
    mid = low + (high - low) // 2

    if comes_before(arr[mid], arr[low], metrics, band_only):
        arr[low], arr[mid] = arr[mid], arr[low]
        if metrics is not None:
            metrics.moves += 2

    if comes_before(arr[high], arr[low], metrics, band_only):
        arr[low], arr[high] = arr[high], arr[low]
        if metrics is not None:
            metrics.moves += 2

    if comes_before(arr[high], arr[mid], metrics, band_only):
        arr[mid], arr[high] = arr[high], arr[mid]
        if metrics is not None:
            metrics.moves += 2

    # Move median to low
    if mid != low:
        arr[low], arr[mid] = arr[mid], arr[low]
        if metrics is not None:
            metrics.moves += 2

    return low


def quick_sort_hardened(arr, metrics=None, band_only=False):
    """
    Hardened QuickSort with Median-of-Three, 3-Way Partitioning, and Tail-Recursion Loop.
    
    Time Complexity:
      - Best/Average: O(n log n)
      - Duplicate-Heavy (C6): O(n)
    Space Complexity:
      - O(log n) call stack (maximum ~19 frames for 284k records).
    """
    n = len(arr)
    if n <= 1:
        return arr

    def _sort(low, high):
        while low < high:
            if high - low >= 2:
                _median_of_three(arr, low, high, metrics, band_only)

            pivot = arr[low]
            lt = low
            gt = high
            i = low + 1

            # 3-Way Dutch National Flag partitioning
            while i <= gt:
                if comes_before(arr[i], pivot, metrics, band_only):
                    arr[lt], arr[i] = arr[i], arr[lt]
                    if metrics is not None:
                        metrics.moves += 2
                    lt += 1
                    i += 1
                elif comes_before(pivot, arr[i], metrics, band_only):
                    arr[i], arr[gt] = arr[gt], arr[i]
                    if metrics is not None:
                        metrics.moves += 2
                    gt -= 1
                else:
                    # Equal key
                    i += 1

            # Recurse on smaller subarray first to minimize stack depth
            left_size = lt - 1 - low
            right_size = high - (gt + 1)

            if left_size < right_size:
                if low < lt - 1:
                    _sort(low, lt - 1)
                low = gt + 1
            else:
                if gt + 1 < high:
                    _sort(gt + 1, high)
                high = lt - 1

    _sort(0, n - 1)
    return arr
