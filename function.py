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

def analyze_api_logs(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze API logs with full statistics, anomaly detection, and caching opportunities."""
    if not logs:
        return {
            "summary": {},
            "endpoint_stats": [],
            "performance_issues": [],
            "size_insights": {},
            "hourly_distribution": {},
            "top_users_by_requests": [],
            "recommendations": [],
            "anomalies": {
                "response_time_spikes": [],
                "server_errors": [],
                "suspicious_endpoints": {},
                "suspicious_users": {}
            },
            "caching_opportunities": [],
            "total_potential_savings": {}
        }

    valid_logs = [log for log in logs if is_valid_log(log)]
    if not valid_logs:
        return analyze_api_logs([])

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

    # Endpoint stats 

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

    size_insights = {
        "avg_request_size_bytes": sum(l["request_size_bytes"] for l in valid_logs) / total_requests,
        "avg_response_size_bytes": sum(l["response_size_bytes"] for l in valid_logs) / total_requests,
        "largest_request": max(valid_logs, key=lambda x: x["request_size_bytes"]),
        "largest_response": max(valid_logs, key=lambda x: x["response_size_bytes"])
    }

    hourly_distribution = defaultdict(int)
    for ts in timestamps:
        hourly_distribution[ts.strftime("%H:00")] += 1

    user_counter = Counter(l["user_id"] for l in valid_logs)
    top_users = [{"user_id": u, "request_count": c} for u, c in user_counter.most_common(5)]

    recommendations = []
    for endpoint, logs_list in endpoints.items():
        req_count = len(logs_list)
        get_count = sum(1 for l in logs_list if l["method"] == "GET")
        errors = sum(1 for l in logs_list if l["status_code"] >= 400)
        err_rate = errors / req_count * 100
        avg_resp = sum(l["response_time_ms"] for l in logs_list) / req_count

        if req_count > 10 and get_count / req_count > 0.8 and err_rate < 2:
            recommendations.append(f"Consider caching for {endpoint} ({req_count} requests, high GET traffic, low error rate)")
        if avg_resp > 500:
            recommendations.append(f"Investigate {endpoint} performance (avg {int(avg_resp)}ms exceeds 500ms threshold)")
        if err_rate > 5:
            recommendations.append(f"Alert: {endpoint} has {round(err_rate,2)}% error rate")
    # Anomaly Detection
    anomalies = {
        "response_time_spikes": [],
        "server_errors": [],
        "suspicious_endpoints": {},
        "suspicious_users": {}
    }

    for log in valid_logs:
        if log["response_time_ms"] > 1000:  # spike threshold
            anomalies["response_time_spikes"].append(log)
        if log["status_code"] >= 500:
            anomalies["server_errors"].append(log)

    endpoint_errors = Counter(l["endpoint"] for l in valid_logs if l["status_code"] >= 500)
    user_errors = Counter(l["user_id"] for l in valid_logs if l["status_code"] >= 500)
    anomalies["suspicious_endpoints"] = {k: v for k, v in endpoint_errors.items() if v > 0}
    anomalies["suspicious_users"] = {k: v for k, v in user_errors.items() if v > 0}

    # Caching Opportunity Analysis
    caching_opportunities = []
    total_requests_saved = 0
    total_cost_savings = 0
    total_perf_improvement = 0

    for endpoint, logs_list in endpoints.items():
        req_count = len(logs_list)
        if req_count < 100:
            continue 
        get_count = sum(1 for l in logs_list if l["method"] == "GET")
        errors = sum(1 for l in logs_list if l["status_code"] >= 400)
        err_rate = errors / req_count * 100

        if get_count / req_count > 0.8 and err_rate < 2:
            potential_requests_saved = int(req_count * 0.9)  # assume 90% cacheable
            estimated_cost_savings_usd = round(potential_requests_saved * 0.001, 2)
            performance_improvement_ms = int(sum(l["response_time_ms"] for l in logs_list) / req_count * 0.9)
            caching_opportunities.append({
                "endpoint": endpoint,
                "potential_cache_hit_rate": int(get_count / req_count * 100),
                "current_requests": req_count,
                "potential_requests_saved": potential_requests_saved,
                "estimated_cost_savings_usd": estimated_cost_savings_usd,
                "recommended_ttl_minutes": 15,
                "recommendation_confidence": "high"
            })
            total_requests_saved += potential_requests_saved
            total_cost_savings += estimated_cost_savings_usd
            total_perf_improvement += performance_improvement_ms

    total_potential_savings = {
        "requests_eliminated": total_requests_saved,
        "cost_savings_usd": total_cost_savings,
        "performance_improvement_ms": total_perf_improvement
    }

    return {
        "summary": summary,
        "endpoint_stats": endpoint_stats,
        "performance_issues": performance_issues,
        "size_insights": size_insights,
        "hourly_distribution": dict(hourly_distribution),
        "top_users_by_requests": top_users,
        "recommendations": recommendations,
        "anomalies": anomalies,
        "caching_opportunities": caching_opportunities,
        "total_potential_savings": total_potential_savings
    }
