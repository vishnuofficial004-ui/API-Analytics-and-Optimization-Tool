# Design Decisions - API Logs Analyzer

## Chosen Advanced Features
1. **Anomaly Detection**
   - Tracks response time spikes (>1000ms), server errors (status_code >=500), and suspicious endpoints/users.
   - Helps identify potential API failures, performance bottlenecks, or unusual usage.

2. **Caching Opportunity Analysis**
   - Analyzes GET-heavy endpoints with low error rates.
   - Estimates requests saved, performance improvement, and potential cost savings.

## Trade-offs
- **Simplicity vs. Completeness:** Focused on two advanced features for clarity. Other features (like detailed traffic spikes, error clusters) were omitted to ensure reliable results.
- **Memory Usage:** Storing all logs in memory can be expensive for extremely large datasets (>1 million logs). Could switch to streaming processing for huge datasets.

## Scaling to 1 Million+ Logs
- **Batch processing:** Load logs in chunks instead of keeping all in memory.
- **Parallel computation:** Utilize `multiprocessing` or async processing per endpoint.
- **Database-backed stats:** Store intermediate stats in a database for persistent tracking.

## Improvements with More Time
- Integrate **rate-limiting analysis** for advanced user monitoring.
- Implement **cost estimation engine** for detailed serverless execution costs.
- Add **alerting/notification system** for anomalies.

## Approximate Time Spent
- Core function: 4 hours
- Advanced features: 3 hours
- Unit tests: 2 hours
- Code cleanup & validation: 1 hour
- Total: ~10 hours
