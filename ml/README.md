# ml

Python models, retrained nightly at 02:00 UTC by a Container Apps Job (cron `0 2 * * *`). Owner: **DS**

The job reads gold tables from PostgreSQL, trains, evaluates, and writes `gold.predictions`.
Model files are saved to a Blob Storage container, named by `model_version` (date + git SHA).

| Step | Due |
|---|---|
| Feature and target design, evaluation plan (time split, MAE) | D2 |
| Baselines in SQL (dbt models): last value, hour × day-type mean | D5 |
| Feature table (lags t-1, t-2, t-4, hour, day type, weather): dbt model `gold.ml_features` | D7 |
| Prototype on 7-10 days: LightGBM classifier (class L/M/H at +30 min) + LightGBM regressor (ratio at +15/30/60 min, one model, segment as a feature) | D10 |
| Final training on 14 days, walk-forward evaluation | D11-D12 |
| `gold.predictions` + model card | D13 |

Rule: a model ships only if it beats both baselines.
Code goes in `src/ml/` (`train.py`, `evaluate.py`, `predict.py`). Notebooks stay in `notebooks/`
for exploration only. The job never runs a notebook.

Planned `requirements.txt`: `pandas`, `lightgbm`, `scikit-learn`, `psycopg[binary]`, `azure-storage-blob`, `azure-identity`.
