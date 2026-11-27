# collector

Container Apps Job with a cron trigger (`*/15 * * * *`). Owner: **DE1 + DE2** · Due: **D1**

- Code: `src/collector/` (start in `main.py`, it lists the steps and rules)
- Tests: `tests/`
- Image: add a `Dockerfile` here (Python 3.11 slim, copy `src/` and `../config/`), pushed to `ghcr.io`

Local run without Azure: `SINK=file` writes events as JSON lines to `scripts/out/events/`
instead of sending them to Service Bus. Use it to start collecting before the subscription is ready,
then send the files to the queue once (backfill).

## Environment variables

| Variable | Required | Example |
|---|---|---|
| `TOMTOM_API_KEY` | yes | from Key Vault |
| `OPENWEATHER_API_KEY` | yes | from Key Vault |
| `SINK` | no (default `servicebus`) | `file` for a local run |
| `SERVICEBUS_NAMESPACE` | when `SINK` is not `file` | `sb-flowcast.servicebus.windows.net` |

`SERVICEBUS_NAMESPACE` should be the full hostname. A short name such as `sb-flowcast`
also works: the collector appends `.servicebus.windows.net` when it is missing.
