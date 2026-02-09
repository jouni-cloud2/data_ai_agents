# Microsoft Fabric Terraform Modules

Terraform modules for Microsoft Fabric infrastructure.

> **Note**: Fabric does not have an official Terraform provider. These modules use the Azure REST API or AzAPI provider.

## Available Modules

| Module | Status | Description |
|--------|--------|-------------|
| workspace/ | Planned | Fabric workspace via REST API |
| capacity/ | Planned | Fabric capacity management |

## Provider Configuration

```hcl
terraform {
  required_providers {
    azapi = {
      source  = "Azure/azapi"
      version = "~> 1.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}
```

## Fabric API Approach

Since Fabric lacks a native provider, use:
1. **AzAPI provider** for Fabric capacity
2. **REST API calls** for workspace/lakehouse management
3. **Git integration** for artifact deployment

## Example: Fabric Capacity

```hcl
resource "azapi_resource" "fabric_capacity" {
  type      = "Microsoft.Fabric/capacities@2022-07-01-preview"
  name      = "fabric-capacity-dev"
  location  = "westeurope"
  parent_id = azurerm_resource_group.main.id

  body = jsonencode({
    sku = {
      name = "F2"
      tier = "Fabric"
    }
    properties = {
      administration = {
        members = ["admin@company.com"]
      }
    }
  })
}
```

## Limitations

- No Terraform provider for workspaces, lakehouses, notebooks
- Use Git integration for artifact deployment
- API changes may require module updates

## References

- [Fabric REST API](https://learn.microsoft.com/rest/api/fabric/)
- [AzAPI Provider](https://registry.terraform.io/providers/Azure/azapi/latest/docs)

---

*Last Updated: 2026-02-09*
