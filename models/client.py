# models/client.py
import time
import json
import os
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

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

    def _get_llm(self, temperature, max_tokens):
        models = {
            "openai": lambda: ChatOpenAI(
                model="gpt-4o-mini",
                temperature=1.0,
                max_tokens=max_tokens,
                api_key=self.api_key
            ),
            "gemini": lambda: ChatGoogleGenerativeAI(
                model='gemini-2.5-flash',
                temperature=temperature,
                max_tokens=max_tokens,
                google_api_key=self.api_key
            )
            # TODO: Add additional llms here
        }
        model = models.get(self.provider)
        if not model:
            raise ValueError(f"Unkown or unsupported provider: {self.provider}")
        return model

    def sanitize_input(self, prompt):
        if not self.sanitize:
            return prompt, {}
        # simple sanitization: remove 'ignore previous' phrases
        replaced = prompt.replace("Ignore previous instructions", "[sanitized]")
        meta = {"sanitized": True}
        return replaced, meta

    def query(self, attack_id, prompt, max_tokens=200, temperature=1.0, **kwargs):
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
    
        if not self.api_key:
            raise RuntimeError(f"{self.provider} provider requested but no API key provided")

        llm = self._get_llm(temperature=temperature, max_tokens=max_tokens)
        response = llm.invoke(prompt)
        text = response.content
        meta = {"mock": False, "provider": self.provider}
        self._log(attack_id, prompt, meta)
        return {"text": text, "meta": meta}