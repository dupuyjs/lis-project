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

# Assign app container identity with acrpull role to pull images from registry (used by kubernetes)
resource "azurerm_role_assignment" "acr_pull_role" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "acrpull"
  principal_id         = azurerm_app_service.app_container.identity.principal_id
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
      "list",
      "delete"
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

# Create a Storage Account
resource "azurerm_storage_account" "sa" {
  name                     = "${local.name_prefix}sa"
  location                 = azurerm_resource_group.rg.location
  resource_group_name      = azurerm_resource_group.rg.name
  account_tier             = var.asa_account_tier
  account_replication_type = var.asa_replication_type
}

# Create an Application Insights
resource "azurerm_application_insights" "insights" {
  name                = "${local.name_prefix}ai"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = var.ai_app_type
}

# Create an Azure ML Workspace
resource "azurerm_machine_learning_workspace" "workspace" {
  name                    = "${local.name_prefix}mlw"
  location                = azurerm_resource_group.rg.location
  resource_group_name     = azurerm_resource_group.rg.name
  application_insights_id = azurerm_application_insights.insights.id
  key_vault_id            = azurerm_key_vault.kv.id
  storage_account_id      = azurerm_storage_account.sa.id

  identity {
    type = "SystemAssigned"
  }
}

# Create an Azure ML Compute Cluster
resource "azurerm_machine_learning_compute_instance" "compute_instance" {
  name                          = "${local.name_prefix}cc"
  location                      = azurerm_resource_group.rg.location
  virtual_machine_size          = var.ccluster_vm_size
  machine_learning_workspace_id = azurerm_machine_learning_workspace.workspace.id

  identity {
    type = "SystemAssigned"
  }
}

# Create an Azure Cognitive Services Account (SpeechServices)
resource "azurerm_cognitive_account" "cognitive_account" {
  name                = "${local.name_prefix}cognitive"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "SpeechServices"

  sku_name = var.cognitive_account_sku
}

resource "azurerm_app_service_plan" "app_plan" {
  name                = "${local.name_prefix}app_plan"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "Linux"
  reserved            = true

  sku {
    tier = "Standard"
    size = "S2"
  }
}

resource "azurerm_app_service" "app_container" {
  name                    = "${local.name_prefix}app"
  location                = azurerm_resource_group.rg.location
  resource_group_name     = azurerm_resource_group.rg.name
  app_service_plan_id     = azurerm_app_service_plan.app_plan.id
  https_only              = true
  client_affinity_enabled = true

  site_config {
    always_on                            = true
    acr_use_managed_identity_credentials = true
    acr_user_managed_identity_client_id  = azurerm_role_assignment.acr_pull_role.id

    linux_fx_version = "DOCKER|registry.hub.docker.com/tutum/hello-world"
  }

  identity {
    type = "SystemAssigned"
  }

  app_settings = {
    "AZURE_MONITOR_INSTRUMENTATION_KEY" = azurerm_application_insights.insights.instrumentation_key
  }
}
