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
variable "service_principal_objectid" {
  description = "Service principal object id."
  type        = string
  sensitive   = true
}
variable "container_registry_sku" {
  description = "Azure container registry sku."
  type        = string
  default     = "Basic"
}