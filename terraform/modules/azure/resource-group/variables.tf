variable "name" {
  description = "Name of the resource group"
  type        = string

  validation {
    condition     = can(regex("^rg-", var.name))
    error_message = "Resource group name must start with 'rg-' prefix."
  }
}

variable "location" {
  description = "Azure region for the resource group"
  type        = string
  default     = "westeurope"
}

variable "environment" {
  description = "Environment name (dev, test, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "Environment must be one of: dev, test, prod."
  }
}

variable "project" {
  description = "Project name for tagging"
  type        = string
}

variable "tags" {
  description = "Additional tags to apply"
  type        = map(string)
  default     = {}
}
