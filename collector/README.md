# collector

Container Apps Job with a cron trigger (`*/15 * * * *`). Owner: **DE1 + DE2** · Due: **D1**

- Code: `src/collector/` (start in `main.py`, it lists the steps and rules)
- Tests: `tests/`
- Image: add a `Dockerfile` here (Python 3.11 slim, copy `src/` and `../config/`), pushed to `ghcr.io`

Local run without Azure: `SINK=file` writes events as JSON lines to `scripts/out/events/`
instead of sending them to Service Bus. Use it to start collecting before the subscription is ready,
then send the files to the queue once (backfill).
