variable "name" {
  description = "Name of the storage account (3-24 lowercase alphanumeric)"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.name))
    error_message = "Storage account name must be 3-24 lowercase alphanumeric characters."
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

variable "account_tier" {
  description = "Storage account tier"
  type        = string
  default     = "Standard"
}

variable "account_replication_type" {
  description = "Replication type (LRS, GRS, RAGRS, ZRS)"
  type        = string
  default     = "LRS"
}

variable "account_kind" {
  description = "Account kind (StorageV2, BlobStorage, etc.)"
  type        = string
  default     = "StorageV2"
}

# Data Lake Settings
variable "enable_hierarchical_namespace" {
  description = "Enable HNS for Data Lake Gen2"
  type        = bool
  default     = true
}

variable "enable_sftp" {
  description = "Enable SFTP"
  type        = bool
  default     = false
}

variable "enable_nfsv3" {
  description = "Enable NFSv3"
  type        = bool
  default     = false
}

variable "enable_large_file_share" {
  description = "Enable large file shares"
  type        = bool
  default     = false
}

# Security
variable "min_tls_version" {
  description = "Minimum TLS version"
  type        = string
  default     = "TLS1_2"
}

variable "allow_public_access" {
  description = "Allow public access to blobs"
  type        = bool
  default     = false
}

variable "enable_shared_access_key" {
  description = "Enable shared access key authentication"
  type        = bool
  default     = true
}

# Blob Properties
variable "enable_versioning" {
  description = "Enable blob versioning"
  type        = bool
  default     = true
}

variable "enable_change_feed" {
  description = "Enable change feed"
  type        = bool
  default     = true
}

variable "enable_last_access_time" {
  description = "Enable last access time tracking"
  type        = bool
  default     = false
}

variable "blob_soft_delete_days" {
  description = "Soft delete retention for blobs (0 to disable)"
  type        = number
  default     = 7
}

variable "container_soft_delete_days" {
  description = "Soft delete retention for containers (0 to disable)"
  type        = number
  default     = 7
}

# Network Rules
variable "network_default_action" {
  description = "Default network action"
  type        = string
  default     = "Deny"
}

variable "network_bypass" {
  description = "Network bypass options"
  type        = list(string)
  default     = ["AzureServices"]
}

variable "network_ip_rules" {
  description = "Allowed IP addresses"
  type        = list(string)
  default     = []
}

variable "network_subnet_ids" {
  description = "Allowed subnet IDs"
  type        = list(string)
  default     = []
}

# Containers
variable "containers" {
  description = "List of blob containers to create"
  type        = list(string)
  default     = []
}

variable "data_lake_filesystems" {
  description = "List of Data Lake Gen2 filesystems to create"
  type        = list(string)
  default     = ["bronze", "silver", "gold"]
}

# Tags
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
