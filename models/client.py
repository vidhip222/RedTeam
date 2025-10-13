# models/client.py
import time
import json
import os
from datetime import datetime

class ModelClient:
    def __init__(self, provider="mock", api_key=None, sanitize=False):
        self.provider = provider
        self.api_key = api_key
        self.sanitize = sanitize
        os.makedirs("data", exist_ok=True)
        self.log_path = os.path.join("data", "model_calls.log")

    def _log(self, attack_id, prompt, meta=None):
        entry = {
            "ts": datetime.utcnow().isoformat()+"Z",
            "attack_id": attack_id,
            "prompt_trunc": prompt[:400],
            "meta": meta or {}
        }
        with open(self.log_path, "a", encoding="utf8") as f:
            f.write(json.dumps(entry) + "\n")

    def sanitize_input(self, prompt):
        if not self.sanitize:
            return prompt, {}
        # simple sanitization: remove 'ignore previous' phrases
        replaced = prompt.replace("Ignore previous instructions", "[sanitized]")
        meta = {"sanitized": True}
        return replaced, meta

    def query(self, attack_id, prompt, max_tokens=200, **kwargs):
        if self.sanitize:
            prompt, smeta = self.sanitize_input(prompt)
        else:
            smeta = {}
        if self.provider == "mock":
            from models.mock import mock_response_for_attack
            resp = mock_response_for_attack(attack_id, prompt)
            meta = {"mock": True}
            self._log(attack_id, prompt, meta)
            return {"text": resp, "meta": meta}
        elif self.provider == "openai":
            # Minimal HTTP wrapper (placeholder) - requires API key
            if not self.api_key:
                raise RuntimeError("OpenAI provider requested but no API key provided.")
            import requests
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "model": kwargs.get("model", "gpt-4o-mini"),
                "messages": [{"role":"user", "content": prompt}],
                "max_tokens": max_tokens
            }
            r = requests.post(url, json=payload, headers=headers, timeout=20)
            r.raise_for_status()
            j = r.json()
            text = j["choices"][0]["message"]["content"]
            meta = {"mock": False, "provider": "openai"}
            self._log(attack_id, prompt, meta)
            return {"text": text, "meta": meta}
        else:
            raise ValueError("Unknown provider: " + str(self.provider))
