/**
 * # Azure Networking Module
 *
 * Creates VNet, subnets, and network security groups for data platform.
 *
 * ## Usage
 *
 * ```hcl
 * module "network" {
 *   source = "github.com/your-org/data_ai_agents//terraform/modules/azure/networking"
 *
 *   name                = "vnet-dataplatform-dev"
 *   resource_group_name = module.rg.name
 *   location            = module.rg.location
 *
 *   address_space = ["10.0.0.0/16"]
 *
 *   subnets = {
 *     "data" = {
 *       address_prefixes  = ["10.0.1.0/24"]
 *       service_endpoints = ["Microsoft.Storage", "Microsoft.KeyVault"]
 *     }
 *     "compute" = {
 *       address_prefixes  = ["10.0.2.0/24"]
 *       service_endpoints = ["Microsoft.Storage"]
 *     }
 *   }
 *
 *   environment = "dev"
 *   project     = "data-platform"
 * }
 * ```
 */

resource "azurerm_virtual_network" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  address_space       = var.address_space

  dns_servers = var.dns_servers

  tags = merge(
    {
      environment = var.environment
      project     = var.project
      managed_by  = "terraform"
    },
    var.tags
  )
}

resource "azurerm_subnet" "subnets" {
  for_each = var.subnets

  name                 = each.key
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes     = each.value.address_prefixes
  service_endpoints    = lookup(each.value, "service_endpoints", [])

  dynamic "delegation" {
    for_each = lookup(each.value, "delegation", null) != null ? [each.value.delegation] : []
    content {
      name = delegation.value.name
      service_delegation {
        name    = delegation.value.service_name
        actions = lookup(delegation.value, "actions", [])
      }
    }
  }
}

# Network Security Group for each subnet
resource "azurerm_network_security_group" "subnets" {
  for_each = var.create_nsg_per_subnet ? var.subnets : {}

  name                = "nsg-${each.key}"
  location            = var.location
  resource_group_name = var.resource_group_name

  tags = merge(
    {
      environment = var.environment
      project     = var.project
      managed_by  = "terraform"
    },
    var.tags
  )
}

resource "azurerm_subnet_network_security_group_association" "subnets" {
  for_each = var.create_nsg_per_subnet ? var.subnets : {}

  subnet_id                 = azurerm_subnet.subnets[each.key].id
  network_security_group_id = azurerm_network_security_group.subnets[each.key].id
}

# Private DNS Zone for private endpoints (optional)
resource "azurerm_private_dns_zone" "zones" {
  for_each = toset(var.private_dns_zones)

  name                = each.value
  resource_group_name = var.resource_group_name

  tags = merge(
    {
      environment = var.environment
      project     = var.project
      managed_by  = "terraform"
    },
    var.tags
  )
}

resource "azurerm_private_dns_zone_virtual_network_link" "links" {
  for_each = toset(var.private_dns_zones)

  name                  = "link-${replace(each.value, ".", "-")}"
  resource_group_name   = var.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.zones[each.key].name
  virtual_network_id    = azurerm_virtual_network.this.id
  registration_enabled  = false

  tags = merge(
    {
      environment = var.environment
      project     = var.project
      managed_by  = "terraform"
    },
    var.tags
  )
}
