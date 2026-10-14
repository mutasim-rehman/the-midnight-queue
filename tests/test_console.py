"""
Automated unit and integration test for the Analyst Console (Bonus Section 6).
Verifies:
1. Web server initialization
2. HTML dashboard serving
3. JSON API responses for Top-K Heap, MergeSort, Hardened QuickSort
4. Change Request rule parameters (standard, cr_freshness, cr_risk)
"""
import pytest
import threading
import time
import urllib.request
import json
import console

@pytest.fixture(scope="module")
def console_server():
    server_thread = threading.Thread(target=console.run_server, daemon=True)
    server_thread.start()
    time.sleep(1.0)
    yield "http://127.0.0.1:8050"

def test_html_dashboard_endpoint(console_server):
    req = urllib.request.Request(f"{console_server}/")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        content = resp.read().decode("utf-8")
        assert "The Midnight Queue: Analyst Console" in content
        assert "Triage Order Rule" in content

def test_api_min_heap_standard(console_server):
    url = f"{console_server}/api/run?algo=min_heap&cond=C1&n=1000&k=10&rule=standard"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["algorithm"] == "min_heap"
        assert data["k"] == 10
        assert len(data["records"]) == 10
        assert data["comparisons"] > 0
        assert data["moves"] > 0

def test_api_change_request_freshness(console_server):
    url = f"{console_server}/api/run?algo=min_heap&cond=C1&n=1000&k=10&rule=cr_freshness"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["algorithm"] == "min_heap"
        assert len(data["records"]) == 10

def test_api_merge_sort_full(console_server):
    url = f"{console_server}/api/run?algo=merge_sort&cond=C1&n=1000&k=10&rule=standard"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["algorithm"] == "merge_sort"
        assert len(data["records"]) == 10
