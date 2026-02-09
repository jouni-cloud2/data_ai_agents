/**
 * # Azure Storage Account Module
 *
 * Creates an Azure Storage Account configured for data lake usage.
 *
 * ## Usage
 *
 * ```hcl
 * module "storage" {
 *   source = "github.com/your-org/data_ai_agents//terraform/modules/azure/storage"
 *
 *   name                = "stdataplatformdev"
 *   resource_group_name = module.rg.name
 *   location            = module.rg.location
 *
 *   containers = ["bronze", "silver", "gold"]
 *
 *   environment = "dev"
 *   project     = "data-platform"
 * }
 * ```
 */

resource "azurerm_storage_account" "this" {
  name                = var.name
  resource_group_name = var.resource_group_name
  location            = var.location

  account_tier             = var.account_tier
  account_replication_type = var.account_replication_type
  account_kind             = var.account_kind

  # Data lake settings
  is_hns_enabled           = var.enable_hierarchical_namespace
  sftp_enabled             = var.enable_sftp
  nfsv3_enabled            = var.enable_nfsv3
  large_file_share_enabled = var.enable_large_file_share

  # Security
  min_tls_version                 = var.min_tls_version
  allow_nested_items_to_be_public = var.allow_public_access
  shared_access_key_enabled       = var.enable_shared_access_key

  blob_properties {
    versioning_enabled       = var.enable_versioning
    change_feed_enabled      = var.enable_change_feed
    last_access_time_enabled = var.enable_last_access_time

    dynamic "delete_retention_policy" {
      for_each = var.blob_soft_delete_days > 0 ? [1] : []
      content {
        days = var.blob_soft_delete_days
      }
    }

    dynamic "container_delete_retention_policy" {
      for_each = var.container_soft_delete_days > 0 ? [1] : []
      content {
        days = var.container_soft_delete_days
      }
    }
  }

  network_rules {
    default_action             = var.network_default_action
    bypass                     = var.network_bypass
    ip_rules                   = var.network_ip_rules
    virtual_network_subnet_ids = var.network_subnet_ids
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

# Create containers
resource "azurerm_storage_container" "containers" {
  for_each = toset(var.containers)

  name                  = each.value
  storage_account_id    = azurerm_storage_account.this.id
  container_access_type = "private"
}

# Create file systems for data lake (if HNS enabled)
resource "azurerm_storage_data_lake_gen2_filesystem" "filesystems" {
  for_each = var.enable_hierarchical_namespace ? toset(var.data_lake_filesystems) : toset([])

  name               = each.value
  storage_account_id = azurerm_storage_account.this.id
}
