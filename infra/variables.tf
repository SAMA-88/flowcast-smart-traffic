variable "project_id" {
  description = "GCP project id"
  type        = string
}

variable "region" {
  description = "Region for Cloud Run, Scheduler and BigQuery"
  type        = string
  default     = "europe-west1"
}
