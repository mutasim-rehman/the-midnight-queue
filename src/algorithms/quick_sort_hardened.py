"""Quicksort with a middle-of-three pivot and three-way partition."""
from src.triage_record import comes_before


def _median_of_three(arr, low, high, metrics=None, band_only=False, rule="standard"):
    """Put the median of the first, middle, and last items at low."""
    mid = low + (high - low) // 2

    if comes_before(arr[mid], arr[low], metrics, band_only, rule):
        arr[low], arr[mid] = arr[mid], arr[low]
        if metrics is not None:
            metrics.moves += 2

    if comes_before(arr[high], arr[low], metrics, band_only, rule):
        arr[low], arr[high] = arr[high], arr[low]
        if metrics is not None:
            metrics.moves += 2

    if comes_before(arr[high], arr[mid], metrics, band_only, rule):
        arr[mid], arr[high] = arr[high], arr[mid]
        if metrics is not None:
            metrics.moves += 2

    # Move median to low
    if mid != low:
        arr[low], arr[mid] = arr[mid], arr[low]
        if metrics is not None:
            metrics.moves += 2

    return low


def quick_sort_hardened(arr, metrics=None, band_only=False, rule="standard"):
    """Average O(n log n), worst O(n squared). Smaller-side recursion uses O(log n) stack."""
    n = len(arr)
    if n <= 1:
        return arr

    def _sort(low, high):
        while low < high:
            if high - low >= 2:
                _median_of_three(arr, low, high, metrics, band_only, rule)

            pivot = arr[low]
            before_end = low
            after_start = high
            i = low + 1

            # Keep items before, equal to, and after the pivot in separate sections.
            while i <= after_start:
                if comes_before(arr[i], pivot, metrics, band_only, rule):
                    arr[before_end], arr[i] = arr[i], arr[before_end]
                    if metrics is not None:
                        metrics.moves += 2
                    before_end += 1
                    i += 1
                elif comes_before(pivot, arr[i], metrics, band_only, rule):
                    arr[i], arr[after_start] = arr[after_start], arr[i]
                    if metrics is not None:
                        metrics.moves += 2
                    after_start -= 1
                else:
                    # Equal key
                    i += 1

            # Recurse on the smaller side; handle the larger side in this loop.
            left_size = before_end - 1 - low
            right_size = high - (after_start + 1)

            if left_size < right_size:
                if low < before_end - 1:
                    _sort(low, before_end - 1)
                low = after_start + 1
            else:
                if after_start + 1 < high:
                    _sort(after_start + 1, high)
                high = before_end - 1

    _sort(0, n - 1)
    return arr
