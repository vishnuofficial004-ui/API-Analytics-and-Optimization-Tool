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

    # Validate timestamp
    try:
        datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00"))
    except Exception:
        return False

    numeric_fields = ["response_time_ms", "request_size_bytes", "response_size_bytes"]
    for field in numeric_fields:
        if not isinstance(log[field], (int, float)) or log[field] < 0:
            return False

    return True


# Severity Helper Functions

def get_severity_response_time(avg_ms: float) -> str:
    if avg_ms > 2000:
        return "critical"
    elif avg_ms > 1000:
        return "high"
    elif avg_ms > 500:
        return "medium"
    return ""


def get_severity_error_rate(rate: float) -> str:
    if rate > 15:
        return "critical"
    elif rate > 10:
        return "high"
    elif rate > 5:
        return "medium"
    return ""


def analyze_api_logs(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze API logs including summary, endpoint stats, payload analytics, hourly distribution, and top users."""
    if not logs:
        return {
            "summary": {},
            "endpoint_stats": [],
            "performance_issues": [],
            "recommendations": [],
            "hourly_distribution": {},
            "top_users_by_requests": [],
            "size_insights": {}
        }

    # Filter invalid logs
    valid_logs = [log for log in logs if is_valid_log(log)]
    if not valid_logs:
        return {
            "summary": {},
            "endpoint_stats": [],
            "performance_issues": [],
            "recommendations": [],
            "hourly_distribution": {},
            "top_users_by_requests": [],
            "size_insights": {}
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

    # ENDPOINT STATISTICS and PERFORMANCE ISSUES
    endpoints = defaultdict(list)
    for log in valid_logs:
        endpoints[log["endpoint"]].append(log)

    endpoint_stats = []
    performance_issues = []

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

        # Performance Issues
        severity_rt = get_severity_response_time(avg_response)
        if severity_rt:
            performance_issues.append({
                "type": "slow_endpoint",
                "endpoint": endpoint,
                "avg_response_time_ms": round(avg_response, 2),
                "threshold_ms": 500,
                "severity": severity_rt
            })

        error_rate_endpoint = (errors / request_count) * 100
        severity_err = get_severity_error_rate(error_rate_endpoint)
        if severity_err:
            performance_issues.append({
                "type": "high_error_rate",
                "endpoint": endpoint,
                "error_rate_percentage": round(error_rate_endpoint, 2),
                "severity": severity_err
            })

    # STEP 6 — PAYLOAD SIZE ANALYTICS
    size_insights = {
        "avg_request_size_bytes": sum(log["request_size_bytes"] for log in valid_logs) / total_requests,
        "avg_response_size_bytes": sum(log["response_size_bytes"] for log in valid_logs) / total_requests,
        "largest_request": max(valid_logs, key=lambda x: x["request_size_bytes"]),
        "largest_response": max(valid_logs, key=lambda x: x["response_size_bytes"])
    }

    # STEP 7 — HOURLY DISTRIBUTION
    hourly_distribution = defaultdict(int)
    for ts in timestamps:
        hour_key = ts.strftime("%H:00")
        hourly_distribution[hour_key] += 1

    # STEP 8 — TOP USERS BY REQUESTS
    user_counter = Counter(log["user_id"] for log in valid_logs)
    top_users = [{"user_id": uid, "request_count": count} for uid, count in user_counter.most_common(5)]

    return {
        "summary": summary,
        "endpoint_stats": endpoint_stats,
        "performance_issues": performance_issues,
        "size_insights": size_insights,
        "hourly_distribution": dict(hourly_distribution),
        "top_users_by_requests": top_users,
        "recommendations": []
    }
