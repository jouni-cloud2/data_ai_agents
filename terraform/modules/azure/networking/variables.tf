variable "name" {
  description = "Name of the virtual network"
  type        = string

  validation {
    condition     = can(regex("^vnet-", var.name))
    error_message = "Virtual network name must start with 'vnet-' prefix."
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

variable "address_space" {
  description = "Address space for the VNet"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "dns_servers" {
  description = "Custom DNS servers"
  type        = list(string)
  default     = []
}

variable "subnets" {
  description = "Map of subnet configurations"
  type = map(object({
    address_prefixes  = list(string)
    service_endpoints = optional(list(string), [])
    delegation = optional(object({
      name         = string
      service_name = string
      actions      = optional(list(string), [])
    }))
  }))
  default = {}
}

variable "create_nsg_per_subnet" {
  description = "Create a Network Security Group for each subnet"
  type        = bool
  default     = true
}

variable "private_dns_zones" {
  description = "Private DNS zones to create for private endpoints"
  type        = list(string)
  default     = []
  # Common values:
  # - "privatelink.blob.core.windows.net"
  # - "privatelink.dfs.core.windows.net"
  # - "privatelink.vaultcore.azure.net"
  # - "privatelink.database.windows.net"
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
