"""Prepare the six input conditions with a fixed random seed."""
import random
from src.triage_record import arrival_key, standard_key


def subsample_records(full_records, n, seed):
    """Sample without replacement, then restore arrival order."""
    total = len(full_records)
    if n >= total:
        return list(full_records)

    rng = random.Random(seed)
    # Sample n indices uniformly without replacement
    sampled_indices = rng.sample(range(total), n)
    sampled_records = []
    for index in sampled_indices:
        sampled_records.append(full_records[index])

    # Restore to Time order (with txn_id tie-breaking if Time is equal)
    sampled_records.sort(key=arrival_key)
    return sampled_records


def build_condition(base_records, condition_id, seed):
    """Return a fresh input list and whether to compare only bands."""
    cond = condition_id.upper()
    if len(base_records) == 0 and cond in ["C1", "C2", "C3", "C4", "C5", "C6"]:
        return [], cond == "C6"

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
        records = sorted(base_records, key=standard_key)
        return records, False

    elif cond == "C4":
        # Reverse-ranked: exact reverse of triage order
        c3_records = sorted(base_records, key=standard_key)
        c3_records.reverse()
        return c3_records, False

    elif cond == "C5":
        # Nearly ranked: C3 with 1% of records moved to random positions
        records = sorted(base_records, key=standard_key)
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
