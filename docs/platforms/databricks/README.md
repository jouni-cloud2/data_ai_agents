# Databricks

Platform-specific guidance for building data platforms on Databricks.

> **Status**: Documentation planned. Contributions welcome.

## Overview

Databricks is a unified analytics platform built on Apache Spark:
- **Unity Catalog**: Unified governance across workspaces
- **Delta Lake**: ACID transactions on data lakes
- **Delta Live Tables**: Declarative ETL pipelines
- **Workflows**: Orchestration and scheduling
- **SQL Warehouses**: SQL analytics at scale

## When to Use Databricks

| Use Case | Fit |
|----------|-----|
| Multi-cloud data platform | Excellent |
| Advanced ML/AI workloads | Excellent |
| Large-scale data processing | Excellent |
| Real-time streaming | Excellent |
| Microsoft-only environment | Consider Fabric |

## Planned Documentation

- [ ] Workspace organization patterns
- [ ] Unity Catalog setup
- [ ] Delta Live Tables patterns
- [ ] Workflow design
- [ ] Notebook standards
- [ ] Cluster configuration
- [ ] Security best practices
- [ ] Cost optimization

## Terraform Modules

See [terraform/modules/databricks/](../../../terraform/modules/databricks/) for ready-to-use infrastructure modules.

## Key References

- [Databricks Documentation](https://docs.databricks.com/)
- [Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)
- [Delta Live Tables](https://docs.databricks.com/en/delta-live-tables/index.html)
- [Databricks Terraform Provider](https://registry.terraform.io/providers/databricks/databricks/latest/docs)
- [Lakehouse Architecture](https://docs.databricks.com/en/lakehouse-architecture/index.html)

## Shared Principles

All Databricks implementations follow:
- [Medallion Architecture](../../principles/medallion-architecture.md)
- [Data Governance](../../principles/data-governance.md)
- [Security & Privacy](../../principles/security-privacy.md)

---

*Last Updated: 2026-02-09*
