# tests/test_attack_schema.py
import json
def test_sample_attacks_file_exists():
    with open("data/sample_attack_cases.json","r",encoding="utf8") as f:
        arr = json.load(f)
    assert isinstance(arr, list)
    assert len(arr) >= 1
    for it in arr:
        assert "attack_id" in it and "prompt" in it and "tags" in it
