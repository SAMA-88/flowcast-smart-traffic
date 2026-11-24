# collector

Cloud Run job, triggered by Cloud Scheduler every 15 minutes. Owner: **DE1 + DE2** · Due: **D1**

- Code: `src/collector/` (start in `main.py`, it lists the steps and rules)
- Tests: `tests/`
- Image: add a `Dockerfile` here (Python 3.11 slim, copy `src/` and `../config/`)

Local run without GCP: add a dry-run mode that prints events instead of publishing.
