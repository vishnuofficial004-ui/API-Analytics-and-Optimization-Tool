API Logs Analyzer

****Overview****

This project implements an API logs analysis tool for serverless marketplace.

It processes API call logs to generate detailed analytics, detect anomalies, identify caching opportunities, and provide actionable recommendations.

****Features****

***Core Functionality***

Computes endpoint statistics: average response times, slowest/fastest requests, error counts, most common status codes.

Calculates overall summary: total requests, error rates, and time range.

Tracks hourly distribution of API requests.

Identifies top 5 users by request count.

****Advanced Features****

Anomaly Detection: Detects response time spikes, server errors, and suspicious endpoints/users.

Caching Opportunity Analysis: Identifies endpoints suitable for caching, estimates performance improvement and potential cost savings.

*****Setup Instructions*****
1. Clone the Repository

git clone https://github.com/vishnuofficial004-ui/API-Analytics-and-Optimization-Tool.git

cd API-Analytics-and-Optimization-Tool

##  Running the Demo

A demo script run_demo.py is included to visualize the output of the analyze_api_logs function.

2. Create Virtual Environment (Python)

python -m venv venv

Windows

venv\Scripts\activate

3. Install Dependencies

pip install -r requirements.txt

****Usage****

from function import analyze_api_logs

logs = [
{
"timestamp": "2025-01-15T10:00:00Z",
"endpoint": "/api/users",
"method": "GET",
"response_time_ms": 100,
"status_code": 200,
"user_id": "user_1",
"request_size_bytes": 512,
"response_size_bytes": 1024
}
]

result = analyze_api_logs(logs)
print(result)

****Running Tests****

Open the project directory

pytest -v --maxfail=1 --tb=short

Covers core logic, edge cases, performance checks, and advanced features.

Minimum coverage expected: 80%.

Time & Space Complexity

Time: O(N) for processing logs (N = total log entries).

Space: O(N) for storing intermediate stats (per endpoint, per user).

****Notes****

Handles large datasets efficiently.

Implements performance issue detection and error rate analysis.

Generates recommendations based on caching opportunities and endpoint performance.

Includes unit tests, edge case handling, and top user analysis.

Fully documented with docstrings and inline comments.
