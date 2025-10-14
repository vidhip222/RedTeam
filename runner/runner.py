# runner/runner.py
import json
import os
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import threading

WRITE_LOCK = threading.Lock()

def safe_query(model_client, attack_id, prompt, max_retries=3):
    """
    Retry wrapper for model queries with exponential backoff on network errors.
    
    Args:
        model_client: The model client instance
        attack_id: Attack identifier for logging
        prompt: The prompt to send to the model
        max_retries: Maximum number of retry attempts (default: 3)
    
    Returns:
        dict: Model response with text and metadata
        
    Raises:
        Exception: If all retries are exhausted
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):  # +1 for initial attempt
        try:
            return model_client.query(attack_id, prompt)
        except Exception as e:
            last_exception = e
            
            # Check if this is a network-related error
            error_str = str(e).lower()
            error_type = type(e).__name__.lower()
            
            # Exclude errors that explicitly say "non-network"
            if 'non-network' in error_str:
                is_network_error = False
            else:
                is_network_error = (
                    any(keyword in error_str for keyword in [
                        'timeout', 'connection', 'network', 'http', 'request', 'socket'
                    ]) or
                    any(keyword in error_type for keyword in [
                        'connection', 'timeout', 'network', 'http'
                    ])
                )
            
            # If it's not a network error or we're on the last attempt, re-raise
            if not is_network_error or attempt == max_retries:
                raise e
            
            # Calculate exponential backoff with jitter
            base_delay = 2 ** attempt  # 1, 2, 4 seconds
            jitter = random.uniform(0.1, 0.5)  # Add 0.1-0.5s random jitter
            delay = base_delay + jitter
            
            print(f"Network error on attempt {attempt + 1}/{max_retries + 1} for attack {attack_id}: {e}")
            print(f"Retrying in {delay:.1f} seconds...")
            time.sleep(delay)
    
    # This should never be reached, but just in case
    raise last_exception

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
        res = safe_query(model_client, attack_id, prompt)
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
