from datetime import datetime, timedelta
from typing import Dict, Any, List

from config import (
    REQUIRED_FIELDS,
    RESPONSE_TIME_THRESHOLDS,
    ERROR_RATE_THRESHOLDS,
)

def parse_iso_timestamp(ts: str):
    """Convert ISO timestamp string to datetime object."""
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def safe_divide(numerator, denominator):
    """Divide numbers safely, return 0 if denominator is 0."""
    return numerator / denominator if denominator else 0


def is_valid_log(log: Dict[str, Any]) -> bool:
    """Validate log entry based on required fields and value types."""
    for field in REQUIRED_FIELDS:
        if field not in log:
            return False

    if parse_iso_timestamp(log["timestamp"]) is None:
        return False

    numeric_fields = ["response_time_ms", "request_size_bytes", "response_size_bytes"]
    for field in numeric_fields:
        if not isinstance(log[field], (int, float)) or log[field] < 0:
            return False

    return True


def classify_response_time(ms: float) -> str:
    """Categorize response time into severity buckets."""
    if ms >= RESPONSE_TIME_THRESHOLDS["critical"]:
        return "critical"
    if ms >= RESPONSE_TIME_THRESHOLDS["high"]:
        return "high"
    if ms >= RESPONSE_TIME_THRESHOLDS["medium"]:
        return "medium"
    return ""


def classify_error_rate(rate: float) -> str:
    """Categorize error rate severity."""
    if rate >= ERROR_RATE_THRESHOLDS["critical"]:
        return "critical"
    if rate >= ERROR_RATE_THRESHOLDS["high"]:
        return "high"
    if rate >= ERROR_RATE_THRESHOLDS["medium"]:
        return "medium"
    return ""


def percentile(values: List[float], p: float) -> float:
    """Compute percentile (p should be 95 or 99)."""
    if not values:
        return 0
    values = sorted(values)
    index = int(len(values) * p / 100)
    index = min(index, len(values) - 1)
    return values[index]


def group_by_endpoint(logs: List[Dict[str, Any]]):
    """Return dictionary endpoint → list of logs."""
    result = {}
    for log in logs:
        result.setdefault(log["endpoint"], []).append(log)
    return result


def window_logs_by_minutes(times: List[datetime], window_minutes: int):
    """Return sliding window counts for detecting spikes."""
    results = []
    for i in range(len(times)):
        start = times[i]
        end = start + timedelta(minutes=window_minutes)
        count = sum(1 for t in times if start <= t < end)
        results.append((start, count))
    return results

