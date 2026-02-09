# Microsoft Fabric

Platform-specific guidance for building data platforms on Microsoft Fabric.

## Overview

Microsoft Fabric is a unified analytics platform combining:
- **OneLake**: Unified data lake storage
- **Lakehouse**: Delta Lake tables with SQL analytics
- **Data Factory**: Data integration pipelines
- **Notebooks**: PySpark/SQL development
- **Semantic Models**: Power BI integration

## When to Use Fabric

| Use Case | Fit |
|----------|-----|
| Microsoft-centric organization | Excellent |
| Power BI heavy workloads | Excellent |
| Unified analytics platform | Excellent |
| Multi-cloud data mesh | Limited |
| Real-time streaming (complex) | Limited |

## Fabric Documentation Index

| Topic | Description |
|-------|-------------|
| [Workspace Patterns](workspace-patterns.md) | Organizing workspaces by domain/environment |
| [Notebook Standards](notebook-standards.md) | PySpark development in Fabric |
| [Pipeline Patterns](pipelines.md) | Data Factory pipeline design |
| [OneLake Patterns](onelake-patterns.md) | Storage, shortcuts, file organization |
| [Pitfalls](pitfalls.md) | Common mistakes and solutions |

## Quick Reference

### Naming Conventions

| Object | Pattern | Example |
|--------|---------|---------|
| Workspace | `{domain}_{env}` | `sales_dev` |
| Lakehouse | `lh_{domain}_{env}` | `lh_sales_dev` |
| Bronze table | `bronze_{source}_{entity}` | `bronze_hubspot_companies` |
| Silver table | `silver_{entity}` | `silver_companies` |
| Gold dimension | `dim_{entity}` | `dim_customer` |
| Gold fact | `fact_{process}` | `fact_sales` |
| Pipeline | `pl_{action}_{entity}_{freq}` | `pl_ingest_companies_daily` |
| Notebook | `nb_{layer}_{action}_{entity}` | `nb_bronze_load_companies` |

### Key Vault Access

```python
from notebookutils import mssparkutils

# Get secret from Key Vault
api_key = mssparkutils.credentials.getSecret("keyvault-name", "secret-name")
```

### Lakehouse Tables

```python
# Write to table
df.write.format("delta").mode("append").saveAsTable("bronze_companies")

# Read from table
df = spark.table("silver_companies")

# SQL query
df = spark.sql("SELECT * FROM gold.dim_customer WHERE is_current = true")
```

### OneLake Paths

```
abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{lakehouse_id}/Tables/{table}
abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{lakehouse_id}/Files/{path}
```

## Architecture Patterns

### Domain Workspace Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOMAIN WORKSPACE PATTERN                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   sales_dev     │  │   sales_test    │  │   sales_prod    │ │
│  │   (Workspace)   │  │   (Workspace)   │  │   (Workspace)   │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                    │           │
│           ▼                    ▼                    ▼           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                      Git Repository                         ││
│  │   main ←── test ←── dev (branches per environment)          ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Lakehouse Structure

```
{lakehouse}/
├── Files/
│   └── landing/
│       └── {source}/
│           └── {entity}/
│               └── {date}/
│                   └── data_{timestamp}.json
└── Tables/
    ├── bronze_{source}_{entity}
    ├── silver_{entity}
    ├── dim_{entity}
    └── fact_{process}
```

## Key Capabilities

### Git Integration

Fabric supports Git integration for version control:

```yaml
# Workspace → Git connection
Repository: github.com/org/repo
Branch: dev  # Environment-specific branch
Root folder: fabric/{workspace}
```

### Shortcuts

Link data without copying:

```python
# Create shortcut to external data
# (Via Fabric UI or API)
# Shortcuts appear as tables in lakehouse
```

### Semantic Models

Connect Gold tables to Power BI:

```
Lakehouse Gold Tables → Semantic Model → Power BI Reports
```

## Platform Limitations

| Limitation | Workaround |
|------------|------------|
| No Terraform provider | Use REST API or Azure Resource Manager |
| Git sync can be slow | Small, frequent commits |
| Limited streaming support | Use Azure Event Hubs + notebooks |
| Capacity throttling | Monitor capacity usage, scale up |

## References

- [Microsoft Fabric Documentation](https://learn.microsoft.com/fabric/)
- [Fabric Well-Architected](https://learn.microsoft.com/fabric/well-architected/)
- [OneLake Documentation](https://learn.microsoft.com/fabric/onelake/)
- [Fabric REST API](https://learn.microsoft.com/rest/api/fabric/)

---

*Last Updated: 2026-02-09*
