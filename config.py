# ============================
#   REQUIRED FIELDS
# ============================
REQUIRED_FIELDS = [
    "timestamp",
    "endpoint",
    "method",
    "response_time_ms",
    "status_code",
    "user_id",
    "request_size_bytes",
    "response_size_bytes",
]

# ============================
#   RESPONSE TIME SEVERITY THRESHOLDS
# ============================
RESPONSE_TIME_THRESHOLDS = {
    "medium": 500,
    "high": 1000,
    "critical": 2000,
}

# Single-use value for slow endpoint classification
SLOW_ENDPOINT_THRESHOLD_MS = 500  


# ============================
#   ERROR RATE THRESHOLDS
# ============================
ERROR_RATE_THRESHOLDS_PERCENT = {
    "medium": 5,
    "high": 10,
    "critical": 15,
}

ERROR_RATE_THRESHOLDS = ERROR_RATE_THRESHOLDS_PERCENT  # backward compatibility


# ============================
#   ANOMALY DETECTION CONSTANTS
# ============================
RESPONSE_SPIKE_MULTIPLIER = 2  # response spike when >2× normal
REQUEST_SPIKE_WINDOW_MINUTES = 5
REQUEST_SPIKE_RATE_MULTIPLIER = 3

ERROR_CLUSTER_WINDOW_MINUTES = 5
ERROR_CLUSTER_THRESHOLD = 10

SUSPICIOUS_TRAFFIC_THRESHOLD = 0.50  # 50%



# ============================
#   CACHING ANALYSIS CONSTANTS
# ============================
CACHE_MIN_REQUESTS = 100
CACHE_MIN_GET_RATIO = 0.80
CACHE_MAX_ERROR_RATE = 2

CACHE_HIT_RATE_ASSUMPTION = 0.90
CACHE_COST_SAVING_PER_REQUEST = 0.001
CACHE_RECOMMENDED_TTL_MINUTES = 15
