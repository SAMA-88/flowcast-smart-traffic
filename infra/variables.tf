variable "subscription_id" {
  description = "Azure subscription id (az account show --query id -o tsv)"
  type        = string
}

variable "location" {
  description = "Azure region for every resource. Azure for Students limits regions: check the allowed list first."
  type        = string
  default     = "westeurope"
}

variable "prefix" {
  description = "Short name used in every resource name, e.g. rg-<prefix>, sb-<prefix>"
  type        = string
  default     = "flowcast"
}

variable "image_tag" {
  description = "Git SHA of the images in ghcr.io to deploy (collector, loader, dbt, alerts, api, ml)"
  type        = string
  default     = "latest"
}

variable "team_members" {
  description = "Entra object ids of teammates (guests) who get Contributor on the resource group"
  type        = list(string)
  default     = []
}

variable "budget_alert_emails" {
  description = "Who gets the budget alerts"
  type        = list(string)
  default     = []
}
