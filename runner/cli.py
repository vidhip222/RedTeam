# runner/cli.py
import argparse
import json
from models.client import ModelClient
from runner.runner import load_attacks, run_all

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="mock", choices=["mock","openai"])
    p.add_argument("--attacks-file", default="data/sample_attack_cases.json")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--api-key", default=None)
    args = p.parse_args()

    attacks = load_attacks(args.attacks_file)
    client = ModelClient(provider=args.model, api_key=args.api_key, sanitize=False)
    print(f"Running {len(attacks)} attacks with model={args.model} workers={args.workers}")
    run_all(attacks, client, out_path="data/results.jsonl", max_workers=args.workers)
    print("Done. results -> data/results.jsonl")

if __name__ == "__main__":
    main()
