/**
 * # Azure Resource Group Module
 *
 * Creates an Azure Resource Group with standardized tagging.
 *
 * ## Usage
 *
 * ```hcl
 * module "rg" {
 *   source = "github.com/your-org/data_ai_agents//terraform/modules/azure/resource-group"
 *
 *   name        = "rg-dataplatform-dev"
 *   location    = "westeurope"
 *   environment = "dev"
 *   project     = "data-platform"
 * }
 * ```
 */

resource "azurerm_resource_group" "this" {
  name     = var.name
  location = var.location

  tags = merge(
    {
      environment = var.environment
      project     = var.project
      managed_by  = "terraform"
      created_at  = timestamp()
    },
    var.tags
  )

  lifecycle {
    ignore_changes = [tags["created_at"]]
  }
}
