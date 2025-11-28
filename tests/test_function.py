import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from function import analyze_api_logs

# -------------------------
# Step 4: Endpoint Statistics
# -------------------------
def test_endpoint_statistics():
    """Step 4: Test endpoint statistics calculation."""
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

    users_stats = endpoints["/api/users"]
    assert users_stats["request_count"] == 2
    assert users_stats["avg_response_time_ms"] == 150
    assert users_stats["slowest_request_ms"] == 200
    assert users_stats["fastest_request_ms"] == 100
    assert users_stats["error_count"] == 1
    assert users_stats["most_common_status"] == 200

    payments_stats = endpoints["/api/payments"]
    assert payments_stats["request_count"] == 1
    assert payments_stats["avg_response_time_ms"] == 500
    assert payments_stats["slowest_request_ms"] == 500
    assert payments_stats["fastest_request_ms"] == 500
    assert payments_stats["error_count"] == 1
    assert payments_stats["most_common_status"] == 500


# -------------------------
# Step 5: Performance Issues
# -------------------------
def test_performance_issues():
    """Step 5: Test detection of slow endpoints and high error rates with correct severities."""
    logs = [
        {"timestamp": "2025-01-15T10:00:00Z", "endpoint": "/api/users", "method": "GET",
         "response_time_ms": 600, "status_code": 200, "user_id": "user_1",
         "request_size_bytes": 512, "response_size_bytes": 1024},
        {"timestamp": "2025-01-15T10:05:00Z", "endpoint": "/api/users", "method": "GET",
         "response_time_ms": 700, "status_code": 500, "user_id": "user_2",
         "request_size_bytes": 512, "response_size_bytes": 1024},
        {"timestamp": "2025-01-15T10:10:00Z", "endpoint": "/api/payments", "method": "POST",
         "response_time_ms": 1100, "status_code": 500, "user_id": "user_1",
         "request_size_bytes": 1024, "response_size_bytes": 512}
    ]
    result = analyze_api_logs(logs)
    issues = result["performance_issues"]

    users_slow = [i for i in issues if i.get("endpoint") == "/api/users" and i["type"] == "slow_endpoint"]
    assert users_slow[0]["severity"] == "medium"

    users_error = [i for i in issues if i.get("endpoint") == "/api/users" and i["type"] == "high_error_rate"]
    assert users_error[0]["severity"] == "critical"

    payments_slow = [i for i in issues if i.get("endpoint") == "/api/payments" and i["type"] == "slow_endpoint"]
    assert payments_slow[0]["severity"] == "high"

    payments_error = [i for i in issues if i.get("endpoint") == "/api/payments" and i["type"] == "high_error_rate"]
    assert payments_error[0]["severity"] == "critical"


# -------------------------
# Step 6: Payload Insights
# -------------------------
def test_payload_insights():
    """Step 6: Test request/response size analytics."""
    logs = [
        {"timestamp": "2025-01-15T10:00:00Z", "endpoint": "/api/users", "method": "GET",
         "response_time_ms": 120, "status_code": 200, "user_id": "user_1",
         "request_size_bytes": 300, "response_size_bytes": 600},
        {"timestamp": "2025-01-15T10:05:00Z", "endpoint": "/api/users", "method": "POST",
         "response_time_ms": 180, "status_code": 201, "user_id": "user_2",
         "request_size_bytes": 700, "response_size_bytes": 900},
        {"timestamp": "2025-01-15T10:10:00Z", "endpoint": "/api/orders", "method": "POST",
         "response_time_ms": 500, "status_code": 200, "user_id": "user_3",
         "request_size_bytes": 1500, "response_size_bytes": 2500}
    ]

    result = analyze_api_logs(logs)
    size_stats = result["size_insights"]

    assert size_stats["avg_request_size_bytes"] == (300 + 700 + 1500) / 3
    assert size_stats["avg_response_size_bytes"] == (600 + 900 + 2500) / 3
    assert size_stats["largest_request"]["request_size_bytes"] == 1500
    assert size_stats["largest_request"]["endpoint"] == "/api/orders"
    assert size_stats["largest_response"]["response_size_bytes"] == 2500
    assert size_stats["largest_response"]["endpoint"] == "/api/orders"


# -------------------------
# Step 7: Hourly Distribution
# -------------------------
def test_hourly_distribution():
    """Step 7: Test hourly request distribution."""
    logs = [
        {"timestamp": "2025-01-15T10:00:00Z", "endpoint": "/api/users", "method": "GET",
         "response_time_ms": 120, "status_code": 200, "user_id": "user_1",
         "request_size_bytes": 300, "response_size_bytes": 600},
        {"timestamp": "2025-01-15T10:15:00Z", "endpoint": "/api/orders", "method": "POST",
         "response_time_ms": 500, "status_code": 200, "user_id": "user_2",
         "request_size_bytes": 500, "response_size_bytes": 800},
        {"timestamp": "2025-01-15T11:05:00Z", "endpoint": "/api/users", "method": "GET",
         "response_time_ms": 150, "status_code": 200, "user_id": "user_3",
         "request_size_bytes": 400, "response_size_bytes": 700}
    ]

    result = analyze_api_logs(logs)
    hourly = result["hourly_distribution"]

    assert hourly["10:00"] == 2
    assert hourly["11:00"] == 1


# -------------------------
# Step 8: Top Users
# -------------------------
def test_top_users_by_requests():
    """Step 8: Test top users by request count."""
    logs = [
        {"timestamp": "2025-01-15T10:00:00Z", "endpoint": "/api/users", "method": "GET",
         "response_time_ms": 120, "status_code": 200, "user_id": "user_1",
         "request_size_bytes": 300, "response_size_bytes": 600},
        {"timestamp": "2025-01-15T10:05:00Z", "endpoint": "/api/users", "method": "POST",
         "response_time_ms": 180, "status_code": 201, "user_id": "user_2",
         "request_size_bytes": 700, "response_size_bytes": 900},
        {"timestamp": "2025-01-15T10:10:00Z", "endpoint": "/api/orders", "method": "POST",
         "response_time_ms": 500, "status_code": 200, "user_id": "user_1",
         "request_size_bytes": 1500, "response_size_bytes": 2500}
    ]

    result = analyze_api_logs(logs)
    top_users = result["top_users_by_requests"]

    assert top_users[0]["user_id"] == "user_1"
    assert top_users[0]["request_count"] == 2
    assert top_users[1]["user_id"] == "user_2"
    assert top_users[1]["request_count"] == 1


# -------------------------
# Step 9: Recommendations
# -------------------------
def test_recommendations():
    """Step 9: Test recommendations generation."""
    logs = []
    for i in range(12):
        logs.append({
            "timestamp": f"2025-01-15T12:{i:02}:00Z",
            "endpoint": "/api/cache",
            "method": "GET",
            "response_time_ms": 100,
            "status_code": 200,
            "user_id": f"user_{i}",
            "request_size_bytes": 100,
            "response_size_bytes": 200
        })
    logs.append({
        "timestamp": "2025-01-15T13:00:00Z",
        "endpoint": "/api/slow",
        "method": "POST",
        "response_time_ms": 600,
        "status_code": 500,
        "user_id": "user_99",
        "request_size_bytes": 200,
        "response_size_bytes": 300
    })

    result = analyze_api_logs(logs)
    recs = result["recommendations"]

    cache_suggestion = [r for r in recs if "/api/cache" in r]
    assert len(cache_suggestion) == 1

    slow_suggestion = [r for r in recs if "/api/slow" in r and "performance" in r]
    assert len(slow_suggestion) == 1

    error_suggestion = [r for r in recs if "/api/slow" in r and "error rate" in r]
    assert len(error_suggestion) == 1


# -------------------------
# Step 10: Anomaly Detection
# -------------------------
def test_anomaly_detection():
    """Step 10: Test detection of response time spikes and server errors."""
    logs = [
        {"timestamp": "2025-01-15T10:00:00Z", "endpoint": "/api/users", "method": "GET",
         "response_time_ms": 100, "status_code": 200, "user_id": "user_1",
         "request_size_bytes": 512, "response_size_bytes": 1024},
        {"timestamp": "2025-01-15T10:05:00Z", "endpoint": "/api/users", "method": "GET",
         "response_time_ms": 500, "status_code": 200, "user_id": "user_2",
         "request_size_bytes": 512, "response_size_bytes": 1024},
        {"timestamp": "2025-01-15T10:10:00Z", "endpoint": "/api/payments", "method": "POST",
         "response_time_ms": 1500, "status_code": 200, "user_id": "user_1",
         "request_size_bytes": 1024, "response_size_bytes": 512},
        {"timestamp": "2025-01-15T10:15:00Z", "endpoint": "/api/payments", "method": "POST",
         "response_time_ms": 300, "status_code": 500, "user_id": "user_3",
         "request_size_bytes": 1024, "response_size_bytes": 512}
    ]

    result = analyze_api_logs(logs)
    anomalies = result["anomalies"]

    # Response time spikes
    spikes = anomalies["response_time_spikes"]
    spike_endpoints = [log["endpoint"] for log in spikes]
    assert "/api/payments" in spike_endpoints

    # Server errors
    server_errors = anomalies["server_errors"]
    assert len(server_errors) == 1
    assert server_errors[0]["status_code"] == 500

    # Suspicious endpoints and users
    suspicious_endpoints = anomalies["suspicious_endpoints"]
    suspicious_users = anomalies["suspicious_users"]
    assert suspicious_endpoints.get("/api/payments") == 1
    assert suspicious_users.get("user_3") == 1


# -------------------------
# Run all tests
# -------------------------
if __name__ == "__main__":
    test_endpoint_statistics()
    print("Step 4 tests passed!")

    test_performance_issues()
    print("Step 5 tests passed!")

    test_payload_insights()
    print("Step 6 tests passed!")

    test_hourly_distribution()
    print("Step 7 tests passed!")

    test_top_users_by_requests()
    print("Step 8 tests passed!")

    test_recommendations()
    print("Step 9 tests passed!")

    test_anomaly_detection()
    print("Step 10 tests passed!")
