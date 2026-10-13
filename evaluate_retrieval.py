import json
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.retrieval_agent import search

# 1. Load evaluation questions using project-root relative path
eval_file = PROJECT_ROOT / "evaluation" / "eval_questions.json"
with open(eval_file, "r", encoding="utf-8") as f:
    test_cases = json.load(f)

recall_correct = 0
reciprocal_ranks = []
total = len(test_cases)
report_lines = []

def log_and_record(line: str):
    print(line)
    report_lines.append(line)

log_and_record("=" * 60)
log_and_record("CareerCompass RAG Retrieval Evaluation")
log_and_record("=" * 60)

for i, test in enumerate(test_cases, start=1):
    question = test["question"]
    category = test["category"]
    expected_source = test["expected_source"]

    # 3. Call existing retrieval function
    results = search(
        query_text=question,
        category=category,
        top_k=5
    )

    retrieved_sources = [
        result["source"]
        for result in results
    ]

    # Calculate Rank of Expected Source
    if expected_source in retrieved_sources:
        rank = retrieved_sources.index(expected_source) + 1
        reciprocal_rank = 1.0 / rank
        is_correct = True
        recall_correct += 1
        rank_str = str(rank)
    else:
        rank = None
        reciprocal_rank = 0.0
        is_correct = False
        rank_str = "Not found"

    reciprocal_ranks.append(reciprocal_rank)

    log_and_record(f"\nTest {i}: {question}")
    log_and_record(f"Expected source         : {expected_source}")
    log_and_record(f"Retrieved sources       : {retrieved_sources}")
    log_and_record(f"Rank of Expected Source : {rank_str}")
    log_and_record(f"Result                  : {'PASS' if is_correct else 'FAIL'}")

# 4. Calculate Recall@5
recall_at_5 = (recall_correct / total) * 100 if total > 0 else 0.0

# 5. Calculate MRR
mrr = (sum(reciprocal_ranks) / total) if total > 0 else 0.0
mrr_percentage = mrr * 100

# 6. Generate results summary
log_and_record("\n" + "=" * 60)
log_and_record("CareerCompass RAG Retrieval Evaluation Summary")
log_and_record("=" * 60)
log_and_record(f"Total Tests       : {total}")
log_and_record(f"Correct Retrieval : {recall_correct}")
log_and_record(f"Recall@5          : {recall_at_5:.2f}%")
log_and_record(f"MRR               : {mrr:.4f}")
log_and_record(f"MRR Percentage    : {mrr_percentage:.2f}%")
log_and_record("=" * 60)

# Ensure results directory exists
results_dir = PROJECT_ROOT / "evaluation" / "results"
results_dir.mkdir(parents=True, exist_ok=True)

# 7. Generate comparative graph using actual measured values
graph_path = results_dir / "careercompass_retrieval_performance.png"

metrics = ["Recall@5", "MRR"]
values = [recall_at_5, mrr_percentage]
colors = ["#2563EB", "#10B981"]

plt.figure(figsize=(7, 5), dpi=300)
bars = plt.bar(metrics, values, color=colors, width=0.45, edgecolor="#1F2937", linewidth=1.2)

plt.title("CareerCompass RAG Retrieval Performance", fontsize=14, fontweight="bold", pad=15)
plt.xlabel("Evaluation Metric", fontsize=12, fontweight="semibold", labelpad=10)
plt.ylabel("Performance (%)", fontsize=12, fontweight="semibold", labelpad=10)
plt.ylim(0, 110)
plt.grid(axis="y", linestyle="--", alpha=0.5)

for bar, val in zip(bars, values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 2.5,
        f"{val:.2f}%",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold"
    )

plt.tight_layout()
plt.savefig(graph_path)
plt.close()
log_and_record(f"\n[Graph generated] Saved to: {graph_path}")

# 8. Generate evaluation report files
report_file = results_dir / "evaluation_report.txt"
with open(report_file, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines) + "\n")
log_and_record(f"[Report generated] Saved to: {report_file}")

results_json_file = results_dir / "evaluation_results.json"
results_payload = {
    "total_tests": total,
    "correct_retrieval": recall_correct,
    "recall_at_5": round(recall_at_5, 2),
    "mrr": round(mrr, 4)
}
with open(results_json_file, "w", encoding="utf-8") as f:
    json.dump(results_payload, f, indent=4)
log_and_record(f"[JSON results generated] Saved to: {results_json_file}")