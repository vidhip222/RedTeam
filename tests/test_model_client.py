# tests/test_model_client.py
from models.client import ModelClient

def test_mock_client_returns_text():
    c = ModelClient(provider="mock")
    out = c.query("jb-01", "dummy")
    assert "text" in out
    assert isinstance(out["text"], str)
