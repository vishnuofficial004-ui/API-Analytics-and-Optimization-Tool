import sys
import os
import pytest
from datetime import datetime
from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from function import analyze_api_logs, is_valid_log

# Basic Validation
def test_is_valid_log():
    valid_log = {
        "timestamp": "2025-01-15T10:00:00Z",
        "endpoint": "/api/users",
        "method": "GET",
        "response_time_ms": 100,
        "status_code": 200,
        "user_id": "user_1",
        "request_size_bytes": 512,
        "response_size_bytes": 1024
    }
    invalid_log_missing_field = valid_log.copy()
    invalid_log_missing_field.pop("method")
    invalid_log_negative = valid_log.copy()
    invalid_log_negative["response_time_ms"] = -50
    invalid_log_bad_ts = valid_log.copy()
    invalid_log_bad_ts["timestamp"] = "invalid-date"

    assert is_valid_log(valid_log)
    assert not is_valid_log(invalid_log_missing_field)
    assert not is_valid_log(invalid_log_negative)
    assert not is_valid_log(invalid_log_bad_ts)

# Core Function - Empty Logs

def test_empty_logs():
    result = analyze_api_logs([])
    assert isinstance(result, dict)
    assert result["summary"] == {}
    assert result["endpoint_stats"] == []
    assert result["anomalies"]["response_time_spikes"] == []

# Endpoint Statistics

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


# Performance Issues

def test_performance_issues():
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


# Payload Insights

def test_payload_insights():
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

    assert round(size_stats["avg_request_size_bytes"]) == round((300 + 700 + 1500) / 3)
    assert round(size_stats["avg_response_size_bytes"]) == round((600 + 900 + 2500) / 3)
    assert size_stats["largest_request"]["request_size_bytes"] == 1500
    assert size_stats["largest_request"]["endpoint"] == "/api/orders"
    assert size_stats["largest_response"]["response_size_bytes"] == 2500
    assert size_stats["largest_response"]["endpoint"] == "/api/orders"


# Hourly Distribution
def test_hourly_distribution():
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

# Top Users

def test_top_users_by_requests():
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


# Recommendations

def test_recommendations():
    logs = []
    for i in range(150):
        logs.append({
            "timestamp": f"2025-01-15T12:{i%60:02}:00Z",
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

    # Slow endpoint
    slow_suggestion = [r for r in recs if "/api/slow" in r and "performance" in r]
    assert len(slow_suggestion) == 1

    # High error rate
    error_suggestion = [r for r in recs if "/api/slow" in r and "error rate" in r]
    assert len(error_suggestion) == 1

# Anomaly Detection

def test_anomaly_detection():
    logs = [
        {"timestamp": "2025-01-15T10:00:00Z", "endpoint": "/api/users", "method": "GET",
         "response_time_ms": 100, "status_code": 200, "user_id": "user_1",
         "request_size_bytes": 512, "response_size_bytes": 1024},
        {"timestamp": "2025-01-15T10:05:00Z", "endpoint": "/api/users", "method": "GET",
         "response_time_ms": 500, "status_code": 200, "user_id": "user_2",
         "request_size_bytes": 512, "response_size_bytes": 1024},
        {"timestamp": "2025-01-15T10:10:00Z", "endpoint": "/api/payments", "method": "POST",
         "response_time_ms": 1500,
         "status_code": 200, "user_id": "user_1",
         "request_size_bytes": 1024, "response_size_bytes": 512},
        {"timestamp": "2025-01-15T10:15:00Z", "endpoint": "/api/payments", "method": "POST",
         "response_time_ms": 300,
         "status_code": 500, "user_id": "user_3",
         "request_size_bytes": 1024, "response_size_bytes": 512}
    ]

    result = analyze_api_logs(logs)
    anomalies = result["anomalies"]

    # Only check server errors because spikes/suspicious users are empty
    server_errors = anomalies.get("server_errors", [])
    assert len(server_errors) == 1
    assert server_errors[0]["status_code"] == 500

# Caching Opportunities
def test_caching_opportunities():
    logs = []
    for i in range(150):
        logs.append({
            "timestamp": f"2025-01-15T12:{i%60:02}:00Z",
            "endpoint": "/api/cache",
            "method": "GET",
            "response_time_ms": 100,
            "status_code": 200,
            "user_id": f"user_{i}",
            "request_size_bytes": 100,
            "response_size_bytes": 200
        })
    result = analyze_api_logs(logs)
    caching = result["caching_opportunities"]
    assert len(caching) == 1
    cache_entry = caching[0]
    assert cache_entry["endpoint"] == "/api/cache"
    assert cache_entry["potential_cache_hit_rate"] > 80
    assert cache_entry["current_requests"] == 150
