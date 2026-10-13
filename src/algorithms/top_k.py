"""
Top-K Selection Contenders from scratch.
Uses simple, standard Python with zero external libraries.

1. Size-K Min-Heap (O(n log K) time, O(K) space)
2. Bounded Insertion Buffer of size K (O(n) best-case comparisons, O(K) space)
"""
from src.triage_record import comes_before


class MinHeapTopK:
    """
    Min-Heap for Top-K selection.
    The root heap[0] holds the weakest survivor in the top K.
    """
    def __init__(self, capacity, metrics=None, band_only=False):
        self.capacity = capacity
        self.metrics = metrics
        self.band_only = band_only
        self.heap = []

    def _is_weaker(self, a, b):
        """Returns True if 'a' has lower triage priority than 'b'."""
        return comes_before(b, a, self.metrics, self.band_only)

    def _sift_up(self, idx):
        current = idx
        while current > 0:
            parent = (current - 1) // 2
            if self._is_weaker(self.heap[current], self.heap[parent]):
                self.heap[current], self.heap[parent] = self.heap[parent], self.heap[current]
                if self.metrics is not None:
                    self.metrics.moves += 2
                current = parent
            else:
                break

    def _sift_down(self, idx):
        size = len(self.heap)
        current = idx
        while True:
            left = 2 * current + 1
            right = 2 * current + 2
            weakest = current

            if left < size and self._is_weaker(self.heap[left], self.heap[weakest]):
                weakest = left
            if right < size and self._is_weaker(self.heap[right], self.heap[weakest]):
                weakest = right

            if weakest != current:
                self.heap[current], self.heap[weakest] = self.heap[weakest], self.heap[current]
                if self.metrics is not None:
                    self.metrics.moves += 2
                current = weakest
            else:
                break

    def insert(self, record):
        if len(self.heap) < self.capacity:
            self.heap.append(record)
            if self.metrics is not None:
                self.metrics.moves += 1
            self._sift_up(len(self.heap) - 1)
        else:
            # If incoming record beats root (weakest survivor):
            if comes_before(record, self.heap[0], self.metrics, self.band_only):
                self.heap[0] = record
                if self.metrics is not None:
                    self.metrics.moves += 1
                self._sift_down(0)

    def get_top_k_sorted(self):
        """Extracts elements and returns them sorted from rank 1 to rank K."""
        k = len(self.heap)
        result = [None] * k
        heap_copy = list(self.heap)
        orig_heap = self.heap
        self.heap = heap_copy

        for i in range(k - 1, -1, -1):
            result[i] = self.heap[0]
            if self.metrics is not None:
                self.metrics.moves += 1
            last_elem = self.heap.pop()
            if len(self.heap) > 0:
                self.heap[0] = last_elem
                if self.metrics is not None:
                    self.metrics.moves += 1
                self._sift_down(0)

        self.heap = orig_heap
        return result


def top_k_min_heap(arr, k, metrics=None, band_only=False):
    """Selects top K elements using a size-K Min-Heap."""
    if k <= 0 or len(arr) == 0:
        return []
    k = min(k, len(arr))

    if metrics is not None:
        metrics.peak_extra_memory = max(metrics.peak_extra_memory, k)

    h = MinHeapTopK(k, metrics, band_only)
    for record in arr:
        h.insert(record)
    return h.get_top_k_sorted()


def _binary_search_pos(buf, target, metrics, band_only):
    """Finds insertion position for target in sorted buf."""
    low = 0
    high = len(buf)
    while low < high:
        mid = (low + high) // 2
        if comes_before(target, buf[mid], metrics, band_only):
            high = mid
        else:
            low = mid + 1
    return low


def top_k_bounded_buffer(arr, k, metrics=None, band_only=False):
    """Selects top K elements using a bounded sorted list of capacity K."""
    if k <= 0 or len(arr) == 0:
        return []
    k = min(k, len(arr))

    if metrics is not None:
        metrics.peak_extra_memory = max(metrics.peak_extra_memory, k)

    buf = []
    for record in arr:
        if len(buf) < k:
            pos = _binary_search_pos(buf, record, metrics, band_only)
            buf.insert(pos, record)
            if metrics is not None:
                metrics.moves += (len(buf) - pos)
        else:
            # Fast rejection test: compare with weakest item buf[-1]
            if comes_before(record, buf[-1], metrics, band_only):
                pos = _binary_search_pos(buf[:-1], record, metrics, band_only)
                buf.pop()
                buf.insert(pos, record)
                if metrics is not None:
                    metrics.moves += (k - pos)

    return buf
