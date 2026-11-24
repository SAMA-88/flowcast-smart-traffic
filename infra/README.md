# infra

Terraform for every GCP resource. Owner: **DE1** · Due: **D3** (everything in code)

Suggested files:

| File | Resources |
|---|---|
| `versions.tf` | Terraform + Google provider, GCS backend for state |
| `variables.tf` | `project_id`, `region`, image tags, billing account |
| `apis.tf` | Enable Run, Scheduler, Pub/Sub, BigQuery, Secret Manager, Artifact Registry |
| `pubsub.tf` | `traffic-events`, `weather-events`, dead-letter topic, BigQuery subscriptions |
| `bigquery.tf` | Datasets `raw`, `ref`, `silver`, `gold`, `ml`; raw tables from `schemas/` |
| `collector.tf` | Cloud Run job + Cloud Scheduler `*/15` |
| `iam.tf` | One service account per service, least privilege |
| `secrets.tf` | Secret Manager secrets (values are added with gcloud, never in Terraform) |
| `budget.tf` | Budget alerts at $1 and $5 |

`schemas/` holds the raw table schemas. They are the data contract: the collector's events
must have exactly these fields.

Rule: raw TomTom data expires after 24 hours (partition expiration on `raw.traffic_events`).
