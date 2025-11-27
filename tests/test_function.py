import sys 
import os 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from function import analyze_api_logs

def test_endpoint_statistics():
    logs = [
        {"timestamp": "2025-01-15T10:00:00Z", "endpoint": "/api/users", "method": "GET",
         "response_time_ms": 100, "status_code": 200, "user_id": "user_1",
         "request_size_bytes": 512, "response_size_bytes": 1024},
        {"timestamp": "2025-01-15T10:05:00Z", "endpoint": "/api/users", "method": "GET",
         "response_time_ms": 200, "status_code": 404, "user_id": "user_2",
         "request_size_bytes": 512, "response_size_bytes": 1024},
        {"timestamp": "2025-01-15T10:10:00Z", "endpoint": "/api/payments", "method": "POST",
         "response_time_ms": 500, "status_code": 500, "user_id": "user_1",
         "request_size_bytes": 1024, "response_size_bytes": 512}
    ]
    result = analyze_api_logs(logs)
    endpoints = {e["endpoint"]: e for e in result["endpoint_stats"]}

    # /api/users stats
    users_stats = endpoints["/api/users"]
    assert users_stats["request_count"] == 2
    assert users_stats["avg_response_time_ms"] == 150  # (100+200)/2
    assert users_stats["slowest_request_ms"] == 200
    assert users_stats["fastest_request_ms"] == 100
    assert users_stats["error_count"] == 1
    assert users_stats["most_common_status"] == 200

    # /api/payments stats
    payments_stats = endpoints["/api/payments"]
    assert payments_stats["request_count"] == 1
    assert payments_stats["avg_response_time_ms"] == 500
    assert payments_stats["slowest_request_ms"] == 500
    assert payments_stats["fastest_request_ms"] == 500
    assert payments_stats["error_count"] == 1
    assert payments_stats["most_common_status"] == 500

if __name__ == "__main__":
    test_endpoint_statistics()
    print("Step 4 tests passed!")
