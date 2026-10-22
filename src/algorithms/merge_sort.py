"""Merge sort: sort two halves, then join them using one extra list."""
from src.triage_record import comes_before


def merge_sort(arr, metrics=None, band_only=False, rule="standard"):
    """Stable. Time: O(n log n). Extra space: O(n)."""
    n = len(arr)
    if n <= 1:
        return arr

    if metrics is not None:
        metrics.peak_extra_memory = max(metrics.peak_extra_memory, n)

    # Reuse this list for every merge.
    aux = [None] * n

    def _merge(left, mid, right):
        i = left
        j = mid + 1
        k = left

        while i <= mid and j <= right:
            # Take the left item on ties to keep the sort stable.
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

        # Copy the joined section back.
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
