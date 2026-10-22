"""Check the sorting and selection algorithms with Python's reference sort."""
import random
import unittest

from src.triage_record import TriageRecord, standard_key
from src.metrics import Metrics
from src.conditions import build_condition
from src.algorithms.insertion_sort import insertion_sort
from src.algorithms.merge_sort import merge_sort
from src.algorithms.quick_sort_naive import quick_sort_naive
from src.algorithms.quick_sort_hardened import quick_sort_hardened
from src.algorithms.heap_sort import heap_sort
from src.algorithms.top_k import MinHeapTopK, top_k_min_heap, top_k_bounded_buffer


FULL_SORT_ALGORITHMS = [
    ("Insertion Sort", insertion_sort),
    ("Merge Sort", merge_sort),
    ("Naive QuickSort", quick_sort_naive),
    ("Hardened QuickSort", quick_sort_hardened),
    ("Heap Sort", heap_sort),
]


def make_dummy_records(n, seed=2514):
    """Make repeatable test records without loading the CSV."""
    rng = random.Random(seed)
    records = []
    for i in range(1, n + 1):
        time = i * 10.0 + rng.uniform(-5, 5)
        amount = round(rng.uniform(1.0, 500.0), 2)
        risk = rng.uniform(1.0, 1000.0)
        band = rng.randint(0, 9)
        fraud = 0
        if rng.random() < 0.05:
            fraud = 1
        records.append(TriageRecord(i, time, amount, risk, band, fraud))
    return records


def record_ids(records):
    ids = []
    for record in records:
        ids.append(record.txn_id)
    return ids


class AlgorithmTests(unittest.TestCase):
    def test_empty_and_single_inputs(self):
        record = TriageRecord(1, 10, 50, 12, 3, 0)
        for name, algorithm in FULL_SORT_ALGORITHMS:
            with self.subTest(algorithm=name):
                assert algorithm([], Metrics()) == []
                assert algorithm([record], Metrics()) == [record]
        for selector in [top_k_min_heap, top_k_bounded_buffer]:
            assert selector([], 10) == []
            assert selector([record], 5) == [record]

    def test_equal_fields_use_row_id(self):
        records = []
        for i in range(1, 15):
            records.append(TriageRecord(i, 100, 50, 25, 4, 0))
        random.Random(42).shuffle(records)
        expected = sorted(records, key=standard_key)
        for name, algorithm in FULL_SORT_ALGORITHMS:
            with self.subTest(algorithm=name):
                result = algorithm(list(records))
                assert record_ids(result) == record_ids(expected)

    def test_every_condition_and_rule(self):
        records = make_dummy_records(100, seed=123)
        for condition in ["C1", "C2", "C3", "C4", "C5", "C6"]:
            data, band_only = build_condition(records, condition, seed=123)
            for rule in ["standard", "cr_freshness", "cr_risk"]:
                def reference_key(record):
                    if band_only:
                        return record.band_only_key()
                    return record.triage_key(rule)

                expected = sorted(data, key=reference_key)
                for name, algorithm in FULL_SORT_ALGORITHMS:
                    with self.subTest(condition=condition, rule=rule, algorithm=name):
                        metrics = Metrics()
                        result = algorithm(list(data), metrics, band_only, rule)
                        assert metrics.comparisons > 0
                        # Already sorted Lomuto input can need no swaps.
                        assert metrics.moves >= 0
                        assert sorted(record_ids(result)) == sorted(record_ids(data))
                        if band_only:
                            for index in range(1, len(result)):
                                assert result[index - 1].band >= result[index].band
                        else:
                            assert record_ids(result) == record_ids(expected)

    def test_top_k_matches_reference(self):
        records = make_dummy_records(100, seed=456)
        for rule in ["standard", "cr_freshness", "cr_risk"]:
            def reference_key(record):
                return record.triage_key(rule)

            ordered = sorted(records, key=reference_key)
            for k in [0, 1, 5, 10, 25, 50, 100, 150]:
                for selector in [top_k_min_heap, top_k_bounded_buffer]:
                    with self.subTest(rule=rule, k=k, selector=selector.__name__):
                        result = selector(records, k, Metrics(), rule=rule)
                        assert record_ids(result) == record_ids(ordered[:k])

    def test_stable_algorithms_keep_band_ties_in_arrival_order(self):
        records = make_dummy_records(50)
        for record in records:
            record.band = 4
        for algorithm in [insertion_sort, merge_sort]:
            result = algorithm(list(records), band_only=True)
            assert record_ids(result) == record_ids(records)

    def test_persistent_heap_can_publish_without_losing_records(self):
        records = make_dummy_records(60)
        heap = MinHeapTopK(10)
        seen = []
        for record in records:
            heap.insert(record)
            seen.append(record)
            expected = sorted(seen, key=standard_key)[:10]
            assert record_ids(heap.get_top_k_sorted()) == record_ids(expected)
            assert len(heap.heap) == min(10, len(seen))

    def test_recursive_quicksort_limit_and_iterative_fallback(self):
        records = sorted(make_dummy_records(1200, seed=999), key=standard_key)
        with self.assertRaises(RecursionError):
            quick_sort_naive(list(records), Metrics(), use_explicit_stack=False)
        for algorithm in [quick_sort_naive, quick_sort_hardened]:
            result = algorithm(list(records), Metrics())
            assert record_ids(result) == record_ids(records)

    def test_empty_conditions(self):
        for condition in ["C1", "C2", "C3", "C4", "C5", "C6"]:
            records, band_only = build_condition([], condition, seed=2514)
            assert records == []
            assert band_only == (condition == "C6")
