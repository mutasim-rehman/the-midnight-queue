"""Check the CSV loader with small examples that have known risk scores."""
import csv
import math
import os
import tempfile
import unittest

from src.dataset import load_triage_records


class DatasetTests(unittest.TestCase):
    def load_example(self, feature_values):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "creditcard.csv")
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                columns = ["Time"]
                for i in range(1, 29):
                    columns.append("V" + str(i))
                columns.extend(["Amount", "Class"])
                writer.writerow(columns)
                for value in feature_values:
                    row = [value * 10]
                    for i in range(28):
                        row.append(value)
                    row.extend([50, 0])
                    writer.writerow(row)
            return load_triage_records(path)

    def test_population_standard_deviation(self):
        records = self.load_example([0, 2, 4])
        assert len(records) == 3
        for index, expected_risk in enumerate([42, 0, 42]):
            assert records[index].txn_id == index + 1
            assert math.isclose(records[index].risk, expected_risk, abs_tol=1e-10)
        assert records[0].band == 5
        assert records[1].band == 0
        assert records[2].band == 5

    def test_empty_file(self):
        assert self.load_example([]) == []

    def test_constant_features(self):
        records = self.load_example([3, 3])
        for record in records:
            assert record.risk == 0
            assert record.band == 0

    def test_single_record(self):
        records = self.load_example([3])
        assert len(records) == 1
        assert records[0].risk == 0
        assert records[0].band == 0
