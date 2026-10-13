"""
Dataset loading and feature standardization pipeline according to Section 3.2.
"""
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
import pandas as pd

from src.triage_record import TriageRecord


def find_dataset_path() -> Path:
    """Locates the creditcard.csv file in common workspace directories."""
    candidates = [
        Path("creditcard.csv"),
        Path("mlg-ulb/creditcardfraud/versions/3/creditcard.csv"),
        Path("../creditcard.csv"),
        Path("data/creditcard.csv")
    ]
    for p in candidates:
        if p.exists():
            return p.resolve()
    raise FileNotFoundError(
        "creditcard.csv not found. Please ensure the dataset is placed in the workspace."
    )


def load_triage_records(csv_path: Optional[Path] = None) -> List[TriageRecord]:
    """
    Loads creditcard.csv and computes:
      1. txn_id: 1-indexed row number.
      2. Standardised features: z_i = (V_i - mean_i) / std_i for i = 1..28.
      3. Risk score: sum(z_i^2).
      4. Risk band: min(9, max(0, floor(log2(risk)))).
    Returns list of TriageRecord in original file order (Time ascending).
    """
    if csv_path is None:
        csv_path = find_dataset_path()

    df = pd.read_csv(csv_path)

    # 1. txn_id (1-indexed row number)
    txn_ids = np.arange(1, len(df) + 1, dtype=np.int64)

    # 2. Standardised features z_1 to z_28
    v_cols = [f"V{i}" for i in range(1, 29)]
    v_matrix = df[v_cols].values
    means = np.mean(v_matrix, axis=0)
    stds = np.std(v_matrix, axis=0, ddof=0)  # full file std

    # Avoid zero division
    stds[stds == 0] = 1.0
    z_matrix = (v_matrix - means) / stds

    # 3. Risk score: sum of squared z_i
    risk_scores = np.sum(z_matrix ** 2, axis=1)

    # 4. Risk band: min(9, max(0, floor(log2(risk))))
    # Protect against non-positive risk
    log2_risk = np.floor(np.log2(np.maximum(risk_scores, 1e-12))).astype(int)
    bands = np.clip(log2_risk, 0, 9)

    times = df["Time"].values.astype(float)
    amounts = df["Amount"].values.astype(float)
    classes = df["Class"].values.astype(int)

    records: List[TriageRecord] = []
    for i in range(len(df)):
        records.append(
            TriageRecord(
                txn_id=int(txn_ids[i]),
                Time=float(times[i]),
                Amount=float(amounts[i]),
                risk=float(risk_scores[i]),
                band=int(bands[i]),
                Class=int(classes[i])
            )
        )

    return records
