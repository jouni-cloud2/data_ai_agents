/**
 * # Azure Key Vault Module
 *
 * Creates an Azure Key Vault with secrets and access policies.
 *
 * ## Usage
 *
 * ```hcl
 * module "keyvault" {
 *   source = "github.com/your-org/data_ai_agents//terraform/modules/azure/keyvault"
 *
 *   name                = "kv-dataplatform-dev"
 *   resource_group_name = module.rg.name
 *   location            = module.rg.location
 *
 *   secrets = {
 *     "api-key" = var.api_key
 *   }
 *
 *   environment = "dev"
 *   project     = "data-platform"
 * }
 * ```
 */

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = var.sku_name

  soft_delete_retention_days = var.soft_delete_retention_days
  purge_protection_enabled   = var.purge_protection_enabled

  enable_rbac_authorization = var.enable_rbac_authorization

  network_acls {
    bypass                     = var.network_acls_bypass
    default_action             = var.network_acls_default_action
    ip_rules                   = var.network_acls_ip_rules
    virtual_network_subnet_ids = var.network_acls_subnet_ids
  }

  tags = merge(
    {
      environment = var.environment
      project     = var.project
      managed_by  = "terraform"
    },
    var.tags
  )
}

# Access policy for Terraform service principal
resource "azurerm_key_vault_access_policy" "terraform" {
  count = var.enable_rbac_authorization ? 0 : 1

  key_vault_id = azurerm_key_vault.this.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  secret_permissions = [
    "Get",
    "List",
    "Set",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
    "Purge"
  ]

  key_permissions = [
    "Get",
    "List",
    "Create",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
    "Purge"
  ]
}

# Create secrets
resource "azurerm_key_vault_secret" "secrets" {
  for_each = var.secrets

  name         = each.key
  value        = each.value
  key_vault_id = azurerm_key_vault.this.id
  content_type = lookup(var.secret_content_types, each.key, "text/plain")

  depends_on = [azurerm_key_vault_access_policy.terraform]
}
