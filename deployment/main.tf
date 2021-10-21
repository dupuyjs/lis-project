terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=2.80.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "random_string" "random" {
  length  = 4
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
  name     = "rg-${local.name_prefix}-${var.environment}"
  location = var.location
  tags     = local.required_tags
}

# Create azure container registry
resource "azurerm_container_registry" "acr" {
  name                = "cr${local.name_prefix}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = var.container_registry_sku
  admin_enabled       = true
  tags                = local.required_tags
}

# Assign app container identity with acrpull role to pull images from registry (used by kubernetes)
resource "azurerm_role_assignment" "acr_pull_role" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "acrpull"
  principal_id         = azurerm_app_service.app_container.identity[0].principal_id
}

# Create azure key vault
resource "azurerm_key_vault" "kv" {
  name                = "kv${local.name_prefix}"
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
      "list",
      "delete"
    ]
  }

  lifecycle {
    ignore_changes = [access_policy]
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

resource "azurerm_key_vault_secret" "secret_app_container_name" {
  name         = "APP-NAME"
  value        = azurerm_app_service.app_container.name
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "secret_storage_data_name" {
  name         = "STORAGE-DATA-NAME"
  value        = azurerm_storage_account.data_storage.name
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "secret_storage_data_key" {
  name         = "STORAGE-DATA-KEY"
  value        = azurerm_storage_account.data_storage.primary_access_key
  key_vault_id = azurerm_key_vault.kv.id
}

# Create storage accounts
resource "azurerm_storage_account" "ml_storage" {
  count                    = var.deploy_data_science_tools ? 1 : 0
  name                     = "st${local.name_prefix}ml"
  location                 = azurerm_resource_group.rg.location
  resource_group_name      = azurerm_resource_group.rg.name
  account_tier             = var.storage_account_tier
  account_replication_type = var.storage_replication_type
  tags                     = local.required_tags
}

resource "azurerm_storage_account" "data_storage" {
  name                     = "st${local.name_prefix}data"
  location                 = azurerm_resource_group.rg.location
  resource_group_name      = azurerm_resource_group.rg.name
  account_tier             = var.storage_account_tier
  account_replication_type = var.storage_replication_type
  tags                     = local.required_tags
}

# Create application insights
resource "azurerm_application_insights" "insights" {
  name                = "insights${local.name_prefix}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = var.insights_app_type
  tags                = local.required_tags
}

# Create azure ml workspace
resource "azurerm_machine_learning_workspace" "workspace" {
  count                   = var.deploy_data_science_tools ? 1 : 0
  name                    = "mlw${local.name_prefix}"
  location                = azurerm_resource_group.rg.location
  resource_group_name     = azurerm_resource_group.rg.name
  application_insights_id = azurerm_application_insights.insights.id
  key_vault_id            = azurerm_key_vault.kv.id
  storage_account_id      = azurerm_storage_account.ml_storage[0].id
  tags                    = local.required_tags

  identity {
    type = "SystemAssigned"
  }
}

# Create azure ml compute instance
resource "azurerm_machine_learning_compute_instance" "compute_instance" {
  count                         = var.deploy_data_science_tools ? 1 : 0
  name                          = "compute${local.name_prefix}"
  location                      = azurerm_resource_group.rg.location
  virtual_machine_size          = var.ml_instance_vm_size
  machine_learning_workspace_id = azurerm_machine_learning_workspace.workspace[0].id
  tags                          = local.required_tags

  identity {
    type = "SystemAssigned"
  }
}

# Create speech services account
resource "azurerm_cognitive_account" "speech" {
  name                = "speech${local.name_prefix}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "SpeechServices"
  sku_name            = var.cognitive_speech_account_sku
  tags                = local.required_tags
}

# Create web app for containers
resource "azurerm_app_service_plan" "app_plan" {
  name                = "plan${local.name_prefix}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "Linux"
  reserved            = true
  tags                = local.required_tags

  sku {
    tier = "Standard"
    size = "S2"
  }
}

resource "azurerm_app_service" "app_container" {
  name                    = "webapp${local.name_prefix}"
  location                = azurerm_resource_group.rg.location
  resource_group_name     = azurerm_resource_group.rg.name
  app_service_plan_id     = azurerm_app_service_plan.app_plan.id
  https_only              = true
  client_affinity_enabled = true
  tags                    = local.required_tags

  site_config {
    always_on                            = true
    acr_use_managed_identity_credentials = true

    linux_fx_version = "DOCKER|registry.hub.docker.com/tutum/hello-world"
  }

  identity {
    type = "SystemAssigned"
  }

  app_settings = {
    "AZURE_MONITOR_INSTRUMENTATION_KEY" = azurerm_application_insights.insights.instrumentation_key
  }
}

# Create azure cognitive search
resource "azurerm_search_service" "search" {
  name                = "search${local.name_prefix}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "basic"
}
