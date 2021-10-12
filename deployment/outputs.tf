output "resource_group_name" {
  description = "The resource group name."
  value       = azurerm_resource_group.rg.name
}

output "acr_login_server" {
  description = "The URL that can be used to log into the container registry."
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

output "storage_account_name" {
  description = "The Storage Account name."
  value       = azurerm_storage_account.sa.name
}

output "ml_workspace_name" {
  description = "The ML Workspace name."
  value       = azurerm_machine_learning_workspace.workspace.name
}

output "ml_compute_instance_name" {
  description = "The ML Compute Cluster name."
  value       = azurerm_machine_learning_compute_instance.compute_instance.name
}

output "speechservices_cognitiveaccount_name" {
  description = "The Cognitive Service Account name."
  value       = azurerm_cognitive_account.cognitive_account.name
}

output "speechservices_cognitiveaccount_key" {
  description = "The Cognitive Service Account Key."
  value       = azurerm_cognitive_account.cognitive_account.primary_access_key
  sensitive   = true
}

output "app_service_webapp_hostname" {
  description = "The URL of the App Service Webapp"
  value       = azurerm_app_service.app_container.default_site_hostname
}
