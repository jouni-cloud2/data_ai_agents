variable "name" {
  description = "Name of the Key Vault"
  type        = string

  validation {
    condition     = can(regex("^kv-", var.name))
    error_message = "Key Vault name must start with 'kv-' prefix."
  }
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "sku_name" {
  description = "SKU name for the Key Vault"
  type        = string
  default     = "standard"

  validation {
    condition     = contains(["standard", "premium"], var.sku_name)
    error_message = "SKU must be 'standard' or 'premium'."
  }
}

variable "soft_delete_retention_days" {
  description = "Soft delete retention in days"
  type        = number
  default     = 90
}

variable "purge_protection_enabled" {
  description = "Enable purge protection"
  type        = bool
  default     = true
}

variable "enable_rbac_authorization" {
  description = "Use RBAC instead of access policies"
  type        = bool
  default     = false
}

variable "network_acls_bypass" {
  description = "Network ACLs bypass"
  type        = string
  default     = "AzureServices"
}

variable "network_acls_default_action" {
  description = "Default network ACL action"
  type        = string
  default     = "Deny"
}

variable "network_acls_ip_rules" {
  description = "Allowed IP addresses"
  type        = list(string)
  default     = []
}

variable "network_acls_subnet_ids" {
  description = "Allowed subnet IDs"
  type        = list(string)
  default     = []
}

variable "secrets" {
  description = "Map of secret names to values"
  type        = map(string)
  default     = {}
  sensitive   = true
}

variable "secret_content_types" {
  description = "Map of secret names to content types"
  type        = map(string)
  default     = {}
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project" {
  description = "Project name"
  type        = string
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
