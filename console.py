"""Serve the analyst page and run the selected algorithm. Start with python console.py."""
import http.server
import socketserver
import urllib.parse
import json
import time
import math
import os


from src.dataset import load_triage_records
from src.conditions import build_condition, subsample_records
from src.metrics import Metrics
from src.algorithms.top_k import top_k_min_heap, top_k_bounded_buffer
from src.algorithms.merge_sort import merge_sort
from src.algorithms.heap_sort import heap_sort
from src.algorithms.quick_sort_hardened import quick_sort_hardened

PORT = 8050

# Load records on the first request and reuse them afterwards.
MASTER_RECORDS = None


def get_master_records():
    global MASTER_RECORDS
    if MASTER_RECORDS is None:
        print("Loading transaction records...")
        MASTER_RECORDS = load_triage_records()
        print(f"Loaded {len(MASTER_RECORDS):,} transactions.")
    return MASTER_RECORDS


with open(os.path.join(os.path.dirname(__file__), "console.html"), encoding="utf-8") as page_file:
    HTML_PAGE = page_file.read()


def build_queue(algo, cond_id, n, k, rule="standard"):
    """Prepare an input, time the algorithm, and return the queue and counters."""
    # Prepare data
    seed = 2514
    sub = subsample_records(get_master_records(), n, seed=seed)
    cond_data, band_only = build_condition(sub, cond_id, seed=seed)
    total_frauds_sample = 0
    for r in sub:
        total_frauds_sample += r.Class

    metrics = Metrics()
    start_time = time.perf_counter()
    top_records = []
    aux_mem = k

    if algo == "min_heap":
        top_records = top_k_min_heap(cond_data, k, metrics, band_only, rule=rule)
        aux_mem = k
    elif algo == "bounded_buffer":
        top_records = top_k_bounded_buffer(cond_data, k, metrics, band_only, rule=rule)
        aux_mem = k
    elif algo == "merge_sort":
        arr_copy = list(cond_data)
        merge_sort(arr_copy, metrics, band_only, rule=rule)
        top_records = arr_copy[:k]
        aux_mem = n
    elif algo == "quick_hardened":
        arr_copy = list(cond_data)
        quick_sort_hardened(arr_copy, metrics, band_only, rule=rule)
        top_records = arr_copy[:k]
        aux_mem = 0
        if n > 0:
            aux_mem = int(math.log2(n))
    elif algo == "heap_sort":
        arr_copy = list(cond_data)
        heap_sort(arr_copy, metrics, band_only, rule=rule)
        top_records = arr_copy[:k]
        aux_mem = 0

    elapsed_time = time.perf_counter() - start_time
    frauds_captured = 0
    for r in top_records:
        frauds_captured += r.Class

    record_rows = []
    for record in top_records:
        row = {
            "txn_id": record.txn_id,
            "band": record.band,
            "Amount": record.Amount,
            "Time": record.Time,
            "risk": record.risk,
            "Class": record.Class,
        }
        record_rows.append(row)
    response_payload = {
        "algorithm": algo,
        "condition": cond_id,
        "n": n,
        "k": k,
        "time_sec": elapsed_time,
        "comparisons": metrics.comparisons,
        "moves": metrics.moves,
        "aux_memory": aux_mem,
        "total_frauds_in_sample": total_frauds_sample,
        "frauds_captured": frauds_captured,
        "records": record_rows
    }

    return response_payload


class AnalystConsoleHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
            return

        elif parsed.path == "/api/run":
            query = urllib.parse.parse_qs(parsed.query)
            algo = query.get("algo", ["min_heap"])[0]
            cond_id = query.get("cond", ["C1"])[0]
            n = int(query.get("n", [10000])[0])
            k = int(query.get("k", [53])[0])
            rule = query.get("rule", ["standard"])[0]

            response_payload = build_queue(algo, cond_id, n, k, rule)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response_payload).encode("utf-8"))
            return

        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    server_address = ("127.0.0.1", PORT)
    with socketserver.TCPServer(server_address, AnalystConsoleHandler) as httpd:
        print(f"\n=======================================================")
        print(f"[+] Analyst Console Server Running at http://127.0.0.1:{PORT}")
        print("Press Ctrl+C to stop.")
        print(f"=======================================================\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down Analyst Console server.")

if __name__ == "__main__":
    run_server()
