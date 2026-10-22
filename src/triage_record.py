"""Transaction fields and the rules used to compare two transactions."""


class TriageRecord:
    """Store one transaction. Class is used only to measure fraud recall."""

    def __init__(self, txn_id, Time, Amount, risk, band, Class):
        self.txn_id = int(txn_id)
        self.Time = float(Time)
        self.Amount = float(Amount)
        self.risk = float(risk)
        self.band = int(band)
        self.Class = int(Class)

    def triage_key(self, rule="standard"):
        """Negative values put larger numbers first in the reference sort."""
        if rule == "cr_freshness":
            return (-self.band, -self.Amount, -self.Time, self.txn_id)
        if rule == "cr_risk":
            return (-self.band, -self.risk, -self.Amount, self.Time, self.txn_id)
        return (-self.band, -self.Amount, self.Time, self.txn_id)

    def band_only_key(self):
        """C6 ignores every field except band."""
        return (-self.band,)

    def __repr__(self):
        return (f"TriageRecord(txn_id={self.txn_id}, band={self.band}, "
                f"Amount={self.Amount:.2f}, Time={self.Time:.1f}, Class={self.Class})")


def comes_before(a, b, metrics=None, band_only=False, rule="standard"):
    """Return True if a should appear before b. Count one key comparison."""
    if metrics is not None:
        metrics.comparisons += 1

    if a.band != b.band:
        return a.band > b.band
    if band_only:
        return False

    # The continuous-risk rule adds one check before Amount.
    if rule == "cr_risk" and a.risk != b.risk:
        return a.risk > b.risk
    if a.Amount != b.Amount:
        return a.Amount > b.Amount
    if a.Time != b.Time:
        if rule == "cr_freshness":
            return a.Time > b.Time
        return a.Time < b.Time

    # Row IDs break the final tie.
    return a.txn_id < b.txn_id


def arrival_key(record):
    """Restore sampled records to arrival order."""
    return (record.Time, record.txn_id)


def standard_key(record):
    """Reference key for preparing inputs and checking results."""
    return record.triage_key()
