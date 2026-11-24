# Day 1 checklist

Goal for tonight: **the collector runs every 15 minutes and events land in BigQuery.**
Every day of delay is a day less of training data.

## Everyone (morning)

- [ ] Install: Git, Python 3.11, Docker Desktop, VS Code, [gcloud CLI](https://cloud.google.com/sdk/docs/install), [Terraform](https://developer.hashicorp.com/terraform/install)
- [ ] Clone the repo, run `pip install -r requirements-dev.txt` and `pytest`
- [ ] Accept the GCP project invite (your own Google account)

## DE1

- [ ] Create the GCP project, link billing, add a budget alert at $1
- [ ] Invite the team by e-mail (IAM) with the roles agreed in the kickoff
- [ ] Create the Terraform state bucket: `<project_id>-tfstate`
- [ ] Create Artifact Registry, Pub/Sub topics, BigQuery `raw` tables (Terraform or console today, Terraform by D3)

## DE1 + DE2

- [ ] Implement `collector/src/collector/main.py`, with tests
- [ ] Build the image, deploy the Cloud Run job, add the `*/15` Cloud Scheduler trigger
- [ ] Check rows in `raw.traffic_events` and `raw.weather_events`
- [ ] Write the first slot time in `dataform/includes/constants.js`

## DA1

- [ ] Get the TomTom key (developer.tomtom.com) and OpenWeather key (openweathermap.org, free plan)
- [ ] Verify the 15 probe points: TomTom must return the intended road and direction
- [ ] Update `config/segments.yml` before noon

## DA2 and DS

- [ ] DA2: dashboard wireframe, list of delivery companies to contact
- [ ] DS: feature and target design, evaluation plan
