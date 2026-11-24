terraform {
  required_version = ">= 1.6"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }

  # State lives in a GCS bucket. Init with:
  #   terraform init -backend-config="bucket=<project_id>-tfstate"
  backend "gcs" {}
}

provider "google" {
  project = var.project_id
  region  = var.region
}
