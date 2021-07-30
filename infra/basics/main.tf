terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=2.69.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "random_string" "random" {
  length  = 5
  special = false
  number  = true
  lower   = true
  upper   = false
}

locals {
  name_prefix = "${var.prefix}${random_string.random.result}"
  required_tags = {
    environment = var.environment
  }
}

resource "azurerm_resource_group" "rg" {
  name     = "${local.name_prefix}-${var.environment}-rg"
  location = var.location
  tags     = local.required_tags
}

resource "azurerm_container_registry" "acr" {
  name                = "${local.name_prefix}acr"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = var.container_registry_sku
  admin_enabled       = false
  tags                = local.required_tags
}

resource "azurerm_role_assignment" "acr_role" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "acrpull"
  principal_id         = var.service_principal_objectid
}
