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

# Anamoly detection

def detect_anomalies(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not logs:
        return {}

    response_times = [log["response_time_ms"] for log in logs]
    avg_rt = sum(response_times) / len(response_times)
    threshold = avg_rt * 2.5  # spike threshold

    anomalies = {
        "response_time_spikes": [],
        "server_errors": [],
        "suspicious_endpoints": Counter(),
        "suspicious_users": Counter(),
        "stats": {
            "average_response_time_ms": avg_rt,
            "spike_threshold_ms": threshold
        }
    }

    for log in logs:
        rt = log["response_time_ms"]

        # High latency spike detection
        if rt > threshold:
            anomalies["response_time_spikes"].append(log)

        # 5xx server error detection
        if 500 <= log["status_code"] <= 599:
            anomalies["server_errors"].append(log)
            anomalies["suspicious_endpoints"][log["endpoint"]] += 1
            anomalies["suspicious_users"][log["user_id"]] += 1

    #JSON compatibility
    anomalies["suspicious_endpoints"] = dict(anomalies["suspicious_endpoints"])
    anomalies["suspicious_users"] = dict(anomalies["suspicious_users"])

    return anomalies

def analyze_api_logs(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze API logs including summary, endpoint stats, payload analytics, hourly distribution, top users, recommendations, and anomalies."""
    if not logs:
        return {
            "summary": {},
            "endpoint_stats": [],
            "performance_issues": [],
            "recommendations": [],
            "hourly_distribution": {},
            "top_users_by_requests": [],
            "size_insights": {},
            "anomalies": {}
        }

    valid_logs = [log for log in logs if is_valid_log(log)]
    if not valid_logs:
        return {
            "summary": {},
            "endpoint_stats": [],
            "performance_issues": [],
            "recommendations": [],
            "hourly_distribution": {},
            "top_users_by_requests": [],
            "size_insights": {},
            "anomalies": {}
        }

    total_requests = len(valid_logs)
    timestamps = [datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00")) for log in valid_logs]
    avg_response_time = sum(log["response_time_ms"] for log in valid_logs) / total_requests
    error_count = sum(1 for log in valid_logs if log["status_code"] >= 400)
    summary = {
        "total_requests": total_requests,
        "time_range": {
            "start": min(timestamps).isoformat() + "Z",
            "end": max(timestamps).isoformat() + "Z"
        },
        "avg_response_time_ms": round(avg_response_time, 2),
        "error_rate_percentage": round((error_count / total_requests) * 100, 2)
    }

    # performance issues
    endpoints = defaultdict(list)
    for log in valid_logs:
        endpoints[log["endpoint"]].append(log)

    endpoint_stats = []
    performance_issues = []

    for endpoint, logs_list in endpoints.items():
        request_count = len(logs_list)
        avg_resp = sum(l["response_time_ms"] for l in logs_list) / request_count
        slowest = max(l["response_time_ms"] for l in logs_list)
        fastest = min(l["response_time_ms"] for l in logs_list)
        errors = sum(1 for l in logs_list if l["status_code"] >= 400)
        most_common_status = Counter(l["status_code"] for l in logs_list).most_common(1)[0][0]

        endpoint_stats.append({
            "endpoint": endpoint,
            "request_count": request_count,
            "avg_response_time_ms": round(avg_resp, 2),
            "slowest_request_ms": slowest,
            "fastest_request_ms": fastest,
            "error_count": errors,
            "most_common_status": most_common_status
        })

        sev_rt = get_severity_response_time(avg_resp)
        if sev_rt:
            performance_issues.append({
                "type": "slow_endpoint",
                "endpoint": endpoint,
                "avg_response_time_ms": round(avg_resp, 2),
                "threshold_ms": 500,
                "severity": sev_rt
            })

        err_rate = (errors / request_count) * 100
        sev_err = get_severity_error_rate(err_rate)
        if sev_err:
            performance_issues.append({
                "type": "high_error_rate",
                "endpoint": endpoint,
                "error_rate_percentage": round(err_rate, 2),
                "severity": sev_err
            })

    # Payload analytics
    size_insights = {
        "avg_request_size_bytes": sum(l["request_size_bytes"] for l in valid_logs) / total_requests,
        "avg_response_size_bytes": sum(l["response_size_bytes"] for l in valid_logs) / total_requests,
        "largest_request": max(valid_logs, key=lambda x: x["request_size_bytes"]),
        "largest_response": max(valid_logs, key=lambda x: x["response_size_bytes"])
    }

    #Hourly distribution
    hourly_distribution = defaultdict(int)
    for ts in timestamps:
        hourly_distribution[ts.strftime("%H:00")] += 1

    # Top users
    user_counter = Counter(l["user_id"] for l in valid_logs)
    top_users = [{"user_id": u, "request_count": c} for u, c in user_counter.most_common(5)]

    # Recommendations
    recommendations = []
    for endpoint, logs_list in endpoints.items():
        req_count = len(logs_list)
        get_count = sum(1 for l in logs_list if l["method"] == "GET")
        errors = sum(1 for l in logs_list if l["status_code"] >= 400)
        err_rate = errors / req_count * 100
        avg_resp = sum(l["response_time_ms"] for l in logs_list) / req_count

        if req_count > 10 and get_count / req_count > 0.8 and err_rate < 2:
            recommendations.append(
                f"Consider caching for {endpoint} ({req_count} requests, high GET traffic, low error rate)"
            )

        if avg_resp > 500:
            recommendations.append(
                f"Investigate {endpoint} performance (avg {int(avg_resp)}ms exceeds 500ms threshold)"
            )

        if err_rate > 5:
            recommendations.append(
                f"Alert: {endpoint} has {round(err_rate,2)}% error rate"
            )

    anomalies = detect_anomalies(valid_logs)

    return {
        "summary": summary,
        "endpoint_stats": endpoint_stats,
        "performance_issues": performance_issues,
        "size_insights": size_insights,
        "hourly_distribution": dict(hourly_distribution),
        "top_users_by_requests": top_users,
        "recommendations": recommendations,
        "anomalies": anomalies
    }
