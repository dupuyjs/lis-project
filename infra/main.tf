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

# Create resource group
resource "azurerm_resource_group" "rg" {
  name     = "${local.name_prefix}-${var.environment}-rg"
  location = var.location
  tags     = local.required_tags
}

# Create azure container registry
resource "azurerm_container_registry" "acr" {
  name                = "${local.name_prefix}acr"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = var.container_registry_sku
  admin_enabled       = false
  tags                = local.required_tags
}

# Create azure kubernetes cluster
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "${local.name_prefix}aks"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "${local.name_prefix}k8s"
  tags                = local.required_tags

  default_node_pool {
    name            = "default"
    node_count      = 1
    vm_size         = "Standard_NC6"
  }

  identity {
    type = "SystemAssigned"
  }
}

# Assign kubelet_identity with acrpull role to registry scope
resource "azurerm_role_assignment" "aks_role" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "acrpull"
  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
}
