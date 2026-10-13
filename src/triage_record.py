"""
TriageRecord and total-order comparison logic.
Uses simple, standard Python with zero external libraries.

Triage Order (Section 3.2):
  1. band descending   (higher risk band first)
  2. Amount descending (larger transaction value first)
  3. Time ascending    (earlier transaction first)
  4. txn_id ascending  (earlier file row breaks ties)
"""


class TriageRecord:
    """
    Represents a single credit card transaction in the triage pipeline.
    """
    def __init__(self, txn_id, Time, Amount, risk, band, Class):
        self.txn_id = int(txn_id)
        self.Time = float(Time)
        self.Amount = float(Amount)
        self.risk = float(risk)
        self.band = int(band)
        self.Class = int(Class)

    def triage_key(self):
        """
        Total order tuple key used for Python's sorted() oracle.
        Tuple order matches standard ascending sort:
        (-band, -Amount, Time, txn_id)
        """
        return (-self.band, -self.Amount, self.Time, self.txn_id)

    def band_only_key(self):
        """Key used for Condition C6 where sorting is by band alone."""
        return (-self.band,)

    def __repr__(self):
        return (f"TriageRecord(txn_id={self.txn_id}, band={self.band}, "
                f"Amount={self.Amount:.2f}, Time={self.Time:.1f}, Class={self.Class})")


def comes_before(a, b, metrics=None, band_only=False):
    """
    Returns True if record 'a' ranks strictly BEFORE record 'b' in triage order.
    Increments metrics.comparisons by 1 if metrics is provided.
    """
    if metrics is not None:
        metrics.comparisons += 1

    if band_only:
        # Band descending: higher band comes first
        return a.band > b.band

    # Multi-tier total order:
    # 1. Band descending
    if a.band != b.band:
        return a.band > b.band

    # 2. Amount descending
    if a.Amount != b.Amount:
        return a.Amount > b.Amount

    # 3. Time ascending
    if a.Time != b.Time:
        return a.Time < b.Time

    # 4. txn_id ascending (unique tie-breaker)
    return a.txn_id < b.txn_id
