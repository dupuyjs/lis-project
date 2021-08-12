variable "prefix" {
  description = "The prefix name used to create all resources."
  type        = string
  default     = "lis"
}
variable "location" {
  description = "The location of all resources."
  type        = string
  default     = "westeurope"
}
variable "environment" {
  description = "Environment flag, used in resource group name and resource tags."
  type        = string
  default     = "dev"
}
variable "container_registry_sku" {
  description = "Azure container registry sku."
  type        = string
  default     = "Basic"
}
variable "key_vault_sku" {
  description = "Azure key vault sku."
  type        = string
  default     = "standard"
}
variable "aks_pool_node_count" {
  description = "The initial number of nodes which should exist in the default node pool."
  type        = number
  default     = 1
}
variable "aks_pool_vm_size" {
  description = "The size of the Virtual Machine."
  type        = string
  default     = "Standard_NC6"
}