# Databricks Terraform Modules

Reusable Terraform modules for Databricks infrastructure.

## Available Modules

| Module | Status | Description |
|--------|--------|-------------|
| workspace/ | Planned | Databricks workspace |
| cluster/ | Planned | Compute clusters |
| unity-catalog/ | Planned | Unity Catalog setup |
| secret-scope/ | Planned | Secret management |

## Provider Configuration

```hcl
terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.0"
    }
  }
}

provider "databricks" {
  host = var.databricks_host
  # Use one of: token, azure CLI, service principal
}
```

## Example Usage

```hcl
# Workspace (on Azure)
module "databricks_workspace" {
  source = "./modules/databricks/workspace"

  name                = "dbw-dataplatform-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "premium"

  tags = {
    environment = var.environment
  }
}

# Unity Catalog
module "unity_catalog" {
  source = "./modules/databricks/unity-catalog"

  metastore_name = "dataplatform-metastore"
  catalog_name   = "main"
  schemas        = ["bronze", "silver", "gold"]
}
```

## References

- [Databricks Terraform Provider](https://registry.terraform.io/providers/databricks/databricks/latest/docs)
- [Databricks on Azure](https://learn.microsoft.com/azure/databricks/)
- [Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)

---

*Last Updated: 2026-02-09*
