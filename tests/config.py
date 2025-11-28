# config.py

# Required fields for log validation
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

# Response time severity thresholds (ms)
RESPONSE_TIME_THRESHOLDS = {
    "medium": 500,
    "high": 1000,
    "critical": 2000
}

# Error rate severity thresholds (%)
ERROR_RATE_THRESHOLDS = {
    "medium": 5,
    "high": 10,
    "critical": 15
}
