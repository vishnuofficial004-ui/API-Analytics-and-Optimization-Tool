from function import analyze_api_logs

def test_empty_logs():
    logs = []
    result = analyze_api_logs(logs)
    assert result["summary"] == {}
    assert result["endpoint_stats"] == []
    assert result["performance_issues"] == []
    assert result["recommendations"] == []
    assert result["hourly_distribution"] == {}
    assert result["top_users_by_requests"] == []

if __name__ == "__main__":
    test_empty_logs()
    print("Step 1 test passed!")
