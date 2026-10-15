"""
Dataset loading and feature standardization pipeline according to Section 3.2.
"""
import os
import numpy as np
import pandas as pd

from src.triage_record import TriageRecord


def find_dataset_path():
    """Locates the creditcard.csv file in common workspace directories."""
    candidates = [
        "creditcard.csv",
        os.path.join("mlg-ulb", "creditcardfraud", "versions", "3", "creditcard.csv"),
        os.path.join("..", "creditcard.csv"),
        os.path.join("data", "creditcard.csv")
    ]
    for p in candidates:
        if os.path.exists(p):
            return os.path.abspath(p)
    raise FileNotFoundError(
        "creditcard.csv not found. Please ensure the dataset is placed in the workspace."
    )


def load_triage_records(csv_path=None):
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
    n = len(df)
    txn_ids = np.arange(1, n + 1, dtype=np.int64)

    # 2. Standardised features z_1 to z_28 and Risk Score (column-by-column to minimize memory)
    risk_scores = np.zeros(n, dtype=np.float64)
    for i in range(1, 29):
        col = df[f"V{i}"].values
        m = np.mean(col)
        s = np.std(col, ddof=0)
        if s == 0:
            s = 1.0
        z = (col - m) / s
        risk_scores += z * z

    # 3. Risk band: min(9, max(0, floor(log2(risk))))
    log2_risk = np.floor(np.log2(np.maximum(risk_scores, 1e-12))).astype(int)
    bands = np.clip(log2_risk, 0, 9)

    times = df["Time"].values.astype(float)
    amounts = df["Amount"].values.astype(float)
    classes = df["Class"].values.astype(int)

    records = []
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

