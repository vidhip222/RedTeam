# eval/metrics.py
import json
from collections import defaultdict

def load_scores(path="data/score_report.json"):
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)

def compute_metrics(scores):
    per_tag = defaultdict(lambda: {"total":0,"vulnerable":0})
    for s in scores:
        # attack_id may encode tag; for now use severity buckets
        sev = s.get("severity_score", 0.0)
        bucket = "high" if sev >= 0.9 else ("medium" if sev >= 0.5 else "low")
        per_tag[bucket]["total"] += 1
        if s.get("vuln_bool"):
            per_tag[bucket]["vulnerable"] += 1
    return per_tag

if __name__ == "__main__":
    scores = load_scores()
    print(compute_metrics(scores))
