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
  admin_enabled       = true
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
    name       = "default"
    node_count = var.aks_pool_node_count
    vm_size    = var.aks_pool_vm_size
  }

  identity {
    type = "SystemAssigned"
  }
}

# Assign kubelet_identity with acrpull role to pull images from registry (used by kubernetes)
resource "azurerm_role_assignment" "acr_pull_role" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "acrpull"
  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
}

# Create azure key vault
resource "azurerm_key_vault" "kv" {
  name                = "${local.name_prefix}kv"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = var.key_vault_sku
  tags                = local.required_tags

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "get",
      "set",
      "list"
    ]
  }
}

# Create secrets
resource "azurerm_key_vault_secret" "secret_rg_name" {
  name         = "RG-NAME"
  value        = azurerm_resource_group.rg.name
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "secret_acr_login" {
  name         = "ACR-LOGIN"
  value        = azurerm_container_registry.acr.login_server
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "secret_acr_username" {
  name         = "ACR-USERNAME"
  value        = azurerm_container_registry.acr.admin_username
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "secret_acr_password" {
  name         = "ACR-PASSWORD"
  value        = azurerm_container_registry.acr.admin_password
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "secret_aks_name" {
  name         = "AKS-NAME"
  value        = azurerm_kubernetes_cluster.aks.name
  key_vault_id = azurerm_key_vault.kv.id
}
