# Terraform Modules

Reusable Terraform modules for data platform infrastructure.

## Module Structure

```
terraform/
├── modules/
│   ├── fabric/          # Microsoft Fabric resources
│   ├── databricks/      # Databricks workspaces
│   ├── snowflake/       # Snowflake resources
│   ├── azure/           # Azure services (Key Vault, Storage, etc.)
│   ├── aws/             # AWS services (S3, Glue, etc.)
│   └── gcp/             # GCP services (BigQuery, GCS, etc.)
└── examples/            # Example usage patterns
```

## Module Status

| Module | Status | Description |
|--------|--------|-------------|
| [fabric/](modules/fabric/) | Planned | Fabric workspace, lakehouse (via API) |
| [databricks/](modules/databricks/) | Planned | Workspace, cluster, Unity Catalog |
| [snowflake/](modules/snowflake/) | Planned | Database, warehouse, roles |
| [azure/](modules/azure/) | Planned | Key Vault, Storage, networking |
| [aws/](modules/aws/) | Planned | S3, Glue, IAM |
| [gcp/](modules/gcp/) | Planned | BigQuery, GCS, IAM |

## Usage Pattern

```hcl
# Example: Using the Azure module for Key Vault
module "keyvault" {
  source = "github.com/your-org/data_ai_agents//terraform/modules/azure/keyvault"

  name                = "kv-dataplatform-dev"
  resource_group_name = "rg-dataplatform-dev"
  location            = "westeurope"

  secrets = {
    "api-key" = var.api_key
  }
}
```

## Contributing Modules

### Module Requirements

Each module should have:
- `README.md` - Documentation with examples
- `variables.tf` - Input variables with descriptions
- `outputs.tf` - Output values
- `main.tf` - Main resource definitions
- `versions.tf` - Provider version constraints

### Module Template

```
modules/{platform}/{resource}/
├── README.md
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
└── examples/
    └── basic/
        └── main.tf
```

## Best Practices

1. **Use version constraints** - Pin provider versions
2. **Document everything** - Variables, outputs, usage
3. **Follow naming conventions** - Consistent resource naming
4. **Enable tagging** - Support for resource tags
5. **Secure by default** - Encryption, least privilege

## References

- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [Terraform Module Registry](https://registry.terraform.io/)
- [Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Databricks Provider](https://registry.terraform.io/providers/databricks/databricks/latest/docs)
- [Snowflake Provider](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs)

---

*Last Updated: 2026-02-09*
