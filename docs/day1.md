# Day 1 checklist

Goal for tonight: **the collector runs every 15 minutes and events land in PostgreSQL.**
Every day of delay is a day less of training data.

If the Azure subscription is not ready yet, start collecting on one laptop with `SINK=file`
(see `collector/README.md`) and backfill later. Do not wait.

## Everyone (morning)

- [ ] Install: Git, Python 3.11, Docker Desktop, VS Code, [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli), [Terraform](https://developer.hashicorp.com/terraform/install), `psql`
- [ ] Clone the repo, run `pip install -r requirements-dev.txt` and `pytest`
- [ ] Accept the Azure invite e-mail (guest in the team lead's directory), then in the portal switch directory to it

## DE1

- [ ] Create the subscription (Azure free account, or Azure for Students), add a budget alert at $1
- [ ] Check the allowed regions (Students subscriptions restrict them) and set `location` in `terraform.tfvars`
- [ ] Create `rg-flowcast` and invite the team (Access control (IAM) → Contributor on the resource group)
- [ ] Create the Terraform state: resource group `rg-flowcast-tfstate`, storage account, container `tfstate`
- [ ] Create Service Bus (Basic) with the 2 queues, PostgreSQL B1ms, Key Vault (Terraform or portal today, Terraform by D3)
- [ ] Apply `infra/sql/001_raw_tables.sql` with `psql`

## DE1 + DE2

- [ ] Implement `collector/src/collector/main.py` and `loader/`, with tests
- [ ] Build the images, push to `ghcr.io`, deploy the collector job (cron `*/15`) and the loader job (event trigger)
- [ ] Check rows in `raw.traffic_events` and `raw.weather_events`
- [ ] Write the first slot time in `dbt/dbt_project.yml` (`vars.collection_start`)

## DA1

- [ ] Get the TomTom key (developer.tomtom.com) and OpenWeather key (openweathermap.org, free plan)
- [ ] Add both to Key Vault: `az keyvault secret set --vault-name <kv> --name tomtom-key --value ...`
- [ ] Verify the 15 probe points: TomTom must return the intended road and direction
- [ ] Update `config/segments.yml` before noon

## DA2 and DS

- [ ] DA2: Power BI wireframe, check who has a Power BI Pro license (university Microsoft 365?), list of delivery companies to contact
- [ ] DS: feature and target design, evaluation plan
