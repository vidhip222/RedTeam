# tests/test_retry_functionality.py
import pytest
import time
from unittest.mock import Mock, patch
from runner.runner import safe_query

class MockModelClient:
    def __init__(self, should_fail_times=0, failure_type="network"):
        self.call_count = 0
        self.should_fail_times = should_fail_times
        self.failure_type = failure_type
    
    def query(self, attack_id, prompt):
        self.call_count += 1
        if self.call_count <= self.should_fail_times:
            if self.failure_type == "network":
                raise ConnectionError("Connection timeout")
            else:
                raise ValueError("Non-network error")
        return {"text": "Success response", "meta": {"attempt": self.call_count}}

def test_safe_query_success_on_first_try():
    """Test that safe_query succeeds immediately when no errors occur."""
    client = MockModelClient(should_fail_times=0)
    result = safe_query(client, "test-01", "test prompt")
    
    assert result["text"] == "Success response"
    assert client.call_count == 1

def test_safe_query_retries_network_errors():
    """Test that safe_query retries network errors with exponential backoff."""
    client = MockModelClient(should_fail_times=2, failure_type="network")
    
    start_time = time.time()
    result = safe_query(client, "test-01", "test prompt")
    end_time = time.time()
    
    assert result["text"] == "Success response"
    assert client.call_count == 3  # 2 failures + 1 success
    # Should have taken some time due to backoff delays
    assert end_time - start_time > 1.0

def test_safe_query_fails_non_network_errors():
    """Test that safe_query doesn't retry non-network errors."""
    client = MockModelClient(should_fail_times=1, failure_type="non_network")
    
    with pytest.raises(ValueError, match="Non-network error"):
        safe_query(client, "test-01", "test prompt")
    
    assert client.call_count == 1  # Should not retry

def test_safe_query_exhausts_retries():
    """Test that safe_query raises exception after exhausting all retries."""
    client = MockModelClient(should_fail_times=5, failure_type="network")
    
    with pytest.raises(ConnectionError, match="Connection timeout"):
        safe_query(client, "test-01", "test prompt")
    
    assert client.call_count == 4  # 3 retries + 1 initial attempt

def test_safe_query_with_custom_max_retries():
    """Test that safe_query respects custom max_retries parameter."""
    client = MockModelClient(should_fail_times=3, failure_type="network")
    
    with pytest.raises(ConnectionError, match="Connection timeout"):
        safe_query(client, "test-01", "test prompt", max_retries=1)
    
    assert client.call_count == 2  # 1 retry + 1 initial attempt
