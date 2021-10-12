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

variable "asa_account_tier" {
  description = "The Tier level of the Storage Account."
  type        = string
  default     = "Standard"
}

variable "asa_replication_type" {
  description = "The Storage Account Replication Type."
  type        = string
  default     = "LRS"
}

variable "ai_app_type" {
  description = "Specifies the type of Application Insights to create."
  type        = string
  default     = "web"
}

variable "ccluster_vm_priority" {
  description = "The priority of the VM."
  type        = string
  default     = "Dedicated"
}

variable "ccluster_vm_size" {
  description = "The size of the ML Compute Cluster VM."
  type        = string
  default     = "Standard_NC6"
}

variable "ccluster_scale_min_node_count" {
  description = "Minimal node count."
  type        = number
  default     = 0
}

variable "ccluster_scale_max_node_count" {
  description = "Maximal node count."
  type        = number
  default     = 1
}

variable "cognitive_account_sku" {
  description = "Specifies the SKU Name for this Cognitive Service Account."
  type        = string
  default     = "S0"
}
