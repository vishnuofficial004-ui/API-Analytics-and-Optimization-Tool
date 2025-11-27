from collections import defaultdict, Counter
from datetime import datetime
from typing import List, Dict, Any

REQUIRED_FIELDS = [
    "timestamp",
    "endpoint",
    "method",
    "response_time_ms",
    "status_code",
    "user_id",
    "request_size_bytes",
    "response_size_bytes"
]

def is_valid_log(log: Dict[str, Any]) -> bool:
    """Validate a single log entry."""
    for field in REQUIRED_FIELDS:
        if field not in log:
            return False
    try:
        datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00"))
    except Exception:
        return False
    numeric_fields = ["response_time_ms", "request_size_bytes", "response_size_bytes"]
    for field in numeric_fields:
        if not isinstance(log[field], (int, float)) or log[field] < 0:
            return False
    return True


def analyze_api_logs(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze API logs including summary and endpoint-level statistics."""
    if not logs:
        return {
            "summary": {},
            "endpoint_stats": [],
            "performance_issues": [],
            "recommendations": [],
            "hourly_distribution": {},
            "top_users_by_requests": []
        }

    # Filter invalids
    valid_logs = [log for log in logs if is_valid_log(log)]
    if not valid_logs:
        return {
            "summary": {},
            "endpoint_stats": [],
            "performance_issues": [],
            "recommendations": [],
            "hourly_distribution": {},
            "top_users_by_requests": []
        }

    total_requests = len(valid_logs)
    timestamps = [datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00")) for log in valid_logs]
    time_range = {
        "start": min(timestamps).isoformat() + "Z",
        "end": max(timestamps).isoformat() + "Z"
    }
    avg_response_time = sum(log["response_time_ms"] for log in valid_logs) / total_requests
    error_count = sum(1 for log in valid_logs if log["status_code"] >= 400)
    error_rate_percentage = round((error_count / total_requests) * 100, 2)

    summary = {
        "total_requests": total_requests,
        "time_range": time_range,
        "avg_response_time_ms": round(avg_response_time, 2),
        "error_rate_percentage": error_rate_percentage
    }

    endpoints = defaultdict(list)
    for log in valid_logs:
        endpoints[log["endpoint"]].append(log)

    endpoint_stats = []
    for endpoint, logs_list in endpoints.items():
        request_count = len(logs_list)
        avg_response = sum(l["response_time_ms"] for l in logs_list) / request_count
        slowest = max(l["response_time_ms"] for l in logs_list)
        fastest = min(l["response_time_ms"] for l in logs_list)
        errors = sum(1 for l in logs_list if l["status_code"] >= 400)
        most_common_status = Counter(l["status_code"] for l in logs_list).most_common(1)[0][0]

        endpoint_stats.append({
            "endpoint": endpoint,
            "request_count": request_count,
            "avg_response_time_ms": round(avg_response, 2),
            "slowest_request_ms": slowest,
            "fastest_request_ms": fastest,
            "error_count": errors,
            "most_common_status": most_common_status
        })

    return {
        "summary": summary,
        "endpoint_stats": endpoint_stats,
        "performance_issues": [],
        "recommendations": [],
        "hourly_distribution": {},
        "top_users_by_requests": []
    }
