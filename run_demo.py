# run_demo.py
import json
from function import analyze_api_logs

# Sample logs
logs = [
    {"timestamp": "2025-01-15T10:00:00Z", "endpoint": "/api/users", "method": "GET",
     "response_time_ms": 100, "status_code": 200, "user_id": "user_1",
     "request_size_bytes": 512, "response_size_bytes": 1024},
    {"timestamp": "2025-01-15T10:05:00Z", "endpoint": "/api/payments", "method": "POST",
     "response_time_ms": 1500, "status_code": 500, "user_id": "user_2",
     "request_size_bytes": 1024, "response_size_bytes": 512}
]

result = analyze_api_logs(logs)
print(json.dumps(result, indent=4))
