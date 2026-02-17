# Fabric Workspace Patterns

Organizing Microsoft Fabric workspaces for data platforms.

## Workspace Strategy

### Domain + Environment Pattern

One workspace per domain per environment:

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKSPACE ORGANIZATION                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Domain       Dev              Test             Prod            │
│  ──────────────────────────────────────────────────────────────│
│  Sales        sales_dev        sales_test       sales_prod      │
│  HR           hr_dev           hr_test          hr_prod         │
│  Finance      finance_dev      finance_test     finance_prod    │
│  Analytics    analytics_dev    analytics_test   analytics_prod  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Naming Convention

| Component | Pattern | Example |
|-----------|---------|---------|
| Workspace | `{domain}_{env}` | `sales_dev` |
| Lakehouse | `lh_{domain}_{env}` | `lh_sales_dev` |
| Warehouse | `wh_{domain}_{env}` | `wh_sales_dev` |

### Capacity Assignment

| Environment | Capacity | Rationale |
|-------------|----------|-----------|
| Dev | F2 (shared) | Cost-effective for development |
| Test | F2 (shared) | Integration testing |
| Prod | F4+ (dedicated) | Production performance |

## Workspace Contents

### Standard Lakehouse Structure

Each workspace contains:

```
{domain}_{env} (Workspace)
├── lh_{domain}_{env} (Lakehouse)
│   ├── Tables/
│   │   ├── bronze_{source}_{entity}
│   │   ├── silver_{entity}
│   │   ├── dim_{entity}
│   │   └── fact_{process}
│   └── Files/
│       └── landing/
│           └── {source}/{entity}/{date}/
├── Notebooks/
│   ├── nb_bronze_load_{source}_{entity}
│   ├── nb_silver_transform_{entity}
│   └── nb_gold_{dim|fact}_{entity}
├── Pipelines/
│   └── pl_ingest_{source}_daily
└── Semantic Models/
    └── sm_{domain}_{env}
```

### Dual Lakehouse per Domain

For domains with DDM (Dynamic Data Masking) or clear Bronze/Silver separation, use **two lakehouses** per workspace:

```
{domain}_{env} (Workspace)
├── lh_{domain}_bronze_{env} (Lakehouse — raw ingestion)
│   ├── Tables/
│   │   └── bronze_{source}_{entity}     # PII may be present
│   └── Files/
│       └── mock/{domain}/{entity}/      # Mock data (dev only)
│
├── lh_{domain}_curated_{env} (Lakehouse — silver + views)
│   ├── Tables/
│   │   └── silver_{entity}              # FK refs only, no raw PII
│   └── SQL Analytics Endpoint
│       └── vw_ddm_bronze_{source}_{entity}  # DDM masked views
│
└── Notebooks/
    ├── bronze_load_{source}             # Default: lh_{domain}_bronze_{env}
    ├── silver_transform_{source}        # Default: lh_{domain}_curated_{env}
    ├── setup_ddm_views_{domain}         # Deploys DDM views once
    └── util_generate_mock_data_{domain} # Generates dev fixture data
```

**When to use dual lakehouse:**
- Domain contains PII and needs DDM views for analyst access
- Silver tables should be isolated from raw bronze data
- Clear medallion boundary required (Bronze restricted, Curated open)

**Cross-lakehouse reads in notebooks:**

```python
# Silver notebook reads bronze across lakehouses
BRONZE_LAKEHOUSE = "lh_it_bronze_dev"
df = spark.table(f"{BRONZE_LAKEHOUSE}.bronze_freshservice_requesters")
```

## Git Integration

### Branch Strategy

```
main (prod)
├── test (test environment)
│   └── dev (development)
│       └── feature/* (feature branches)
```

### Workspace-Branch Mapping

| Workspace | Branch | Auto-sync |
|-----------|--------|-----------|
| `{domain}_dev` | `dev` | Yes |
| `{domain}_test` | `test` | Yes |
| `{domain}_prod` | `main` | Manual approval |

### Git Repository Structure

```
repository/
├── fabric/
│   ├── sales_dev/
│   │   ├── lh_sales_dev.Lakehouse/
│   │   ├── nb_bronze_load_hubspot.Notebook/
│   │   └── pl_ingest_hubspot.Pipeline/
│   └── sales_prod/
│       └── (same structure)
└── terraform/
    └── (infrastructure)
```

## Access Control

### Workspace Roles

| Role | Dev | Test | Prod |
|------|-----|------|------|
| Admin | Data Platform Team | Data Platform Team | Data Platform Team |
| Member | Data Engineers | Data Engineers (read) | - |
| Contributor | - | QA Team | - |
| Viewer | Business Analysts | Business Analysts | Business Analysts |

### Security Groups

```
# Azure AD Groups
data-platform-admins      → Admin (all workspaces)
data-engineers            → Member (dev), Contributor (test)
data-analysts-{domain}    → Viewer (prod)
```

## Cross-Workspace Access

### Shortcuts Pattern

Link data between workspaces without copying:

```
analytics_prod (Workspace)
└── lh_analytics_prod (Lakehouse)
    └── Shortcuts/
        ├── → sales_prod/gold_dim_customer
        ├── → hr_prod/gold_dim_employee
        └── → finance_prod/gold_fact_invoice
```

### Creating Shortcuts

```python
# Via Fabric REST API
import requests

def create_shortcut(
    workspace_id: str,
    lakehouse_id: str,
    shortcut_name: str,
    source_workspace_id: str,
    source_lakehouse_id: str,
    source_table: str
):
    """Create a shortcut to another lakehouse table."""

    url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/lakehouses/{lakehouse_id}/shortcuts"

    payload = {
        "name": shortcut_name,
        "target": {
            "oneLake": {
                "workspaceId": source_workspace_id,
                "itemId": source_lakehouse_id,
                "path": f"Tables/{source_table}"
            }
        }
    }

    response = requests.post(url, json=payload, headers=get_auth_headers())
    return response.json()
```

## Deployment Patterns

### Promotion Flow

```
Dev Workspace                Test Workspace              Prod Workspace
     │                            │                           │
     │  1. Developer commits      │                           │
     │  to dev branch             │                           │
     ▼                            │                           │
  Git Sync                        │                           │
     │                            │                           │
     │  2. PR: dev → test         │                           │
     └───────────────────────────►│                           │
                                  │                           │
                               Git Sync                       │
                                  │                           │
                                  │  3. PR: test → main       │
                                  └──────────────────────────►│
                                                              │
                                                           Git Sync
                                                           (manual)
```

### Deployment Pipeline (Alternative)

Use Fabric Deployment Pipelines for stage promotion:

```
Development → Test → Production
    │           │         │
    │    Deploy │  Deploy │
    └───────────┴─────────┘
```

## Workspace Metadata

### README Template

Each workspace should have documentation:

```markdown
# {Domain} {Environment} Workspace

## Overview
- **Domain**: {Domain name}
- **Environment**: {Dev/Test/Prod}
- **Capacity**: {Capacity name}
- **Git Branch**: {Branch name}

## Contents
- Lakehouse: lh_{domain}_{env}
- Tables: {count} Bronze, {count} Silver, {count} Gold
- Notebooks: {count}
- Pipelines: {count}

## Owners
- Business Owner: {name}
- Technical Owner: {name}

## Data Sources
- {Source 1}: {description}
- {Source 2}: {description}

## Schedule
- Daily refresh: 02:00 UTC
```

## Best Practices

| Practice | Rationale |
|----------|-----------|
| One lakehouse per workspace | Simplifies governance |
| Consistent naming | Enables automation |
| Git integration always | Version control, collaboration |
| Separate dev data | Compliance, see [Environment Separation](../../principles/environment-separation.md) |
| Document in workspace | Self-describing workspaces |

## References

- [Fabric Workspaces](https://learn.microsoft.com/fabric/get-started/workspaces)
- [Git Integration](https://learn.microsoft.com/fabric/cicd/git-integration/intro-to-git-integration)
- [Deployment Pipelines](https://learn.microsoft.com/fabric/cicd/deployment-pipelines/intro-to-deployment-pipelines)

---

*Last Updated: 2026-02-09*
