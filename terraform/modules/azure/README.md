# Azure Terraform Modules

Reusable Terraform modules for Azure data platform infrastructure.

## Available Modules

| Module | Status | Description |
|--------|--------|-------------|
| [resource-group/](resource-group/) | Ready | Resource group with standardized tagging |
| [keyvault/](keyvault/) | Ready | Key Vault with secrets and access policies |
| [storage/](storage/) | Ready | Storage Account configured for Data Lake |
| [networking/](networking/) | Ready | VNet, subnets, NSGs, private DNS |

## Provider Configuration

```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }
}
```

## Example Usage

### Complete Data Platform Setup

```hcl
# Resource Group
module "rg" {
  source = "./modules/azure/resource-group"

  name        = "rg-dataplatform-${var.environment}"
  location    = var.location
  environment = var.environment
  project     = "data-platform"
}

# Networking
module "network" {
  source = "./modules/azure/networking"

  name                = "vnet-dataplatform-${var.environment}"
  resource_group_name = module.rg.name
  location            = module.rg.location

  address_space = ["10.0.0.0/16"]

  subnets = {
    "data" = {
      address_prefixes  = ["10.0.1.0/24"]
      service_endpoints = ["Microsoft.Storage", "Microsoft.KeyVault"]
    }
    "compute" = {
      address_prefixes  = ["10.0.2.0/24"]
      service_endpoints = ["Microsoft.Storage"]
    }
  }

  private_dns_zones = [
    "privatelink.blob.core.windows.net",
    "privatelink.dfs.core.windows.net",
    "privatelink.vaultcore.azure.net"
  ]

  environment = var.environment
  project     = "data-platform"
}

# Key Vault
module "keyvault" {
  source = "./modules/azure/keyvault"

  name                = "kv-dataplatform-${var.environment}"
  resource_group_name = module.rg.name
  location            = module.rg.location

  network_acls_subnet_ids = [module.network.subnet_ids["data"]]

  secrets = {
    "api-key" = var.api_key
  }

  environment = var.environment
  project     = "data-platform"
}

# Data Lake Storage
module "storage" {
  source = "./modules/azure/storage"

  name                = "stdataplatform${var.environment}"
  resource_group_name = module.rg.name
  location            = module.rg.location

  enable_hierarchical_namespace = true
  data_lake_filesystems         = ["bronze", "silver", "gold"]

  network_subnet_ids = [module.network.subnet_ids["data"]]

  environment = var.environment
  project     = "data-platform"
}
```

## Naming Conventions

| Resource | Prefix | Example |
|----------|--------|---------|
| Resource Group | `rg-` | `rg-dataplatform-dev` |
| Virtual Network | `vnet-` | `vnet-dataplatform-dev` |
| Key Vault | `kv-` | `kv-dataplatform-dev` |
| Storage Account | `st` | `stdataplatformdev` |

## Security Best Practices

1. **Network isolation** - Use private endpoints and service endpoints
2. **Key Vault** - Store all secrets in Key Vault, not in code
3. **RBAC** - Use Azure RBAC instead of access policies where possible
4. **Encryption** - Enable encryption at rest and in transit
5. **Soft delete** - Enable soft delete for recovery

## References

- [Azure Provider Documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure Best Practices](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/)
- [Azure Naming Conventions](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming)

---

*Last Updated: 2026-02-09*
