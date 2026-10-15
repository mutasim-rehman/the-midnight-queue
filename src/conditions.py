"""
Input condition generators (C1 through C6) and subsampling pipeline (Section 3.3 and 3.4).
"""
import random
from src.triage_record import TriageRecord


def subsample_records(full_records, n, seed):
    """
    Subsamples size n uniformly without replacement using seed s,
    then restores the sample to Time order (as per Section 3.3).
    """
    total = len(full_records)
    if n >= total:
        return list(full_records)

    rng = random.Random(seed)
    # Sample n indices uniformly without replacement
    sampled_indices = rng.sample(range(total), n)
    sampled_records = [full_records[i] for i in sampled_indices]

    # Restore to Time order (with txn_id tie-breaking if Time is equal)
    sampled_records.sort(key=lambda r: (r.Time, r.txn_id))
    return sampled_records


def build_condition(base_records, condition_id, seed):
    """
    Constructs the specified input condition (C1-C6) from base_records.
    Returns (records, band_only_flag).

    
    C1: Arrival (records in file order / Time ascending)
    C2: Shuffled (C1 shuffled with seed s)
    C3: Pre-ranked (records already in triage order)
    C4: Reverse-ranked (exact reverse of triage order)
    C5: Nearly ranked (C3 with 1% of records moved to random positions)
    C6: Band-only (C1, but the sort key is band alone)
    """
    cond = condition_id.upper()

    if cond == "C1":
        # Arrival order (copy of base_records, which is already in Time order)
        return list(base_records), False

    elif cond == "C2":
        # Shuffled with seed s
        records = list(base_records)
        rng = random.Random(seed)
        rng.shuffle(records)
        return records, False

    elif cond == "C3":
        # Pre-ranked: sorted in total triage order
        records = sorted(base_records, key=lambda r: r.triage_key())
        return records, False

    elif cond == "C4":
        # Reverse-ranked: exact reverse of triage order
        c3_records = sorted(base_records, key=lambda r: r.triage_key())
        c3_records.reverse()
        return c3_records, False

    elif cond == "C5":
        # Nearly ranked: C3 with 1% of records moved to random positions
        records = sorted(base_records, key=lambda r: r.triage_key())
        n = len(records)
        num_displaced = max(1, int(0.01 * n))
        rng = random.Random(seed)

        # Select 1% indices to displace
        source_indices = rng.sample(range(n), num_displaced)
        for src_idx in source_indices:
            elem = records.pop(src_idx)
            dest_idx = rng.randint(0, len(records))
            records.insert(dest_idx, elem)
        return records, False

    elif cond == "C6":
        # Band-only: C1 arrival records, but sort key is band alone
        return list(base_records), True

    else:
        raise ValueError(f"Unknown condition ID: {condition_id}. Must be C1..C6.")
