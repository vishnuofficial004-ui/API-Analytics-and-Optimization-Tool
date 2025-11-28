#log validation
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

# Response time
RESPONSE_TIME_THRESHOLDS = {
    "medium": 500,
    "high": 1000,
    "critical": 2000
}

# Error rate severity
ERROR_RATE_THRESHOLDS = {
    "medium": 5,
    "high": 10,
    "critical": 15
}
