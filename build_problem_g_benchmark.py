"""
Problem G: Change Request Benchmark & Visualization Suite.
Produces empirical measurement data and figures for Problem G Addendum.
Uses basic Python with minimal libraries (matplotlib only for plotting).
"""
import os
import sys
import time
from pathlib import Path
import matplotlib.pyplot as plt

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.dataset import load_triage_records
from src.conditions import subsample_records
from src.metrics import Metrics
from src.algorithms.merge_sort import merge_sort
from src.algorithms.heap_sort import heap_sort
from src.algorithms.quick_sort_hardened import quick_sort_hardened
from src.algorithms.top_k import top_k_min_heap

def run_problem_g_benchmarks():
    out_dir = Path("figures/problem_g")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading master dataset for Problem G benchmarks...")
    records = load_triage_records()
    total_records = len(records)
    total_frauds = sum(r.Class for r in records)
    seed = 2514
    print(f"Loaded {total_records:,} transactions ({total_frauds} frauds).")
    
    # -------------------------------------------------------------
    # 1. Benchmark Runtime and Comparisons Across Input Sizes (n)
    # -------------------------------------------------------------
    sizes = [1000, 10000, 100000, 284807]
    rules = ["standard", "cr_freshness", "cr_risk"]
    rule_labels = {
        "standard": "Baseline (Time Asc)",
        "cr_freshness": "CR-A (Freshest First)",
        "cr_risk": "CR-B (Continuous Risk)"
    }
    
    # Structure: results[algo][rule][n] = (time_sec, comps, moves)
    results = {
        "merge_sort": {r: {} for r in rules},
        "heap_sort": {r: {} for r in rules},
        "min_heap_53": {r: {} for r in rules}
    }
    
    print("\n" + "="*70)
    print("BENCHMARKING ALGORITHMS ACROSS RULES AND SIZES")
    print("="*70)
    
    for n in sizes:
        sub = subsample_records(records, n, seed=seed)
        for r_id in rules:
            # Merge Sort
            arr_m = list(sub)
            m_m = Metrics()
            t0 = time.perf_counter()
            merge_sort(arr_m, m_m, rule=r_id)
            dt_m = time.perf_counter() - t0
            results["merge_sort"][r_id][n] = (dt_m, m_m.comparisons, m_m.moves)
            
            # Heap Sort
            arr_h = list(sub)
            m_h = Metrics()
            t0 = time.perf_counter()
            heap_sort(arr_h, m_h, rule=r_id)
            dt_h = time.perf_counter() - t0
            results["heap_sort"][r_id][n] = (dt_h, m_h.comparisons, m_h.moves)
            
            # Top-K Min-Heap (K = 53)
            m_k = Metrics()
            t0 = time.perf_counter()
            top_k_min_heap(sub, 53, m_k, rule=r_id)
            dt_k = time.perf_counter() - t0
            results["min_heap_53"][r_id][n] = (dt_k, m_k.comparisons, m_k.moves)
            
            print(f"n = {n:>7,d} | {rule_labels[r_id]:<22s} | MergeSort: {dt_m:.4f}s ({m_m.comparisons:>9,d} comps) | HeapSort: {dt_h:.4f}s | Min-Heap-53: {dt_k:.4f}s ({m_k.comparisons:>7,d} comps)")

    # -------------------------------------------------------------
    # 2. Fraud Recall & Queue Analysis across K
    # -------------------------------------------------------------
    print("\n" + "="*70)
    print("ANALYZING FRAUD RECALL DYNAMICS ACROSS K")
    print("="*70)
    
    # Pre-sort complete dataset under each rule using Python oracle
    sorted_baseline = sorted(records, key=lambda r: r.triage_key(rule="standard"))
    sorted_freshness = sorted(records, key=lambda r: r.triage_key(rule="cr_freshness"))
    sorted_risk = sorted(records, key=lambda r: r.triage_key(rule="cr_risk"))
    
    # Cumulative fraud counts
    def get_cum_frauds(arr):
        cum = []
        count = 0
        for r in arr:
            if r.Class == 1:
                count += 1
            cum.append(count)
        return cum
        
    cum_base = get_cum_frauds(sorted_baseline)
    cum_fresh = get_cum_frauds(sorted_freshness)
    cum_risk = get_cum_frauds(sorted_risk)
    
    k_eval_points = [10, 50, 53, 100, 200, 500, 1000, 1928, 2068, 2086, 5000, 10000]
    for k in k_eval_points:
        fb = cum_base[k-1]
        ff = cum_fresh[k-1]
        fr = cum_risk[k-1]
        print(f"K = {k:>6,d} | Baseline: {fb:>3d} ({fb/total_frauds*100:5.1f}%) | CR-A(Fresh): {ff:>3d} ({ff/total_frauds*100:5.1f}%) | CR-B(Risk): {fr:>3d} ({fr/total_frauds*100:5.1f}%)")

    # Find exact 50% fraud crossover (246 frauds)
    k_50_base = cum_base.index(246) + 1
    k_50_fresh = cum_fresh.index(246) + 1
    k_50_risk = cum_risk.index(246) + 1
    
    print("\n--- 50% Fraud Threshold (246 frauds) Summary ---")
    print(f"Baseline (Time Asc):    K = {k_50_base:,} transactions")
    print(f"CR-A (Freshest First):  K = {k_50_fresh:,} transactions (+{k_50_fresh - k_50_base} slots)")
    print(f"CR-B (Continuous Risk): K = {k_50_risk:,} transactions ({k_50_risk - k_50_base} slots)")

    # -------------------------------------------------------------
    # 3. Generate Visual Deliverables
    # -------------------------------------------------------------
    print("\nGenerating figures in figures/problem_g/...")
    
    # Plot G1: Fraud Recall Curve Comparison
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=150)
    k_range = list(range(1, 5001))
    
    recall_base = [cum_base[k-1] / total_frauds * 100 for k in k_range]
    recall_fresh = [cum_fresh[k-1] / total_frauds * 100 for k in k_range]
    recall_risk = [cum_risk[k-1] / total_frauds * 100 for k in k_range]
    
    ax.plot(k_range, recall_base, label="Baseline: Time Ascending", color="#1e3a8a", linewidth=2)
    ax.plot(k_range, recall_fresh, label="CR-A: Freshest First (Time Desc)", color="#0284c7", linestyle="--", linewidth=2)
    ax.plot(k_range, recall_risk, label="CR-B: Continuous Risk Score", color="#10b981", linewidth=2)
    
    # Thresholds
    ax.axhline(50, color="#ef4444", linestyle=":", linewidth=1.5, label="50% Fraud Capture Threshold (246 Frauds)")
    ax.axvline(53, color="#f59e0b", linestyle="-.", linewidth=1.5, label="Personal Shift Capacity K = 53")
    
    # Scatter points for crossover
    ax.scatter([k_50_base], [50], color="#1e3a8a", s=60, zorder=5)
    ax.scatter([k_50_fresh], [50], color="#0284c7", s=60, zorder=5)
    ax.scatter([k_50_risk], [50], color="#10b981", s=60, zorder=5)
    
    ax.annotate(f"Baseline K = {k_50_base:,}", xy=(k_50_base, 50), xytext=(k_50_base + 150, 43),
                arrowprops=dict(arrowstyle="->", color="#1e3a8a", lw=1), fontsize=9, fontweight="bold", color="#1e3a8a")
    ax.annotate(f"CR-A K = {k_50_fresh:,}", xy=(k_50_fresh, 50), xytext=(k_50_fresh + 150, 36),
                arrowprops=dict(arrowstyle="->", color="#0284c7", lw=1), fontsize=9, fontweight="bold", color="#0284c7")
    ax.annotate(f"CR-B K = {k_50_risk:,}\n(Saves 140 slots)", xy=(k_50_risk, 50), xytext=(k_50_risk - 900, 56),
                arrowprops=dict(arrowstyle="->", color="#10b981", lw=1), fontsize=9, fontweight="bold", color="#047857")

    ax.set_title("Problem G: Fraud Recall vs Queue Capacity (Baseline vs Change Requests)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Queue Shift Capacity (K)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Total Fraud Capture Recall (%)", fontsize=11, fontweight="bold")
    ax.set_xlim(0, 5000)
    ax.set_ylim(0, 80)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="lower right", frameon=True, fontsize=9)
    plt.tight_layout()
    plot_g1_path = out_dir / "plot_g1_fraud_recall_comparison.png"
    plt.savefig(plot_g1_path)
    plt.close()
    print(f"Saved: {plot_g1_path}")

    # Plot G2: Algorithmic Invariance (Runtime & Comparisons vs n)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=150)
    
    # Left: Merge Sort Runtime Comparison
    for r_id, color, marker in [("standard", "#1e3a8a", "o"), ("cr_freshness", "#0284c7", "s"), ("cr_risk", "#10b981", "^")]:
        times = [results["merge_sort"][r_id][n][0] for n in sizes]
        ax1.plot(sizes, times, label=f"MergeSort: {rule_labels[r_id]}", color=color, marker=marker, linewidth=1.8)
    
    # Also plot Min-Heap
    for r_id, color, marker in [("standard", "#d97706", "o"), ("cr_freshness", "#ea580c", "s")]:
        times = [results["min_heap_53"][r_id][n][0] for n in sizes]
        ax1.plot(sizes, times, label=f"Min-Heap-53: {rule_labels[r_id]}", color=color, marker=marker, linestyle="--", linewidth=1.8)
        
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_title("Execution Runtime vs Input Size (n)", fontsize=12, fontweight="bold", pad=10)
    ax1.set_xlabel("Input Size (n)", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Execution Time (seconds, log scale)", fontsize=10, fontweight="bold")
    ax1.grid(True, which="both", linestyle="--", alpha=0.5)
    ax1.legend(fontsize=8, loc="upper left")

    # Right: Comparisons vs n
    for r_id, color, marker in [("standard", "#1e3a8a", "o"), ("cr_freshness", "#0284c7", "s"), ("cr_risk", "#10b981", "^")]:
        comps = [results["merge_sort"][r_id][n][1] for n in sizes]
        ax2.plot(sizes, comps, label=f"MergeSort: {rule_labels[r_id]}", color=color, marker=marker, linewidth=1.8)

    for r_id, color, marker in [("standard", "#d97706", "o"), ("cr_freshness", "#ea580c", "s")]:
        comps = [results["min_heap_53"][r_id][n][1] for n in sizes]
        ax2.plot(sizes, comps, label=f"Min-Heap-53: {rule_labels[r_id]}", color=color, marker=marker, linestyle="--", linewidth=1.8)

    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_title("Key Comparisons vs Input Size (n)", fontsize=12, fontweight="bold", pad=10)
    ax2.set_xlabel("Input Size (n)", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Key Comparisons (log scale)", fontsize=10, fontweight="bold")
    ax2.grid(True, which="both", linestyle="--", alpha=0.5)
    ax2.legend(fontsize=8, loc="upper left")

    plt.suptitle("Problem G: Computational Invariance Under Sorting Rule Modifications", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plot_g2_path = out_dir / "plot_g2_runtime_invariance.png"
    plt.savefig(plot_g2_path)
    plt.close()
    print(f"Saved: {plot_g2_path}")

    print("\nProblem G benchmark suite complete!")

if __name__ == "__main__":
    run_problem_g_benchmarks()
