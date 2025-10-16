"""
Metrics computation and aggregation for red-teaming evaluation.
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict, Counter
from datetime import datetime


class MetricsComputer:
    """Computes aggregate metrics from scored results."""
    
    def __init__(self, score_report_file: str = "data/score_report.json"):
        """
        Initialize metrics computer.
        
        Args:
            score_report_file: Path to score report JSON
        """
        self.score_report_file = Path(score_report_file)
        self.scores = []
        self.metadata = {}
    
    def load_scores(self):
        """Load scores from report file."""
        if not self.score_report_file.exists():
            raise FileNotFoundError(f"Score report not found: {self.score_report_file}")
        
        with open(self.score_report_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.metadata = data.get("metadata", {})
            self.scores = data.get("scores", [])
        
        print(f"Loaded {len(self.scores)} scored results.")
    
    def compute_success_rate_per_tag(self) -> Dict[str, Dict[str, Any]]:
        """
        Compute success rate (vulnerability rate) per tag.
        
        Returns:
            Dictionary mapping tag -> metrics
        """
        tag_stats = defaultdict(lambda: {"total": 0, "vulnerable": 0, "severities": []})
        
        for score in self.scores:
            tags = score.get("tags", ["untagged"])
            is_vulnerable = score.get("vulnerable", False)
            severity = score.get("severity_score", 0.0)
            
            for tag in tags:
                tag_stats[tag]["total"] += 1
                if is_vulnerable:
                    tag_stats[tag]["vulnerable"] += 1
                    tag_stats[tag]["severities"].append(severity)
        
        result = {}
        for tag, stats in tag_stats.items():
            success_rate = stats["vulnerable"] / stats["total"] if stats["total"] > 0 else 0.0
            avg_severity = (
                sum(stats["severities"]) / len(stats["severities"]) 
                if stats["severities"] else 0.0
            )
            
            result[tag] = {
                "total_attacks": stats["total"],
                "successful_attacks": stats["vulnerable"],
                "success_rate": round(success_rate, 3),
                "average_severity": round(avg_severity, 3),
                "max_severity": round(max(stats["severities"], default=0.0), 3)
            }
        
        return result
    
    def compute_top_vulnerable_attacks(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Find the top N most vulnerable attacks (highest severity).
        
        Args:
            top_n: Number of top attacks to return
            
        Returns:
            List of top attack summaries
        """
        vulnerable_scores = [s for s in self.scores if s.get("vulnerable", False)]
        
        sorted_scores = sorted(
            vulnerable_scores,
            key=lambda x: x.get("severity_score", 0.0),
            reverse=True
        )
        
        top_attacks = []
        for score in sorted_scores[:top_n]:
            top_attacks.append({
                "attack_id": score.get("attack_id"),
                "severity_score": score.get("severity_score"),
                "vulnerability_reasons": score.get("vulnerability_reasons", []),
                "evidence_count": score.get("evidence_count", 0),
                "tags": score.get("tags", []),
                "notes": score.get("notes", "")
            })
        
        return top_attacks
    
    def compute_vulnerability_type_distribution(self) -> Dict[str, int]:
        """
        Compute distribution of vulnerability types.
        
        Returns:
            Dictionary mapping vulnerability type -> count
        """
        type_counter = Counter()
        
        for score in self.scores:
            if score.get("vulnerable", False):
                reasons = score.get("vulnerability_reasons", [])
                for reason in reasons:
                    type_counter[reason] += 1
        
        return dict(type_counter)
    
    def compute_severity_distribution(self) -> Dict[str, int]:
        """
        Compute distribution of severity scores.
        
        Returns:
            Dictionary with severity buckets
        """
        severity_buckets = {
            "critical (0.8-1.0)": 0,
            "high (0.6-0.8)": 0,
            "medium (0.4-0.6)": 0,
            "low (0.0-0.4)": 0
        }
        
        for score in self.scores:
            if not score.get("vulnerable", False):
                continue
            
            severity = score.get("severity_score", 0.0)
            
            if severity >= 0.8:
                severity_buckets["critical (0.8-1.0)"] += 1
            elif severity >= 0.6:
                severity_buckets["high (0.6-0.8)"] += 1
            elif severity >= 0.4:
                severity_buckets["medium (0.4-0.6)"] += 1
            else:
                severity_buckets["low (0.0-0.4)"] += 1
        
        return severity_buckets
    
    def compute_all_metrics(self) -> Dict[str, Any]:
        """
        Compute all metrics.
        
        Returns:
            Dictionary containing all computed metrics
        """
        self.load_scores()
        
        metrics = {
            "summary": {
                "total_attacks": len(self.scores),
                "vulnerable_attacks": sum(1 for s in self.scores if s.get("vulnerable")),
                "overall_success_rate": round(
                    sum(1 for s in self.scores if s.get("vulnerable")) / len(self.scores), 3
                ) if self.scores else 0.0,
                "average_severity": round(
                    sum(s.get("severity_score", 0) for s in self.scores) / len(self.scores), 3
                ) if self.scores else 0.0,
            },
            "success_rate_per_tag": self.compute_success_rate_per_tag(),
            "top_vulnerable_attacks": self.compute_top_vulnerable_attacks(top_n=5),
            "vulnerability_type_distribution": self.compute_vulnerability_type_distribution(),
            "severity_distribution": self.compute_severity_distribution(),
            "metadata": {
                "computed_at": datetime.now().isoformat(),
                "source_report": str(self.score_report_file)
            }
        }
        
        return metrics
    
    def save_metrics(self, output_file: str = "data/metrics.json"):
        """Save computed metrics to JSON file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        metrics = self.compute_all_metrics()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        
        print(f"Metrics saved to: {output_path}")
        self._print_summary(metrics)
        
        return output_path
    
    def _print_summary(self, metrics: Dict[str, Any]):
        """Print a human-readable summary of metrics."""
        print("\n" + "=" * 60)
        print("METRICS SUMMARY")
        print("=" * 60)
        
        summary = metrics["summary"]
        print(f"\nTotal Attacks: {summary['total_attacks']}")
        print(f"Vulnerable: {summary['vulnerable_attacks']} ({summary['overall_success_rate']:.1%})")
        print(f"Average Severity: {summary['average_severity']:.2f}")
        
        print("\n--- Top Vulnerable Attacks ---")
        for i, attack in enumerate(metrics["top_vulnerable_attacks"], 1):
            print(f"{i}. {attack['attack_id']} (severity: {attack['severity_score']:.2f})")
            print(f"   Reasons: {', '.join(attack['vulnerability_reasons'])}")
        
        print("\n--- Success Rate by Tag ---")
        for tag, stats in sorted(
            metrics["success_rate_per_tag"].items(),
            key=lambda x: x[1]["success_rate"],
            reverse=True
        )[:10]:
            print(f"{tag}: {stats['success_rate']:.1%} ({stats['successful_attacks']}/{stats['total_attacks']})")
        
        print("\n" + "=" * 60)


def main():
    """Main entry point for metrics computation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Compute evaluation metrics")
    parser.add_argument(
        "--report",
        default="data/score_report.json",
        help="Path to score report JSON"
    )
    parser.add_argument(
        "--output",
        default="data/metrics.json",
        help="Path to output metrics file"
    )
    
    args = parser.parse_args()
    
    computer = MetricsComputer(score_report_file=args.report)
    computer.save_metrics(output_file=args.output)


if __name__ == "__main__":
    main()