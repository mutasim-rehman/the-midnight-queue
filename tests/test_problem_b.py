"""
Comprehensive test suite for Problem B: Build the Contenders.
Tests all 5 full-sort algorithms and both Top-K selectors against Python's sorted() oracle.

Requirements tested:
1. Empty input
2. Single record
3. All-equal keys
4. Duplicate-heavy input
5. Bit-for-bit output identity on total order
6. All 6 input conditions (C1 to C6)
7. Recursion depth failure documentation and handling
"""
import pytest
import copy
import random
from typing import List

from src.triage_record import TriageRecord, comes_before
from src.metrics import Metrics
from src.algorithms.insertion_sort import insertion_sort
from src.algorithms.merge_sort import merge_sort
from src.algorithms.quick_sort_naive import quick_sort_naive
from src.algorithms.quick_sort_hardened import quick_sort_hardened
from src.algorithms.heap_sort import heap_sort
from src.algorithms.top_k import top_k_min_heap, top_k_bounded_buffer
from src.conditions import build_condition


def make_dummy_records(n: int, seed: int = 2514) -> List[TriageRecord]:
    """Generates synthetic TriageRecord data for fast, reproducible testing."""
    rng = random.Random(seed)
    records = []
    for i in range(1, n + 1):
        records.append(
            TriageRecord(
                txn_id=i,
                Time=float(i * 10.0 + rng.uniform(-5, 5)),
                Amount=round(rng.uniform(1.0, 500.0), 2),
                risk=rng.uniform(1.0, 1000.0),
                band=rng.randint(0, 9),
                Class=1 if rng.random() < 0.05 else 0
            )
        )
    return records


FULL_SORT_ALGORITHMS = [
    ("Insertion Sort", insertion_sort),
    ("Merge Sort", merge_sort),
    ("Naive QuickSort (Iterative)", lambda arr, metrics=None, band_only=False: quick_sort_naive(arr, metrics, band_only, use_explicit_stack=True)),
    ("Hardened QuickSort", quick_sort_hardened),
    ("Heap Sort", heap_sort),
]


# --------------------------------------------------------------------------
# 1. Edge Case Tests: Empty Input
# --------------------------------------------------------------------------
@pytest.mark.parametrize("name, algo", FULL_SORT_ALGORITHMS)
def test_empty_input_full_sort(name, algo):
    arr = []
    metrics = Metrics()
    res = algo(arr, metrics, False)
    assert res == []
    assert len(res) == 0


def test_empty_input_top_k():
    arr = []
    metrics = Metrics()
    assert top_k_min_heap(arr, 10, metrics, False) == []
    assert top_k_bounded_buffer(arr, 10, metrics, False) == []


# --------------------------------------------------------------------------
# 2. Edge Case Tests: Single Record
# --------------------------------------------------------------------------
@pytest.mark.parametrize("name, algo", FULL_SORT_ALGORITHMS)
def test_single_record_full_sort(name, algo):
    rec = TriageRecord(txn_id=1, Time=10.0, Amount=50.0, risk=12.0, band=3, Class=0)
    arr = [rec]
    metrics = Metrics()
    res = algo(arr, metrics, False)
    assert len(res) == 1
    assert res[0].txn_id == 1


def test_single_record_top_k():
    rec = TriageRecord(txn_id=1, Time=10.0, Amount=50.0, risk=12.0, band=3, Class=0)
    arr = [rec]
    metrics = Metrics()
    res_heap = top_k_min_heap(arr, 5, metrics, False)
    res_buf = top_k_bounded_buffer(arr, 5, metrics, False)
    assert len(res_heap) == 1 and res_heap[0].txn_id == 1
    assert len(res_buf) == 1 and res_buf[0].txn_id == 1


# --------------------------------------------------------------------------
# 3. Edge Case Tests: All-Equal Keys
# --------------------------------------------------------------------------
@pytest.mark.parametrize("name, algo", FULL_SORT_ALGORITHMS)
def test_all_equal_keys_full_sort(name, algo):
    # Equal band, Amount, Time (different txn_id breaks ties)
    records = [
        TriageRecord(txn_id=i, Time=100.0, Amount=50.0, risk=25.0, band=4, Class=0)
        for i in range(1, 15)
    ]
    random.Random(42).shuffle(records)
    oracle = sorted(records, key=lambda r: r.triage_key())

    metrics = Metrics()
    res = algo(list(records), metrics, False)
    assert [r.txn_id for r in res] == [r.txn_id for r in oracle]


# --------------------------------------------------------------------------
# 4. Edge Case Tests: Duplicate-Heavy Keys (C6 Band-Only Simulation)
# --------------------------------------------------------------------------
@pytest.mark.parametrize("name, algo", FULL_SORT_ALGORITHMS)
def test_duplicate_heavy_band_only(name, algo):
    # Only 3 distinct bands (0, 1, 2) across 50 records
    records = [
        TriageRecord(txn_id=i, Time=float(i), Amount=10.0, risk=1.0, band=i % 3, Class=0)
        for i in range(1, 51)
    ]
    metrics = Metrics()
    res = algo(list(records), metrics, band_only=True)
    
    # In band_only descending: band values must be non-increasing
    bands = [r.band for r in res]
    assert bands == sorted(bands, reverse=True)


# --------------------------------------------------------------------------
# 5. Total Order Identity Test on Random Inputs
# --------------------------------------------------------------------------
@pytest.mark.parametrize("name, algo", FULL_SORT_ALGORITHMS)
def test_total_order_identity(name, algo):
    records = make_dummy_records(100, seed=123)
    oracle = sorted(records, key=lambda r: r.triage_key())

    metrics = Metrics()
    res = algo(list(records), metrics, False)

    # Must be bit-for-bit identical to oracle
    assert [r.txn_id for r in res] == [r.txn_id for r in oracle]
    # Metrics must have counted positive comparisons and moves
    assert metrics.comparisons > 0
    assert metrics.moves > 0


# --------------------------------------------------------------------------
# 6. Top-K Correctness: Identical to Oracle[:K]
# --------------------------------------------------------------------------
@pytest.mark.parametrize("k", [1, 5, 10, 25, 50])
def test_top_k_selection_matches_oracle(k):
    records = make_dummy_records(100, seed=456)
    oracle_top_k = sorted(records, key=lambda r: r.triage_key())[:k]
    expected_ids = [r.txn_id for r in oracle_top_k]

    metrics_heap = Metrics()
    res_heap = top_k_min_heap(list(records), k, metrics_heap, False)
    assert [r.txn_id for r in res_heap] == expected_ids

    metrics_buf = Metrics()
    res_buf = top_k_bounded_buffer(list(records), k, metrics_buf, False)
    assert [r.txn_id for r in res_buf] == expected_ids


# --------------------------------------------------------------------------
# 7. Verification Across All 6 Input Conditions (C1 to C6)
# --------------------------------------------------------------------------
@pytest.mark.parametrize("cond_id", ["C1", "C2", "C3", "C4", "C5", "C6"])
def test_conditions_with_hardened_quick_sort(cond_id):
    base_records = make_dummy_records(60, seed=789)
    cond_records, band_only = build_condition(base_records, cond_id, seed=789)

    metrics = Metrics()
    res = quick_sort_hardened(list(cond_records), metrics, band_only)

    if not band_only:
        oracle = sorted(cond_records, key=lambda r: r.triage_key())
        assert [r.txn_id for r in res] == [r.txn_id for r in oracle]
    else:
        bands = [r.band for r in res]
        assert bands == sorted(bands, reverse=True)


# --------------------------------------------------------------------------
# 8. Recursion Depth Failure Handling & Documentation
# --------------------------------------------------------------------------
def test_naive_quick_sort_recursion_depth_handling():
    """
    Documents and verifies that:
    1. Native recursive Naive QuickSort fails with RecursionError on large sorted inputs.
    2. Explicit-stack iterative Naive QuickSort succeeds on the exact same input.
    """
    # Size 1200 exceeds Python's default recursion limit (1000)
    sorted_records = make_dummy_records(1200, seed=999)
    sorted_records.sort(key=lambda r: r.triage_key())

    # 1. Recursive version MUST raise RecursionError as documented
    with pytest.raises(RecursionError) as exc_info:
        quick_sort_naive(list(sorted_records), Metrics(), band_only=False, use_explicit_stack=False)
    assert "RecursionError" in str(exc_info.value) or "call stack depth" in str(exc_info.value)

    # 2. Iterative version succeeds safely
    metrics = Metrics()
    res = quick_sort_naive(list(sorted_records), metrics, band_only=False, use_explicit_stack=True)
    assert len(res) == 1200
    assert [r.txn_id for r in res] == [r.txn_id for r in sorted_records]

    # 3. Hardened QuickSort easily handles it recursively because stack depth is O(log n)
    metrics_hard = Metrics()
    res_hard = quick_sort_hardened(list(sorted_records), metrics_hard, band_only=False)
    assert len(res_hard) == 1200
    assert [r.txn_id for r in res_hard] == [r.txn_id for r in sorted_records]
