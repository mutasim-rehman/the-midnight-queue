"""Keep only the best K records using a heap or a sorted list."""
from src.triage_record import comes_before


class MinHeapTopK:
    """The heap root is the weakest record currently kept."""
    def __init__(self, capacity, metrics=None, band_only=False, rule="standard"):
        self.capacity = capacity
        self.metrics = metrics
        self.band_only = band_only
        self.rule = rule
        self.heap = []

    def _is_weaker(self, a, b):
        """Return True if a has lower priority than b."""
        return comes_before(b, a, self.metrics, self.band_only, self.rule)

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
            # Replace the weakest survivor only if the new record is better.
            if comes_before(record, self.heap[0], self.metrics, self.band_only, self.rule):
                self.heap[0] = record
                if self.metrics is not None:
                    self.metrics.moves += 1
                self._sift_down(0)

    def get_top_k_sorted(self):
        """Return the kept records in rank order without changing the saved heap."""
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


def top_k_min_heap(arr, k, metrics=None, band_only=False, rule="standard"):
    """Select top K in O(n log K) time plus O(K log K) to order the result."""
    if k <= 0 or len(arr) == 0:
        return []
    k = min(k, len(arr))

    if metrics is not None:
        metrics.peak_extra_memory = max(metrics.peak_extra_memory, k)

    h = MinHeapTopK(k, metrics, band_only, rule)
    for record in arr:
        h.insert(record)
    return h.get_top_k_sorted()


def _binary_search_pos(buf, target, metrics, band_only, rule="standard"):
    """Find where target belongs, placing it after equal keys."""
    low = 0
    high = len(buf)
    while low < high:
        mid = (low + high) // 2
        if comes_before(target, buf[mid], metrics, band_only, rule):
            high = mid
        else:
            low = mid + 1
    return low


def top_k_bounded_buffer(arr, k, metrics=None, band_only=False, rule="standard"):
    """Keep a sorted list of at most K items. Worst time: O(n K)."""
    if k <= 0 or len(arr) == 0:
        return []
    k = min(k, len(arr))

    if metrics is not None:
        metrics.peak_extra_memory = max(metrics.peak_extra_memory, k)

    buf = []
    for record in arr:
        if len(buf) < k:
            pos = _binary_search_pos(buf, record, metrics, band_only, rule)
            buf.append(None)
            index = len(buf) - 1
            while index > pos:
                buf[index] = buf[index - 1]
                index -= 1
            buf[pos] = record
            if metrics is not None:
                metrics.moves += (len(buf) - pos)
        else:
            # Fast rejection test: compare with weakest item buf[-1]
            if comes_before(record, buf[-1], metrics, band_only, rule):
                pos = _binary_search_pos(buf[:-1], record, metrics, band_only, rule)
                buf.pop()
                buf.append(None)
                index = len(buf) - 1
                while index > pos:
                    buf[index] = buf[index - 1]
                    index -= 1
                buf[pos] = record
                if metrics is not None:
                    metrics.moves += (k - pos)

    return buf
