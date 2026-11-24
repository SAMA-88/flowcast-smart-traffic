# ml

BigQuery ML models, retrained nightly at 02:00 by a scheduled query. Owner: **DS**

| Step | Due |
|---|---|
| Feature and target design, evaluation plan (time split, MAE) | D2 |
| Baselines in SQL: last value, hour × day-type mean | D5 |
| Feature table (lags, hour, day type, weather) | D7 |
| Prototype BOOSTED_TREE_CLASSIFIER + ARIMA_PLUS on 7-10 days | D10 |
| Final training on 14 days, walk-forward evaluation | D11-D12 |
| `gold.predictions` + model card | D13 |

Rule: a model ships only if it beats both baselines.
Put each step in its own numbered `.sql` file (`01_baselines.sql`, `02_features.sql`, ...).
