"""Read transactions and calculate risk using csv, math, and loops."""
import csv
import math
import os

from src.triage_record import TriageRecord


def find_dataset_path():
    """Look for the dataset in the usual project folders."""
    candidates = [
        "creditcard.csv",
        os.path.join("mlg-ulb", "creditcardfraud", "versions", "3", "creditcard.csv"),
        os.path.join("..", "creditcard.csv"),
        os.path.join("data", "creditcard.csv"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return os.path.abspath(path)
    raise FileNotFoundError("Place creditcard.csv in the project or data folder.")


def load_triage_records(csv_path=None):
    """Use three passes so we do not keep all 28 features in memory."""
    if csv_path is None:
        csv_path = find_dataset_path()

    # First pass: find the mean of each feature column.
    totals = [0.0] * 28
    count = 0
    with open(csv_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            count += 1
            for i in range(28):
                totals[i] += float(row["V" + str(i + 1)])

    if count == 0:
        return []

    means = []
    for total in totals:
        means.append(total / count)

    # Second pass: find population standard deviations (divide by n).
    squared_differences = [0.0] * 28
    with open(csv_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            for i in range(28):
                difference = float(row["V" + str(i + 1)]) - means[i]
                squared_differences[i] += difference * difference

    standard_deviations = []
    for total in squared_differences:
        deviation = math.sqrt(total / count)
        if deviation == 0:
            deviation = 1.0
        standard_deviations.append(deviation)

    # Third pass: add squared z-scores and create records in file order.
    records = []
    with open(csv_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            risk = 0.0
            for i in range(28):
                value = float(row["V" + str(i + 1)])
                z_score = (value - means[i]) / standard_deviations[i]
                risk += z_score * z_score

            band = 0
            if risk > 0:
                band = math.floor(math.log2(risk))
            band = min(9, max(0, band))

            record = TriageRecord(
                len(records) + 1, row["Time"], row["Amount"],
                risk, band, row["Class"],
            )
            records.append(record)

    return records
