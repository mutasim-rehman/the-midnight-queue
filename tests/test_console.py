"""Check the console using a small dataset and a temporary local server."""
import json
import socketserver
import threading
import unittest
import urllib.request

import console
from tests.test_problem_b import make_dummy_records


class ConsoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved_records = console.MASTER_RECORDS
        console.MASTER_RECORDS = make_dummy_records(1000)
        # Port 0 asks Windows for a free port.
        cls.server = socketserver.TCPServer(("127.0.0.1", 0), console.AnalystConsoleHandler)
        cls.base_url = "http://127.0.0.1:" + str(cls.server.server_address[1])
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        console.MASTER_RECORDS = cls.saved_records

    def test_html_dashboard_endpoint(self):
        with urllib.request.urlopen(self.base_url + "/", timeout=10) as response:
            assert response.status == 200
            content = response.read().decode("utf-8")
            assert "The Midnight Queue: Analyst Console" in content
            assert "Triage Order Rule" in content

    def test_api_algorithms_and_rules(self):
        algorithms = ["min_heap", "bounded_buffer", "merge_sort", "quick_hardened", "heap_sort"]
        rules = ["standard", "cr_freshness", "cr_risk"]
        for algorithm in algorithms:
            for rule in rules:
                with self.subTest(algorithm=algorithm, rule=rule):
                    url = self.base_url + "/api/run?algo=" + algorithm
                    url += "&cond=C1&n=1000&k=10&rule=" + rule
                    with urllib.request.urlopen(url, timeout=10) as response:
                        assert response.status == 200
                        data = json.loads(response.read().decode("utf-8"))
                    assert data["algorithm"] == algorithm
                    assert data["k"] == 10
                    assert len(data["records"]) == 10
                    assert data["comparisons"] > 0
                    assert data["moves"] > 0

                    def reference_key(record):
                        return record.triage_key(rule)

                    expected = sorted(console.MASTER_RECORDS, key=reference_key)[:10]
                    for index in range(10):
                        assert data["records"][index]["txn_id"] == expected[index].txn_id

    def test_missing_page(self):
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(self.base_url + "/missing", timeout=10)
        assert error.exception.code == 404
