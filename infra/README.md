# infra

Terraform for every Azure resource. Owner: **DE1** · Due: **D3** (everything in code)

Suggested files:

| File | Resources |
|---|---|
| `versions.tf` | Terraform + `azurerm` provider, Azure Storage backend for state |
| `variables.tf` | `subscription_id`, `location`, `prefix`, image tag, team members |
| `main.tf` | Resource group `rg-flowcast`, Log Analytics workspace, Container Apps environment (Consumption) |
| `servicebus.tf` | Namespace (**Basic** tier), queues `traffic-events` and `weather-events`, `max_delivery_count = 5` then dead-letter |
| `postgres.tf` | PostgreSQL Flexible Server **B_Standard_B1ms**, 32 GB, database `flowcast`, firewall rule "Allow Azure services", server parameters below |
| `jobs.tf` | Container Apps Jobs: `collector` (cron `*/15 * * * *`), `loader` (event trigger on queue length), `dbt` (cron `5-59/15 * * * *`), `alerts` (cron `8-59/15 * * * *`), `ml` (cron `0 2 * * *`) |
| `api.tf` | Container App `api` (FastAPI + map), external ingress, `min_replicas = 0` |
| `identity.tf` | One user-assigned managed identity per service, least-privilege role assignments (Service Bus Data Sender / Receiver, Key Vault Secrets User), GitHub OIDC federated credential |
| `keyvault.tf` | Key Vault (RBAC mode), secret *names* only. Values are added with `az keyvault secret set`, never in Terraform |
| `monitoring.tf` | Alert rules: job failed, dead-letter count > 0, no new rows for 20 min |
| `budget.tf` | `azurerm_consumption_budget_resource_group`: alerts at $1 and $5 |

Postgres server parameters:

| Parameter | Value | Why |
|---|---|---|
| `azure.extensions` | `POSTGIS,PG_CRON` | Allow-list the extensions used by `sql/001_raw_tables.sql` |
| `shared_preload_libraries` | `pg_cron` | Needed by pg_cron (server restart) |
| `cron.database_name` | `flowcast` | Run the cron jobs in our database, not `postgres` |

Folders:

- `schemas/`: JSON Schema of each event. This is the **data contract**. The collector validates before
  sending, and the loader validates before inserting. Invalid messages go to the dead-letter queue.
- `sql/`: DDL for the `raw` and `ref` schemas, applied with `psql` after `terraform apply`.

Rules:

- Raw TomTom data expires after 24 hours (pg_cron job in `sql/001_raw_tables.sql`).
- Images live in GitHub Container Registry (`ghcr.io/<org>/flowcast-*`), so we pay nothing for a registry.
  Container Apps pull them with a read-only token stored as a secret.
- The Postgres admin password comes from `random_password` and goes into Key Vault. It is also in the
  Terraform state, so the state container stays private and only DE1 has access.
