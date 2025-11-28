from collections import defaultdict, Counter
from datetime import timedelta
from typing import List, Dict, Any

from config import (
    RESPONSE_SPIKE_MULTIPLIER,
    REQUEST_SPIKE_WINDOW_MINUTES,
    REQUEST_SPIKE_RATE_MULTIPLIER,
    ERROR_CLUSTER_WINDOW_MINUTES,
    ERROR_CLUSTER_THRESHOLD,
    SUSPICIOUS_TRAFFIC_THRESHOLD,
    CACHE_MIN_REQUESTS,
    CACHE_MIN_GET_RATIO,
    CACHE_MAX_ERROR_RATE,
    CACHE_HIT_RATE_ASSUMPTION,
    CACHE_COST_SAVING_PER_REQUEST,
    CACHE_RECOMMENDED_TTL_MINUTES,
    SLOW_ENDPOINT_THRESHOLD_MS,
)
from utils import (
    parse_iso_timestamp,
    is_valid_log,
    classify_response_time,
    classify_error_rate,
    safe_divide,
    window_logs_by_minutes,
    group_by_endpoint,
)


def _iso_z(dt):
    """Return ISO formatted UTC string ending with Z."""
    return dt.isoformat().replace("+00:00", "Z")


def analyze_api_logs(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
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
                "request_spikes": [],
                "error_clusters": [],
                "suspicious_endpoints": {},
                "suspicious_users": {}
            },
            "caching_opportunities": [],
            "total_potential_savings": {}
        }
    
    valid_logs = []
    for raw in logs:
        if not is_valid_log(raw):
            continue
        # attach parsed timestamp to avoid repeated parsing
        ts = parse_iso_timestamp(raw["timestamp"])
        if ts is None:
            continue
        entry = dict(raw)
        entry["_ts"] = ts
        valid_logs.append(entry)

    if not valid_logs:
        return analyze_api_logs([])

    total_requests = len(valid_logs)
    timestamps = [l["_ts"] for l in valid_logs]

    avg_response_time = sum(l["response_time_ms"] for l in valid_logs) / total_requests
    error_count = sum(1 for l in valid_logs if l["status_code"] >= 400)
    summary = {
        "total_requests": total_requests,
        "time_range": {
            "start": _iso_z(min(timestamps)),
            "end": _iso_z(max(timestamps))
        },
        "avg_response_time_ms": round(avg_response_time, 2),
        "error_rate_percentage": round(safe_divide(error_count, total_requests) * 100, 2)
    }

    #Endpoint grouping
    endpoints = group_by_endpoint(valid_logs)  # endpoint -> list(logs)
    endpoint_stats = []
    performance_issues = []
    endpoint_avg_resp = {}

    for endpoint, logs_list in endpoints.items():
        request_count = len(logs_list)
        avg_resp = sum(l["response_time_ms"] for l in logs_list) / request_count
        endpoint_avg_resp[endpoint] = avg_resp
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

        # Performance issues (response time and error rate)
        sev_rt = classify_response_time(avg_resp)
        if sev_rt:
            performance_issues.append({
                "type": "slow_endpoint",
                "endpoint": endpoint,
                "avg_response_time_ms": round(avg_resp, 2),
                "threshold_ms": SLOW_ENDPOINT_THRESHOLD_MS,
                "severity": sev_rt
            })
        err_rate_pct = safe_divide(errors, request_count) * 100
        sev_err = classify_error_rate(err_rate_pct)
        if sev_err:
            performance_issues.append({
                "type": "high_error_rate",
                "endpoint": endpoint,
                "error_rate_percentage": round(err_rate_pct, 2),
                "severity": sev_err
            })

    # --- Size insights ---
    size_insights = {
        "avg_request_size_bytes": round(sum(l["request_size_bytes"] for l in valid_logs) / total_requests, 2),
        "avg_response_size_bytes": round(sum(l["response_size_bytes"] for l in valid_logs) / total_requests, 2),
        "largest_request": max(valid_logs, key=lambda x: x["request_size_bytes"]),
        "largest_response": max(valid_logs, key=lambda x: x["response_size_bytes"])
    }

    # --- Hourly distribution ---
    hourly_distribution = defaultdict(int)
    for ts in timestamps:
        hourly_distribution[ts.strftime("%H:00")] += 1

    # --- Top users ---
    user_counter = Counter(l["user_id"] for l in valid_logs)
    top_users = [{"user_id": u, "request_count": c} for u, c in user_counter.most_common(5)]

    # --- Recommendations (simple heuristics) ---
    recommendations = []
    for endpoint, logs_list in endpoints.items():
        req_count = len(logs_list)
        get_count = sum(1 for l in logs_list if l["method"] == "GET")
        errors = sum(1 for l in logs_list if l["status_code"] >= 400)
        err_rate_pct = safe_divide(errors, req_count) * 100
        avg_resp = sum(l["response_time_ms"] for l in logs_list) / req_count

        if req_count >= CACHE_MIN_REQUESTS and (get_count / req_count) >= CACHE_MIN_GET_RATIO and err_rate_pct < CACHE_MAX_ERROR_RATE:
            recommendations.append(f"Consider caching for {endpoint} ({req_count} requests, high GET traffic, low error rate)")
        if avg_resp > SLOW_ENDPOINT_THRESHOLD_MS:
            recommendations.append(f"Investigate {endpoint} performance (avg {int(avg_resp)}ms exceeds {SLOW_ENDPOINT_THRESHOLD_MS}ms threshold)")
        if err_rate_pct > 5:
            recommendations.append(f"Alert: {endpoint} has {round(err_rate_pct,2)}% error rate")

    # -------------------
    # Enhanced Anomaly Detection
    # -------------------
    anomalies = {
        "response_time_spikes": [],
        "server_errors": [],
        "request_spikes": [],
        "error_clusters": [],
        "suspicious_endpoints": {},
        "suspicious_users": {}
    }

    # 1) Response time spikes & server errors
    for l in valid_logs:
        ep = l["endpoint"]
        baseline = endpoint_avg_resp.get(ep) or 0
        if baseline and l["response_time_ms"] > RESPONSE_SPIKE_MULTIPLIER * baseline:
            anomalies["response_time_spikes"].append(l)
        if l["status_code"] >= 500:
            anomalies["server_errors"].append(l)

    # 2) Request spikes per endpoint in sliding windows
    for endpoint, times in ((ep, [entry["_ts"] for entry in endpoints[ep]]) for ep in endpoints):
        times.sort()
        # compute an average rate per minute across observed span (safe)
        span_minutes = max(1.0, (times[-1] - times[0]).total_seconds() / 60.0)
        avg_rate_per_window = safe_divide(len(times), span_minutes) * REQUEST_SPIKE_WINDOW_MINUTES  # expected per window
        # sliding windows
        windows = window_logs_by_minutes(times, REQUEST_SPIKE_WINDOW_MINUTES)
        for start, count in windows:
            if count > REQUEST_SPIKE_RATE_MULTIPLIER * avg_rate_per_window:
                anomalies["request_spikes"].append({
                    "endpoint": endpoint,
                    "timestamp": _iso_z(start),
                    "actual_rate": count,
                    "normal_rate": round(avg_rate_per_window, 2),
                    "severity": "high"
                })
                break

    # 3) Error clusters (> threshold within window)
    endpoint_error_times = {}
    for l in valid_logs:
        if l["status_code"] >= 400:
            endpoint_error_times.setdefault(l["endpoint"], []).append(l["_ts"])

    for endpoint, err_times in endpoint_error_times.items():
        err_times.sort()
        windows = window_logs_by_minutes(err_times, ERROR_CLUSTER_WINDOW_MINUTES)
        for start, count in windows:
            if count > ERROR_CLUSTER_THRESHOLD:
                anomalies["error_clusters"].append({
                    "endpoint": endpoint,
                    "time_window": f"{start.strftime('%H:%M')}-{(start + timedelta(minutes=ERROR_CLUSTER_WINDOW_MINUTES)).strftime('%H:%M')}",
                    "error_count": count,
                    "severity": "critical"
                })
                break

    # 4) Suspicious traffic (single user or single endpoint > threshold of total)
    for user, cnt in user_counter.items():
        if safe_divide(cnt, total_requests) > SUSPICIOUS_TRAFFIC_THRESHOLD:
            anomalies["suspicious_users"][user] = cnt
    for endpoint, logs_list in endpoints.items():
        if safe_divide(len(logs_list), total_requests) > SUSPICIOUS_TRAFFIC_THRESHOLD:
            anomalies["suspicious_endpoints"][endpoint] = len(logs_list)

    # Caching Opportunity Analysis
    caching_opportunities = []
    total_requests_saved = 0
    total_cost_savings = 0.0
    total_perf_improvement = 0

    for endpoint, logs_list in endpoints.items():
        req_count = len(logs_list)
        if req_count < CACHE_MIN_REQUESTS:
            continue
        get_count = sum(1 for l in logs_list if l["method"] == "GET")
        errors = sum(1 for l in logs_list if l["status_code"] >= 400)
        err_rate_pct = safe_divide(errors, req_count) * 100
        get_ratio = safe_divide(get_count, req_count)

        if get_ratio >= CACHE_MIN_GET_RATIO and err_rate_pct <= CACHE_MAX_ERROR_RATE:
            potential_requests_saved = int(req_count * CACHE_HIT_RATE_ASSUMPTION)
            estimated_cost_savings_usd = round(potential_requests_saved * CACHE_COST_SAVING_PER_REQUEST, 2)
            avg_resp = sum(l["response_time_ms"] for l in logs_list) / req_count
            performance_improvement_ms = int(avg_resp * CACHE_HIT_RATE_ASSUMPTION)
            caching_opportunities.append({
                "endpoint": endpoint,
                "potential_cache_hit_rate": int(get_ratio * 100),
                "current_requests": req_count,
                "potential_requests_saved": potential_requests_saved,
                "estimated_cost_savings_usd": estimated_cost_savings_usd,
                "recommended_ttl_minutes": CACHE_RECOMMENDED_TTL_MINUTES,
                "recommendation_confidence": "high"
            })
            total_requests_saved += potential_requests_saved
            total_cost_savings += estimated_cost_savings_usd
            total_perf_improvement += performance_improvement_ms

    total_potential_savings = {
        "requests_eliminated": total_requests_saved,
        "cost_savings_usd": round(total_cost_savings, 2),
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
