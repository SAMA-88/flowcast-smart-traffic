# Flowcast · Smart Traffic & Weather Hub

**Traffic & weather intelligence for delivery fleets.**

Every 15 minutes we record road-segment speeds (TomTom) and local weather (OpenWeather)
for 15 roads in Cairo and Alexandria, then turn them into congestion KPIs, forecasts and
alerts for delivery companies. Serverless on Google Cloud, everything as code.

![Architecture](docs/architecture.png)

## Repository layout

| Folder | What goes there | Owner |
|---|---|---|
| [`config/`](config/) | The 15 road segments and 5 weather zones | DA1 |
| [`collector/`](collector/) | Cloud Run job that calls the APIs and publishes events | DE1 + DE2 |
| [`infra/`](infra/) | Terraform for every GCP resource, plus the raw table schemas | DE1 |
| [`dataform/`](dataform/) | SQL transformations: raw → silver → gold, and assertions | DE2 + DA1 |
| [`ml/`](ml/) | BigQuery ML: baselines, classifier, forecast | DS |
| [`api/`](api/) | FastAPI service and the live Leaflet map | DE2 |
| [`alerts/`](alerts/) | Alert job that sends Telegram / e-mail messages | DE2 |
| [`scripts/`](scripts/) | One-off helpers (probe segments, load reference tables) | anyone |
| [`docs/`](docs/) | Architecture, timeline, Day 1 checklist, runbook | everyone |

## Getting started

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   ·   macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check .
pytest
```

Then follow [docs/day1.md](docs/day1.md).

## How we work

- Branch from `main`: `feature/<short-name>`. One pull request per task, reviewed by one teammate.
- No manual changes in the GCP console after D3: change Terraform instead.
- API keys live in Secret Manager only. Never commit keys or paste them in chat.
- Timeline: [docs/timeline.png](docs/timeline.png)
