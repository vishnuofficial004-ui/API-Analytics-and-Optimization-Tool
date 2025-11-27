import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from function import analyze_api_logs

def test_empty_logs():
    result = analyze_api_logs([])
    assert result["summary"] == {}
    assert result["endpoint_stats"] == []

def test_single_valid_log():
    logs = [{
        "timestamp": "2025-01-15T10:00:00Z",
        "endpoint": "/api/users",
        "method": "GET",
        "response_time_ms": 100,
        "status_code": 200,
        "user_id": "user_1",
        "request_size_bytes": 512,
        "response_size_bytes": 1024
    }]
    result = analyze_api_logs(logs)
    assert result["summary"]["total_requests"] == 1
    assert result["summary"]["avg_response_time_ms"] == 100
    assert result["summary"]["error_rate_percentage"] == 0.0
    assert result["summary"]["time_range"]["start"] == "2025-01-15T10:00:00Z"
    assert result["summary"]["time_range"]["end"] == "2025-01-15T10:00:00Z"

def test_summary_statistics():
    logs = [
        {"timestamp": "2025-01-15T10:00:00Z", "endpoint": "/api/users", "method": "GET",
         "response_time_ms": 100, "status_code": 200, "user_id": "user_1",
         "request_size_bytes": 512, "response_size_bytes": 1024},
        {"timestamp": "2025-01-15T10:05:00Z", "endpoint": "/api/payments", "method": "POST",
         "response_time_ms": 500, "status_code": 500, "user_id": "user_2",
         "request_size_bytes": 1024, "response_size_bytes": 512},
    ]
    result = analyze_api_logs(logs)
    summary = result["summary"]

    assert summary["total_requests"] == 2
    assert summary["time_range"]["start"] == "2025-01-15T10:00:00Z"
    assert summary["time_range"]["end"] == "2025-01-15T10:05:00Z"
    assert summary["avg_response_time_ms"] == 300  # (100+500)/2
    assert summary["error_rate_percentage"] == 50.0  # 1 out of 2 logs

if __name__ == "__main__":
    test_empty_logs()
    test_single_valid_log()
    test_summary_statistics()
    print("All Step 3 tests passed!")
