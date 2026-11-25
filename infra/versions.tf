terraform {
  required_version = ">= 1.6"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # State lives in an Azure Storage blob container (created once by hand, see docs/day1.md).
  # Init with:
  #   terraform init \
  #     -backend-config="resource_group_name=rg-flowcast-tfstate" \
  #     -backend-config="storage_account_name=<tfstate_account>" \
  #     -backend-config="container_name=tfstate" \
  #     -backend-config="key=flowcast.tfstate"
  backend "azurerm" {
    use_azuread_auth = true
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}
