output "resource_group_name" {
  description = "The resource group name."
  value = azurerm_resource_group.rg.name
}
output "acr_login_server" {
  description = "The URL that can be used to log into the container registry."
  value = azurerm_container_registry.acr.login_server
}
output "aks_name" {
  description = " The name of the kubernetes cluster."
  value = azurerm_kubernetes_cluster.aks.name
}
output "key_vault_name" {
  description = " The name of the key vault."
  value = azurerm_key_vault.kv.name
}