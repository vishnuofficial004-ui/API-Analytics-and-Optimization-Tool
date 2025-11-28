# tests/test_edge_cases.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from function import analyze_api_logs

def test_empty_logs():
    result = analyze_api_logs([])
    assert result["summary"] == {}
    assert result["endpoint_stats"] == []
    assert result["performance_issues"] == []

def test_single_log():
    logs = [{
        "timestamp": "2025-01-15T10:00:00Z",
        "endpoint": "/api/test",
        "method": "GET",
        "response_time_ms": 100,
        "status_code": 200,
        "user_id": "user_1",
        "request_size_bytes": 100,
        "response_size_bytes": 200
    }]
    result = analyze_api_logs(logs)
    assert result["summary"]["total_requests"] == 1
    assert result["endpoint_stats"][0]["request_count"] == 1

def test_malformed_logs():
    logs = [{"timestamp": "invalid-date"}]
    result = analyze_api_logs(logs)
    assert result["summary"] == {}
