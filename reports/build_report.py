"""Build the five-page project report from the saved results and checked facts."""
import csv
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Drawing, Line, PolyLine, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
FACTS = json.loads((ROOT / "reports/report_data.json").read_text())
with open(ROOT / "results.csv", newline="", encoding="utf-8") as file:
    RESULTS = list(csv.DictReader(file))

for name, filename in [("Report", "times.ttf"), ("ReportBold", "timesbd.ttf"), ("ReportItalic", "timesi.ttf")]:
    pdfmetrics.registerFont(TTFont(name, "C:/Windows/Fonts/" + filename))
pdfmetrics.registerFontFamily("Report", normal="Report", bold="ReportBold", italic="ReportItalic", boldItalic="ReportBold")

WIDTH = A4[0] - 84
INK = colors.HexColor("#242424")
GRAY = colors.HexColor("#666666")
STYLES = {
    "title": ParagraphStyle("title", fontName="ReportBold", fontSize=19, leading=22, textColor=INK, spaceAfter=5),
    "subtitle": ParagraphStyle("subtitle", fontName="Report", fontSize=10, leading=13, textColor=GRAY, spaceAfter=12),
    "heading": ParagraphStyle("heading", fontName="ReportBold", fontSize=11.5, leading=14, textColor=INK, spaceBefore=10, spaceAfter=5, keepWithNext=True),
    "body": ParagraphStyle("body", fontName="Report", fontSize=9.6, leading=12.3, textColor=INK, spaceAfter=6),
    "small": ParagraphStyle("small", fontName="Report", fontSize=8.5, leading=10.5, textColor=GRAY, spaceAfter=5),
    "cell": ParagraphStyle("cell", fontName="Report", fontSize=8.2, leading=10, textColor=INK),
    "caption": ParagraphStyle("caption", fontName="ReportItalic", fontSize=8.3, leading=10.5, textColor=GRAY, spaceAfter=8),
}
STORY = []


def paragraph(text, style="body"):
    return Paragraph(text, STYLES[style])


def add(text, style="body"):
    STORY.append(paragraph(text, style))


def table(rows, widths):
    cells = []
    for row in rows:
        cells.append([paragraph(str(value), "cell") for value in row])
    result = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.HexColor("#777777")),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#dddddd")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    STORY.append(result)
    STORY.append(Spacer(1, 5))


def result(algorithm, condition, n):
    for row in RESULTS:
        if row["algorithm"] == algorithm and row["condition"] == condition and int(row["n"]) == n:
            return row
    raise ValueError("Missing tournament result")


ALGORITHMS = ["Insertion Sort", "Merge Sort", "Naive QuickSort", "Hardened QuickSort", "Heap Sort"]
PALETTE = ["#ab5936", "#315a80", "#8b4141", "#4c7456", "#756385"]


def time_chart():
    drawing = Drawing(WIDTH, 172)
    left, bottom, width, height = 48, 35, WIDTH - 60, 105
    def x_position(n):
        return left + (math.log10(n) - 3) / (math.log10(284807) - 3) * width
    def y_position(seconds):
        return bottom + (math.log10(seconds) + 3) / 7 * height
    for power in [-3, -2, -1, 0, 1, 2, 3, 4]:
        y = y_position(10 ** power)
        drawing.add(Line(left, y, left + width, y, strokeColor=colors.HexColor("#dddddd"), strokeWidth=0.4))
        drawing.add(String(left - 7, y - 2, str(10 ** power), fontName="Report", fontSize=7, textAnchor="end"))
    for n, label in [(1000, "1,000"), (10000, "10,000"), (100000, "100,000"), (284807, "284,807")]:
        drawing.add(String(x_position(n), bottom - 12, label, fontName="Report", fontSize=7, textAnchor="middle"))
    for index, algorithm in enumerate(ALGORITHMS):
        previous = None
        for n in [1000, 10000, 100000, 284807]:
            row = result(algorithm, "C2", n)
            current = (x_position(n), y_position(float(row["time_sec"])))
            if previous:
                line = Line(*previous, *current, strokeColor=colors.HexColor(PALETTE[index]), strokeWidth=1.3)
                if row["extrapolated"] == "True":
                    line.strokeDashArray = [3, 2]
                drawing.add(line)
            drawing.add(Rect(current[0]-1.5, current[1]-1.5, 3, 3, fillColor=colors.HexColor(PALETTE[index]), strokeColor=None))
            previous = current
        drawing.add(String(48 + index * 94, 157, algorithm.replace("QuickSort", "Quick"), fontName="Report", fontSize=7.1, fillColor=colors.HexColor(PALETTE[index])))
    drawing.add(String(left, 14, "Input size n (log scale)", fontName="Report", fontSize=8))
    drawing.add(String(0, 144, "Time (s, log)", fontName="Report", fontSize=8))
    return drawing


def recall_chart():
    drawing = Drawing(WIDTH, 160)
    left, bottom, width, height = 35, 27, WIDTH - 50, 110
    for percentage in [0, 25, 50, 75, 100]:
        y = bottom + height * percentage / 100
        drawing.add(Line(left, y, left+width, y, strokeColor=colors.HexColor("#dddddd"), strokeWidth=0.4))
        drawing.add(String(left-7, y-2, str(percentage), fontName="Report", fontSize=7, textAnchor="end"))
    for k in [0, 1000, 2000, 3000, 4000, 5000]:
        drawing.add(String(left + width*k/5000, bottom-12, str(k), fontName="Report", fontSize=7, textAnchor="middle"))
    for rule, label, color, position in [("standard", "Standard", "#315a80", 90), ("cr_freshness", "Freshness", "#ab5936", 210), ("cr_risk", "Continuous risk", "#4c7456", 340)]:
        points = [left, bottom]
        for k, percentage in FACTS["rules"][rule]["recall"]:
            points.extend([left + width*k/5000, bottom + height*percentage/100])
        drawing.add(PolyLine(points, strokeColor=colors.HexColor(color), strokeWidth=1.2))
        drawing.add(String(position, 149, label, fontName="Report", fontSize=8, fillColor=colors.HexColor(color)))
    drawing.add(String(0, 149, "Recall (%)", fontName="Report", fontSize=8))
    drawing.add(String(left, 2, "Queue size K (transactions)", fontName="Report", fontSize=8))
    return drawing


def footer(canvas, document):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#bbbbbb"))
    canvas.setLineWidth(0.4)
    canvas.line(42, 35, A4[0]-42, 35)
    canvas.setFont("Report", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(42, 23, "24i-2514 | Design and Analysis of Algorithms | Assignment 2")
    canvas.drawRightString(A4[0]-42, 23, str(document.page))
    canvas.restoreState()


add("The Midnight Queue", "title")
add("Ranking suspicious transactions at scale<br/>Mutasim ur Rehman | 24i-2514 | Section B<br/>FAST-NUCES, Islamabad | Design and Analysis of Algorithms | Assignment 2", "subtitle")
add("0. Use of AI tools and other sources", "heading")
add("I used AI coding agents, including Codex, to help with writing and simplifying Python code, debugging, preparing plots, and improving the report. I also took help from online sources such as Stack Overflow for coding questions and from course material for algorithm theory. These tools and references supported the work; I remain responsible for the submitted code, results, and explanations.")
add("Project overview", "heading")
add("The task is to rank transactions when analysts can review only a limited number of cases. My seed is 2514, so the shift capacity is K = 25 + (2514 mod 226) = 53. I compare full sorting, top-K selection, and updates as new transactions arrive.")
add("A. Dataset and ranking rule", "heading")
add("The file contains 284,807 transactions, including 492 labelled frauds. I standardise V1 to V28 over the full file, add their squared z-scores to obtain risk, and assign band = min(9, max(0, floor(log₂(risk)))). The ranking is <b>band descending, Amount descending, Time ascending, then txn_id ascending</b>. Class is used only for evaluation.")
rows = [["Band", "Transactions", "Share", "Frauds"]]
for band in range(10):
    rows.append([band, f'{FACTS["bands"][band]:,}', f'{FACTS["bands"][band]/FACTS["n"]*100:.2f}%', FACTS["band_frauds"][band]])
table(rows, [70, 155, 120, WIDTH-345])
add(f'There are {FACTS["distinct_amounts"]:,} distinct amounts. The ten most common amounts account for {FACTS["top10_amount_share"]:.2f}% of records. Time never decreases between consecutive rows, so the raw file meets C1; this does not mean it is already in triage order.')
add("B. Implementation and testing", "heading")
add("I implemented insertion, merge, heap, and both quicksort variants, along with a size-K heap and a bounded sorted buffer. The hardened quicksort uses a median-of-three pivot, three-way partitioning, and recursion on the smaller side. These changes limit stack depth and help with duplicate bands, but its worst-case time is still O(n²).")
add("The current unittest suite has 15 test methods with subtests for algorithms, conditions, and ranking rules. It covers empty and single inputs, ties, top-K output, stable sorting, heap updates, and recursion failure. Full-key outputs are compared with sorted(); for C6, tied items may appear in different orders in unstable sorts.")

STORY.append(PageBreak())
add("C. Full-ranking experiments", "heading")
add("I used six conditions: arrival order (C1), shuffled (C2), pre-ranked (C3), reversed (C4), 1% displaced (C5), and band-only comparison (C6). The four sizes are 1,000, 10,000, 100,000, and 284,807. Each algorithm receives a fresh copy. Timing excludes loading and risk calculation.")
add("The table below uses the saved results.csv. It predates the code simplification: many small runs use five trials, expensive 10,000-row runs use three, and full-file entries use one. Some DNF points were skipped and extrapolated rather than timed to the limit. This falls short of the specified five-run median and should be rerun for final submission.", "small")
rows = [["Full file: seconds", "C1", "C2", "C3", "C4", "C5", "C6"]]
for algorithm in ALGORITHMS:
    row = [algorithm]
    for condition in ["C1", "C2", "C3", "C4", "C5", "C6"]:
        item = result(algorithm, condition, 284807)
        row.append("DNF*" if item["status"] == "DNF" else f'{float(item["time_sec"]):.3f}')
    rows.append(row)
table(rows, [WIDTH-6*58] + [58]*6)
add("* DNF values are labelled extrapolations in results.csv; they are not completed full-file timings.", "caption")
STORY.append(time_chart())
add("Figure 1. C2 runtime from results.csv. Both axes use log scales. Dashed sections are extrapolated DNF points; solid sections join completed runs.", "caption")
rows = [["C2, full file", "Comparisons", "Moves", "Auxiliary space", "Stable?"]]
for algorithm in ALGORITHMS:
    row = result(algorithm, "C2", 284807)
    suffix = "*" if row["extrapolated"] == "True" else ""
    rows.append([algorithm, f'{int(row["comparisons"]):,}'+suffix, f'{int(row["moves"]):,}'+suffix, row["space_complexity"], "Yes" if row["is_stable"] == "True" else "No"])
table(rows, [125, 100, 100, 110, WIDTH-435])
add("What I learned", "heading")
add("Insertion sort is very fast on C3 because it does not need to shift items. However, moving just 1% of the full file still creates many inversions, and C5 takes about 115 seconds. Nearly ranked data is not automatically a small job for insertion sort.")
add("Naive quicksort is fastest on saved C1 and C2 full-file runs, but it performs badly on ordered input. Merge sort gives a more consistent choice across conditions. The hardened quicksort is best on C6, yet takes 73.09 seconds on C3; median-of-three is not a guarantee of balanced partitions.")
add("Measurement notes", "heading")
add("A comparison means one call to the ranking comparator. The current counters treat a non-self swap as two moves and also count saved insertion items, shifts, and output writes. Memory figures count list slots rather than total Python process memory. Original tournament hardware was not recorded, so these timings should not be treated as portable performance claims.")

STORY.append(PageBreak())
add("D. Selecting the shift queue", "heading")
add("For a queue of 53 cases, sorting every transaction does more work than the output requires. I compare merge sort followed by slicing, a heap that keeps the best K records, and a bounded insertion buffer. The heap root is the weakest survivor, so most new records can be rejected after one comparison.")
rows = [["Method", "K", "Time (s)", "Comparisons", "Moves"]]
for row in FACTS["topk"]:
    labels = {"merge":"Full merge sort", "heap":"Size-K min-heap", "buffer":"Bounded buffer"}
    rows.append([labels[row["method"]], row["k"], f'{row["seconds"]:.4f}', f'{row["comparisons"]:,}', f'{row["moves"]:,}'])
table(rows, [125, 50, 80, 125, WIDTH-380])
add("Table 3. Fresh single-run checks on the full file in arrival order, using the current code. Copies and loading are outside the timer. These are checks, not five-run benchmark medians.", "caption")
half = FACTS["rules"]["standard"]["half_k"]
at53 = FACTS["rules"]["standard"]["at53"]
add(f'Under the standard key, K = 53 captures {at53} frauds. The smallest queue containing half of all frauds is K = {half:,}, which captures 246 cases. High risk-band membership alone does not guarantee that a transaction is fraudulent, and the Amount tie-breaker affects which cases fit in a small queue.')
STORY.append(recall_chart())
add("Figure 2. Fraud recall on the full file as queue capacity grows. Class is used only to count frauds after ranking. The alternative keys are described in Section G.", "caption")
add("E. Updating the queue over time", "heading")
add("The notebook splits the file into 48 hourly windows and 288 ten-minute windows. After each window, it publishes the best K records seen so far. The current implementation compares (a) rebuilding top-K from all history, (b) updating a persistent heap, and (c) sorting the new window and merging it with the saved queue.")
rows = [["Window schedule", "Rebuild from history", "Persistent heap", "Window sort + merge"]]
for row in FACTS["stream"]:
    rows.append([str(row["windows"])+" windows"] + [f'{value:.4f} s' for value in row["seconds"]])
table(rows, [110, 135, 120, WIDTH-365])
add("Table 4. Fresh single-run cumulative times; K = 53. Strategy (a) currently rebuilds with a top-K heap, rather than full-sorting history. That distinction matters when comparing these results with the original problem statement.", "caption")
add("A persistent heap keeps O(K) records between windows. Rebuilding retains O(n) history, while window sorting needs space for the incoming window and its merge buffer. Publishing an ordered heap queue also creates O(K) temporary output; K records is not a complete byte-level memory measurement.")

STORY.append(PageBreak())
add("F. Mathematical analysis", "heading")
add("M1. Insertion sort and inversions", "heading")
add("Let I be the number of pairs that are out of order. Each shift removes one inversion, and the outer loop visits n items, so T(n) = Θ(n + I). The best case is Θ(n), and the average and worst cases are Θ(n²). The earlier C5 analysis reports I = 262,763,679 for seed 2514; this explains why 1% displacement can still be expensive.")
add("M2. Merge sort", "heading")
add("For T(n) = 2T(n/2) + cn, repeated substitution gives T(n) = 2ʲT(n/2ʲ) + jcn. At j = log₂n, this becomes nT(1) + cn log₂n = Θ(n log n). Master's theorem gives the same answer: a = b = 2 and f(n) = Θ(n), so Case 2 applies.")
add("M3. Quicksort", "heading")
add("With an extreme pivot, T(n) = T(n - 1) + cn. Unrolling adds c[n + (n - 1) + ... + 2], giving Θ(n²). With balanced partitions, the recursion tree has log₂n levels and Θ(n) work per level, giving Θ(n log n).")
add("For a fixed 1:9 split, T(n) = T(n/10) + T(9n/10) + cn. The shortest and longest branches both have logarithmic depth. Each level costs at most cn, giving O(n log n); before the shortest branch ends, there are Θ(log n) levels carrying Θ(n) work, giving the matching lower bound. The result is Θ(n log n).")
add("M4. Building and sorting a heap", "heading")
add("Most heap nodes are close to the leaves and require little sift-down work. Summing by height gives O(n × Σ h/2ʰ) = O(n), because the series converges to 2. Heap construction is linear. The remaining n - 1 extractions each take O(log n), so total sorting time is O(n log n).")
add("M5. Top-K cost and crossover", "heading")
add("Full merge sort costs O(n log n) plus O(K) to copy the queue. Heap selection costs O(n log K), followed by O(K log K) to publish it in order. The bounded buffer has a linear rejection scan, but a qualifying insertion can shift K items, giving O(nK) worst-case time. The crossover depends on constants and the number of accepted replacements; a universal threshold such as K = 0.35n does not follow from these bounds.")
add("M6. Equal-band comparisons in naive quicksort", "heading")
pairs = FACTS["duplicate_pairs"]
add(f'In a band containing m records, each pair is compared once by strict Lomuto partitioning: m(m - 1)/2 comparisons. Summing the actual group sizes gives {pairs:,} within-band comparisons. Comparisons between different bands add to this total and depend on pivot order. Therefore, the group sizes alone do not determine the exact total comparison count. Saved large C6 totals are extrapolations, not direct full-file measurements.')
add("M7. Total work across w windows", "heading")
add("Assume equal window size m = n/w. Re-sorting all accumulated history costs Σ O(im log(im)) = O(nw log n). Rebuilding top-K from history, as the current notebook does, instead costs O(nw log K + wK log K). A persistent heap costs O(n log K + wK log K), including ordered publication. Window sort and merge costs O(n log(n/w) + wK).")
add("M8. Extra space", "heading")
add("Insertion and heap sort use O(1) extra space. Merge sort uses O(n). Naive quicksort can use O(n) stack space; the hardened smaller-side recursion uses O(log n). Both top-K selectors use O(K), including their output. These bounds describe growth, not the size of Python objects in bytes.")

STORY.append(PageBreak())
add("G. Changes to the ranking rule", "heading")
add("I compared two local change scenarios. Freshness reverses only the Time tie-breaker. Continuous risk inserts risk descending between band and Amount. Both retain txn_id as the final tie-breaker. They change queue membership and recall, while leaving the algorithms' asymptotic bounds unchanged. These scenarios still need to be matched to the actual course-portal change request.")
rows = [["Rule", "Frauds at K = 53", "Smallest K for 50% recall"]]
for key, label in [("standard","Standard"),("cr_freshness","Freshness"),("cr_risk","Continuous risk")]:
    rule = FACTS["rules"][key]
    rows.append([label,rule["at53"],f'{rule["half_k"]:,}'])
table(rows,[170,150,WIDTH-320])
add("H. My recommendations", "heading")
add("<b>Overnight batch:</b> I would use merge sort when an O(n) buffer is available. Its saved results are consistent across the six conditions, and it preserves equal-key order. If memory is too limited for the buffer, heap sort is a reasonable fallback.")
add("<b>Shift queue:</b> I would use a size-K heap when K is small relative to the file and predictable replacement cost matters. The buffer is also worth measuring for very small K, because fewer comparisons can offset its shifts. For a large queue, compare both with full sorting rather than assuming a fixed crossover.")
add("<b>Live refresh:</b> I would keep a persistent heap while scores remain fixed and the queue covers all records seen so far. If old scores change or old transactions expire, retaining only K survivors is insufficient. Historical records must be available for rescoring or replacement; simply merging the next window does not solve this.")
add("Bonus. Analyst Console", "heading")
add("The console is a separate, on-demand demonstration. It lets the analyst choose an algorithm, condition, sample size, K, and ranking rule, then shows the queue and run metrics. It does not replay the live feed. Run <b>python console.py</b> and open <b>http://127.0.0.1:8050</b>. The Python server and console.html use no external web framework.")
add("Appendix. Earlier prediction log and reflections", "heading")
rows = [["Input", "Earlier prediction", "Reflection against saved results"]]
reflections = [
    ["C1", "Merge wins; insertion loses.", "Naive quicksort is actually fastest on the full file. Merge remains the safer batch choice."],
    ["C2", "Merge wins; insertion loses.", "Naive quicksort again has the lowest saved time; insertion grows quadratically."],
    ["C3", "Insertion wins; naive quicksort loses.", "Matches the saved results. An iterative stack prevents a crash, not quadratic work."],
    ["C4", "Merge wins; insertion/naive quicksort lose.", "Merge is fastest among completed full-file runs. Both quadratic cases are extrapolated DNF."],
    ["C5", "Insertion wins; naive quicksort loses.", "Merge is fastest at full size. Insertion needs about 115 seconds despite only 1% displacement."],
    ["C6", "Hardened quicksort wins; naive quicksort loses.", "Hardened quicksort finishes in 0.191 seconds; three-way partitioning skips equal-band groups."],
]
table(rows + reflections, [45,145,WIDTH-190])
add("Sources and reproducibility", "heading")
add("Assignment brief: The Midnight Queue - Assignment 2. Data: ULB Credit Card Fraud Detection, creditcard.csv. Supporting work: results.csv, the three project notebooks, and the mathematical notes in reports/. General references: Stack Overflow for coding questions and course material for algorithm theory. Fresh checks use Python " + escape(FACTS["python"]) + "; saved tournament results came from an earlier run environment. Run tests with python -m unittest discover -s tests -v.", "small")

output = ROOT / "24i-2514-A2-B.pdf"
document = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=42, leftMargin=42, topMargin=36, bottomMargin=47, title="The Midnight Queue - Assignment 2", author="Mutasim ur Rehman", pageCompression=1)
document.build(STORY, onFirstPage=footer, onLaterPages=footer)
print(output)
