from function import analyze_api_logs

def test_empty_logs():
    result = analyze_api_logs([])
    assert result["summary"] == {}
    
def test_single_valid_log():
    logs = [{
        "timestamp": "2025-01-15T10:00:00Z",
        "endpoint": "/api/users",
        "method": "GET",
        "response_time_ms": 100,
        "status_code": 200,
        "user_id": "user_1",
        "request_size_bytes": 512,
        "response_size_bytes": 1024
    }]
    result = analyze_api_logs(logs)
    assert result["summary"]["valid_logs_count"] == 1

def test_missing_field():
    logs = [{
        "timestamp": "2025-01-15T10:00:00Z",
        "endpoint": "/api/users",
        # "method" missing
        "response_time_ms": 100,
        "status_code": 200,
        "user_id": "user_1",
        "request_size_bytes": 512,
        "response_size_bytes": 1024
    }]
    result = analyze_api_logs(logs)
    assert result["summary"] == {}

def test_negative_values():
    logs = [{
        "timestamp": "2025-01-15T10:00:00Z",
        "endpoint": "/api/users",
        "method": "GET",
        "response_time_ms": -50,  # Invalid
        "status_code": 200,
        "user_id": "user_1",
        "request_size_bytes": 512,
        "response_size_bytes": 1024
    }]
    result = analyze_api_logs(logs)
    assert result["summary"] == {}

def test_invalid_timestamp():
    logs = [{
        "timestamp": "invalid-timestamp",
        "endpoint": "/api/users",
        "method": "GET",
        "response_time_ms": 100,
        "status_code": 200,
        "user_id": "user_1",
        "request_size_bytes": 512,
        "response_size_bytes": 1024
    }]
    result = analyze_api_logs(logs)
    assert result["summary"] == {}

if __name__ == "__main__":
    test_empty_logs()
    test_single_valid_log()
    test_missing_field()
    test_negative_values()
    test_invalid_timestamp()
    print("Step 2 tests passed!")
