# Snowflake Terraform Modules

Reusable Terraform modules for Snowflake infrastructure.

## Available Modules

| Module | Status | Description |
|--------|--------|-------------|
| database/ | Planned | Database and schemas |
| warehouse/ | Planned | Virtual warehouses |
| roles/ | Planned | Role-based access control |
| stages/ | Planned | External stages for data loading |

## Provider Configuration

```hcl
terraform {
  required_providers {
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.70"
    }
  }
}

provider "snowflake" {
  account   = var.snowflake_account
  username  = var.snowflake_username
  password  = var.snowflake_password
  role      = "SYSADMIN"
}
```

## Example Usage

```hcl
module "database" {
  source = "./modules/snowflake/database"

  name    = "DATAPLATFORM_${upper(var.environment)}"
  schemas = ["BRONZE", "SILVER", "GOLD"]
}

module "warehouse" {
  source = "./modules/snowflake/warehouse"

  name           = "TRANSFORM_WH"
  size           = "XSMALL"
  auto_suspend   = 60
  auto_resume    = true
}
```

## References

- [Snowflake Terraform Provider](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs)
- [Snowflake Resource Provisioning](https://docs.snowflake.com/en/user-guide/organizations-manage-accounts)

---

*Last Updated: 2026-02-09*
