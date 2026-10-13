"""
Insertion Sort implementation from scratch.
Uses simple, standard Python with zero external libraries.
"""
from src.triage_record import comes_before


def insertion_sort(arr, metrics=None, band_only=False):
    """
    Sorts arr in-place using Insertion Sort.
    
    Time Complexity:
      - Best (already sorted): O(n) comparisons, O(n) moves.
      - Worst (reverse sorted): O(n^2) comparisons, O(n^2) moves.
      - Average: O(n + I) where I is the number of inversions.
    Space Complexity:
      - O(1) auxiliary space (in-place).
    """
    n = len(arr)
    if n <= 1:
        return arr

    for i in range(1, n):
        key_item = arr[i]
        if metrics is not None:
            metrics.moves += 1

        j = i - 1
        while j >= 0:
            if comes_before(key_item, arr[j], metrics, band_only):
                arr[j + 1] = arr[j]
                if metrics is not None:
                    metrics.moves += 1
                j -= 1
            else:
                break

        arr[j + 1] = key_item
        if metrics is not None:
            metrics.moves += 1

    return arr
