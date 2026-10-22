"""Heap sort: move the weakest remaining item to the end."""
from src.triage_record import comes_before


def heap_sort(arr, metrics=None, band_only=False, rule="standard"):
    """Build the heap in O(n), then sort in O(n log n). Extra space: O(1)."""
    n = len(arr)
    if n <= 1:
        return arr

    def _sift_down(root, size):
        current = root
        while True:
            left = 2 * current + 1
            right = 2 * current + 2
            worst_idx = current

            # Find the weakest item among the parent and its children.
            if left < size:
                if comes_before(arr[worst_idx], arr[left], metrics, band_only, rule):
                    worst_idx = left

            if right < size:
                if comes_before(arr[worst_idx], arr[right], metrics, band_only, rule):
                    worst_idx = right

            if worst_idx != current:
                arr[current], arr[worst_idx] = arr[worst_idx], arr[current]
                if metrics is not None:
                    metrics.moves += 2
                current = worst_idx
            else:
                break

    # 1. Build heap bottom-up in O(n)
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(i, n)

    # 2. Extract elements in O(n log n)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        if metrics is not None:
            metrics.moves += 2
        _sift_down(0, i)

    return arr
