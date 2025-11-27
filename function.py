from typing import List, Dict, Any
from datetime import datetime

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
    """
    Validate a single log entry.

    Returns True if log is valid, False otherwise.
    """
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in log:
            return False

    # Validate timestamp
    try:
        datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00"))
    except Exception:
        return False

    # Check numeric fields
    numeric_fields = ["response_time_ms", "request_size_bytes", "response_size_bytes"]
    for field in numeric_fields:
        if not isinstance(log[field], (int, float)) or log[field] < 0:
            return False

    return True


def analyze_api_logs(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze API logs with basic input validation and edge case handling.

    Args:
        logs (List[Dict[str, Any]]): List of API call logs

    Returns:
        Dict[str, Any]: Dictionary containing analysis results
    """
    # Handle empty input
    if not logs:
        return {
            "summary": {},
            "endpoint_stats": [],
            "performance_issues": [],
            "recommendations": [],
            "hourly_distribution": {},
            "top_users_by_requests": []
        }

    # Filter out invalid logs
    valid_logs = [log for log in logs if is_valid_log(log)]

    # Handle single log entry
    if len(valid_logs) == 0:
        return {
            "summary": {},
            "endpoint_stats": [],
            "performance_issues": [],
            "recommendations": [],
            "hourly_distribution": {},
            "top_users_by_requests": []
        }

    # For now, return skeleton with valid logs count
    return {
        "summary": {"valid_logs_count": len(valid_logs)},
        "endpoint_stats": [],
        "performance_issues": [],
        "recommendations": [],
        "hourly_distribution": {},
        "top_users_by_requests": []
    }
