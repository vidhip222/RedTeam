# tests/test_runner_end_to_end.py
import os, json
from runner.runner import run_all, load_attacks
from models.client import ModelClient

def test_run_end_to_end(tmp_path):
    attacks = load_attacks("data/sample_attack_cases.json")
    client = ModelClient(provider="mock")
    out = tmp_path / "res.jsonl"
    run_all(attacks[:3], client, out_path=str(out), max_workers=2)
    with open(out, "r", encoding="utf8") as f:
        lines = [json.loads(l) for l in f if l.strip()]
    assert len(lines) == 3
