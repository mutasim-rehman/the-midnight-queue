"""Insertion sort: insert each item into the sorted part on its left."""
from src.triage_record import comes_before


def insertion_sort(arr, metrics=None, band_only=False, rule="standard"):
    """Stable, in place. Time: O(n + inversions). Extra space: O(1)."""
    n = len(arr)
    if n <= 1:
        return arr

    # The part before i is already sorted.
    for i in range(1, n):
        key_item = arr[i]
        if metrics is not None:
            metrics.moves += 1

        # Make room by shifting lower-priority items right.
        j = i - 1
        while j >= 0:
            if comes_before(key_item, arr[j], metrics, band_only, rule):
                arr[j + 1] = arr[j]
                if metrics is not None:
                    metrics.moves += 1
                j -= 1
            else:
                break

        # Put the saved item in the gap.
        arr[j + 1] = key_item
        if metrics is not None:
            metrics.moves += 1

    return arr

