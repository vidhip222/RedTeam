# runner/runner.py
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import threading

WRITE_LOCK = threading.Lock()

def load_attacks(file_path):
    with open(file_path, "r", encoding="utf8") as f:
        return json.load(f)

def save_result_atomic(out_path, item):
    with WRITE_LOCK:
        with open(out_path, "a", encoding="utf8") as f:
            f.write(json.dumps(item) + "\n")

def run_attack(attack, model_client, out_path):
    attack_id = attack.get("attack_id")
    prompt = attack.get("prompt")
    ts = datetime.utcnow().isoformat() + "Z"
    try:
        res = model_client.query(attack_id, prompt)
        item = {
            "attack_id": attack_id,
            "prompt": prompt,
            "response": res["text"],
            "model_meta": res.get("meta", {}),
            "timestamp": ts
        }
    except Exception as e:
        item = {
            "attack_id": attack_id,
            "prompt": prompt,
            "response": "",
            "error": str(e),
            "model_meta": {},
            "timestamp": ts
        }
    save_result_atomic(out_path, item)
    return item

def run_all(attacks, model_client, out_path="data/results.jsonl", max_workers=4):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    # clear file
    open(out_path, "w", encoding="utf8").close()
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(run_attack, a, model_client, out_path): a for a in attacks}
        for fut in as_completed(futures):
            try:
                r = fut.result()
                results.append(r)
            except Exception as e:
                print("Error in worker:", e)
    return results
