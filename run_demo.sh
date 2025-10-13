#!/usr/bin/env bash
# quick demo script (unix)
set -e
python attacks/generator.py
python runner/cli.py --model=mock --attacks-file=data/sample_attack_cases.json --workers=4
python eval/scorer.py --results=data/results.jsonl --out=data/score_report.json
echo "To view: streamlit run ui/app.py"
