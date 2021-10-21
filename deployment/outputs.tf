output "resource_group_name" {
  description = "The resource group name."
  value       = azurerm_resource_group.rg.name
}

output "acr_login_server" {
  description = "The url that can be used to log into the container registry."
  value       = azurerm_container_registry.acr.login_server
}

output "acr_server_username" {
  description = "The username that can be used to log into the container registry."
  value       = azurerm_container_registry.acr.admin_username
}

output "acr_server_password" {
  description = "The password that can be used to log into the container registry."
  value       = azurerm_container_registry.acr.admin_password
  sensitive   = true
}

output "key_vault_name" {
  description = "The name of the key vault."
  value       = azurerm_key_vault.kv.name
}

output "ml_storage_account_name" {
  description = "The ml storage account name."
  value       = var.deploy_data_science_tools ? azurerm_storage_account.ml_storage[0].name : ""
}

output "data_storage_account_name" {
  description = "The data storage account name."
  value       = azurerm_storage_account.data_storage.name
}

output "ml_workspace_name" {
  description = "The ml workspace name."
  value       = var.deploy_data_science_tools ? azurerm_machine_learning_workspace.workspace[0].name : ""
}

output "ml_compute_instance_name" {
  description = "The ml compute instance name."
  value       = var.deploy_data_science_tools ? azurerm_machine_learning_compute_instance.compute_instance[0].name : ""
}

output "speechservice_cognitive_name" {
  description = "The speech service name."
  value       = azurerm_cognitive_account.speech.name
}

output "speechservice_cognitive_key" {
  description = "The speech service subscription key."
  value       = azurerm_cognitive_account.speech.primary_access_key
  sensitive   = true
}

output "app_service_webapp_hostname" {
  description = "The url of the app service webapp."
  value       = azurerm_app_service.app_container.default_site_hostname
}
