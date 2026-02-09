# Azure Data Services

Platform-specific guidance for Azure data services (non-Fabric).

> **Status**: Documentation planned. Contributions welcome.

## Overview

Azure provides multiple data services:
- **Azure Synapse Analytics**: Unified analytics platform
- **Azure Data Factory**: Data integration
- **Azure Data Lake Storage Gen2**: Scalable data lake
- **Azure SQL Database**: Managed SQL Server
- **Azure Cosmos DB**: Multi-model NoSQL
- **Azure Event Hubs**: Event streaming

## When to Use Azure Services

| Service | Use Case |
|---------|----------|
| **Synapse** | Enterprise data warehouse, before Fabric |
| **Data Factory** | Data integration without Fabric |
| **ADLS Gen2** | Data lake storage for any platform |
| **Event Hubs** | Real-time event ingestion |
| **Key Vault** | Secret management (all platforms) |

## Planned Documentation

- [ ] Synapse workspace patterns
- [ ] Data Factory pipeline design
- [ ] ADLS organization patterns
- [ ] Event Hubs integration
- [ ] Key Vault best practices
- [ ] Virtual network security
- [ ] Cost optimization

## Terraform Modules

See [terraform/modules/azure/](../../../terraform/modules/azure/) for ready-to-use infrastructure modules:
- Resource groups
- Key Vault
- Storage accounts
- Networking

## Key References

- [Azure Data Documentation](https://learn.microsoft.com/azure/data/)
- [Synapse Analytics](https://learn.microsoft.com/azure/synapse-analytics/)
- [Data Factory](https://learn.microsoft.com/azure/data-factory/)
- [Azure Terraform Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)

## Shared Principles

All Azure implementations follow:
- [Well-Architected Framework](../../principles/well-architected.md)
- [Data Governance](../../principles/data-governance.md)
- [Security & Privacy](../../principles/security-privacy.md)

---

*Last Updated: 2026-02-09*
