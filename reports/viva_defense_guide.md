# Master Viva Defense & Oral Examination Guide (20 Marks)

> **Course:** Design and Analysis of Algorithms | BS Data Science & Artificial Intelligence  
> **Institution:** National University of Computer and Emerging Sciences (FAST-NUCES), Islamabad Campus  
> **Candidate:** Mutasim ur Rehman (`24i-2514`) | Seed $s = 2514$ | Shift Capacity $K = 53$  
> **High-Stakes Constraint:** *A viva score below 50% (< 10/20) caps your total assignment grade at 60%!*  

---

## 🎯 1. Instant Personal Parameters Reference

Keep these numbers memorized. The examiners will ask for them immediately:
* **Roll Number Digits ($s$):** `2514`
* **Personal Shift Capacity ($K$):** $K = 25 + (2514 \pmod{226}) = 25 + 28 = \mathbf{53}$
* **Global Random Seed ($s$):** `2514`
* **Dataset Scale:** $N = 284{,}807$ transactions; **492 confirmed frauds (0.173%)**
* **Multi-Tier Total Order Key (Section 3.2):**
  $$\textbf{band} \downarrow \;\longrightarrow\; \textbf{Amount} \downarrow \;\longrightarrow\; \textbf{Time} \uparrow \;\longrightarrow\; \textbf{txn\_id} \uparrow$$
* **Tournament Champion:** **Merge Sort** ($3.77\text{ s}$ full dataset, strictly stable)
* **Shift Queue Champion:** **Size-$K$ Min-Heap** ($0.086\text{ s}$ at $K=53$, $44\times$ faster than full sort)
* **Streaming Champion:** **Persistent Min-Heap (Strategy b)** ($0.093\text{ s}$ across 48 1-hour windows, $400\times$ faster than re-ranking)
* **50% Fraud Recall Threshold:** **$K = 2{,}068$** transactions capture 246 frauds ($50.0\%$)

---

## 💡 2. Top 10 High-Frequency Viva Questions & Model Answers

### Q1: "Why did Naive QuickSort take 3.4 hours on C3 and C4, and why did native recursion crash?"
* **Answer:** "Naive QuickSort uses Lomuto partitioning with the last element as pivot. On C3 (Pre-ranked) and C4 (Reverse-ranked), the last element is always the extreme value (minimum or maximum). This splits the array into sizes $0$ and $n-1$. The recurrence becomes $T(n) = T(n-1) + n$, resulting in $n(n-1)/2 = 40,553,457,873$ comparisons and $O(n^2)$ time ($3.4\text{ hours}$ DNF). Furthermore, the call stack depth reaches $n$ frames, crashing Python's default recursion limit (1,000 frames) with `RecursionError`. We mitigated the crash by replacing Python's call stack with an explicit iterative array stack (`src/algorithms/quick_sort_naive.py`), allowing it to run safely without crashing, though still quadratic."

### Q2: "Why did Naive QuickSort collapse on C6 (Band-Only) when the data was NOT sorted?"
* **Answer:** "On Condition C6, transactions are sorted strictly by `band`. The dataset has only 8 distinct populated bands (Bands 2 to 9), so there are tens of thousands of duplicate keys. Lomuto's partitioning condition is `arr[i].band > pivot.band`. When an element equals the pivot, this evaluates to `False`, forcing all duplicate elements into the right partition! The subproblem size shrinks by only 1 per step inside each duplicate band group. As derived in proof M6, the intra-group comparison count is exactly $\sum_{k=2}^9 \binom{m_k}{2} = 12,927,756,593$ comparisons, taking $36.4\text{ minutes}$ (DNF). Hardened QuickSort solves this completely using 3-way Dutch National Flag partitioning, which gathers all equal keys in $O(n)$ time, running C6 in just **0.191 seconds**."

### Q3: "How does Floyd's build-heap run in O(n) time when sift-down takes O(log n)?"
* **Answer:** "In bottom-up Floyd build-heap, we call `_sift_down` starting from the lowest internal nodes $(n/2 - 1)$ up to the root $0$. A binary heap has at most $\lceil n / 2^{h+1} \rceil$ nodes at height $h$. Nodes near the bottom (height $h=1$) have many instances ($n/4$ nodes) but perform only 1 sift-down step. The root has height $\log n$ but is only 1 node! The summation is $T(n) \le c n \sum_{h=0}^\infty \frac{h}{2^h}$. Using the geometric series derivative $\sum h x^h = \frac{x}{(1-x)^2}$ evaluated at $x = 1/2$, the sum converges strictly to $2$. Thus $T(n) \le 2cn = O(n)$."

### Q4: "What was your exact inversion count on C5 and why did Insertion Sort finish in 115 seconds?"
* **Answer:** "In Problem F (M1), we proved that Insertion Sort running time is $T(n) = \Theta(n + I)$, where $I$ is the number of inversions. Condition C5 takes the sorted data and displaces 1% of elements randomly. Using an $O(n \log n)$ divide-and-conquer inversion counter on student seed $s = 2514$, we measured exactly **$I = 262,763,679$ inversions** out of a maximum possible $40.56\times 10^9$ ($0.648\%$). Because 99.35% of element pairs are already in correct relative order, Insertion Sort performed only $263\text{M}$ inner-loop shifts, finishing the entire $284{,}807$ dataset in **115.16 seconds** instead of the 4.8 hours required for reverse-ranked data."

### Q5: "Why do you recommend Merge Sort for Job 1 (Overnight Batch) instead of Heap Sort, even though Heap Sort uses O(1) memory?"
* **Answer:** "Two critical engineering reasons:
  1. **Strict Stability:** Merge Sort is stable. In fraud audit trails, if two transactions have identical risk bands, amounts, and arrival timestamps, Merge Sort guarantees their relative order is preserved deterministically. Heap Sort is inherently unstable.
  2. **Cache Locality & Constant Factor:** Merge Sort exhibits sequential memory access during array merging, whereas Heap Sort performs non-sequential pointer jumps across child indices $2i+1$ and $2i+2$, causing CPU cache misses. Empirically, Merge Sort completed in **$3.77\text{ s}$** vs. Heap Sort's **$4.53\text{ s}$** ($17\%$ faster). The $O(n)$ auxiliary buffer is only $2.3\text{ MB}$, which is negligible for modern batch servers."

### Q6: "Why is Size-K Min-Heap 18x faster than Full Sort for selecting the top K alert queue?"
* **Answer:** "Full sort sorts all $N = 284{,}807$ elements in $O(N \log N)$ time, performing $4.79\times 10^6$ comparisons. But analysts only review $K$ transactions. The Size-$K$ Min-Heap maintains a priority queue of size $K$ where the root is the weakest candidate currently in the top $K$. For any incoming record, we compare it against the root in **1 comparison**. If it is weaker, it is rejected immediately! Because the heap contains top elements, the vast majority of transactions are rejected in 1 comparison without touching the heap. Only qualifying items sift-down in $O(\log K)$ time. At $K = 2{,}068$, Min-Heap took **$0.249\text{ s}$** and 525,295 comparisons vs. **$4.387\text{ s}$** for Full Sort ($18\times$ speedup) and required only $16.5\text{ KB}$ of memory vs. $2.3\text{ MB}$ ($137\times$ memory reduction)."

### Q7: "What is the fraud recall at personal quota K = 53, and why did CR-B fix it?"
* **Answer:** "At $K = 53$, fraud recall is **0.0% (0 frauds caught)** under the baseline key! In Phase 1 data profiling, we discovered that Band 9 has 862 transactions, but contains high-value corporate non-fraud transactions alongside micro-testing frauds (€0.00–€1.00). Because Amount is the second tier, high-dollar legitimate transactions crowd out the true frauds. In Problem G (CR-B), we replaced nominal Amount with the continuous $z$-score anomaly sum ($\text{risk} \downarrow$). Under CR-B, $K = 53$ captures 4 confirmed frauds, $K = 200$ captures **91 frauds ($18.5\%$)**, and the 50% fraud threshold is achieved at **$K = 1{,}928$ (saving 140 analyst reviews per shift)**."

### Q8: "How does Hardened QuickSort bound its call stack depth to O(log n)?"
* **Answer:** "Standard quicksort can make recursive calls on large partitions, consuming $O(n)$ stack frames in the worst case. Hardened QuickSort (`src/algorithms/quick_sort_hardened.py`) implements **Tail-Call Elimination**: it calculates the sizes of the left and right partitions, explicitly calls recursion on the *smaller* partition first, and loops on the larger partition. The smaller partition is guaranteed to be at most $\lfloor n/2 \rfloor$. Thus, maximum recursion depth is strictly $\le \lceil \log_2 n \rceil \approx 19$ stack frames for $284{,}807$ records, completely eliminating recursion overflow risks."

### Q9: "Why was Bounded Buffer worse than Min-Heap even though both are O(K) space?"
* **Answer:** "Bounded Buffer maintains a sorted array of capacity $K$. When an incoming record qualifies, it finds the insertion position via binary search in $O(\log K)$ comparisons, but inserting into a Python list requires shifting all subsequent elements down in memory, taking $O(K)$ element moves. At $K = 2{,}068$, Bounded Buffer performed **$12,343,548$ element moves** ($50\times$ more than Min-Heap's 249,171 moves). Buffer is only competitive when $K \le 15$."

### Q10: "How did your algorithms guarantee zero ties in sorting?"
* **Answer:** "In `src/triage_record.py`, every transaction has a unique, 1-indexed row number `txn_id` assigned during raw file reading. The multi-tier comparator evaluates:
1. `band` descending
2. `Amount` descending
3. `Time` ascending
4. `txn_id` ascending
Because `txn_id` is strictly unique for every row, two records can never evaluate as equal in the total order comparator. This guarantees a mathematically **strict total order** with zero arbitrary tie-breaking."

---

## 🛠️ 3. Live Code Modification Drills (Examiner Challenge Simulation)

The examiner will ask you to modify your code live on an unseen requirement. Here are the exact modifications:

### Drill 1: "Reverse the sort order so weakest transactions come first"
* **Target:** `src/triage_record.py`
* **Action:** Invert the return statements in `comes_before`:
```python
def comes_before_reversed(a, b):
    # Weakest first: lowest band first, smallest amount first, latest time first
    if a.band != b.band: return a.band < b.band
    if a.Amount != b.Amount: return a.Amount < b.Amount
    if a.Time != b.Time: return a.Time > b.Time
    return a.txn_id > b.txn_id
```

### Drill 2: "Prioritize newest transactions instead of oldest" (Problem G CR-A)
* **Target:** `src/triage_record.py`
* **Action:** Change `a.Time < b.Time` to `a.Time > b.Time`.

### Drill 3: "Add a 5th tie-breaker or change the comparator in console.py"
* **Target:** `console.py` line 364.
* **Action:** Pass `rule="cr_freshness"` or use a named reference-key function that returns `record.triage_key(rule)`.

---

## 🚀 4. How to Demonstrate the Analyst Console in 30 Seconds

```bash
# Terminal command:
py console.py
```
1. Open browser to `http://127.0.0.1:8050`.
2. **Demonstrate Algorithm Speedup:**
   * Select `Full Sort: Merge Sort [:K]` on $n = 10{,}000$ &rarr; Click "Build Queue" &rarr; Show $\approx 80\text{ ms}$, $120\text{k}$ comparisons.
   * Switch to `Size-K Min-Heap` on $n = 10{,}000$ &rarr; Click "Build Queue" &rarr; Show $\approx 4\text{ ms}$, $13\text{k}$ comparisons (**$20\times$ faster**).
3. **Demonstrate Change Request Toggle (Problem G):**
   * Select `Standard Triage Rule` at $K = 53$ &rarr; Show 0 frauds caught ($0.0\%$).
   * Switch dropdown to `Change Request B: Continuous Risk` &rarr; Click "Build Queue" &rarr; Instantly show **4 confirmed frauds caught with glowing red alert badges**!
4. Mention that the server runs on pure Python standard library with **zero external web frameworks**.
