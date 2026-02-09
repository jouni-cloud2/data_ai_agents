# Data AI Agents

AI team for building enterprise data platforms. Currently supports **Microsoft Fabric** and **Azure**.

## Available MCP Servers

This project uses the following Model Context Protocol servers:

- **microsoft-docs** - Official Microsoft/Azure/Fabric documentation
- **azure** - Azure resource management and infrastructure (47+ services)
- **fabric** - Microsoft Fabric API access and development (Preview)
- **context7** - Library and SDK documentation (optional)

## Commands

| Command | Purpose |
|---------|---------|
| `/sdd` | Spec-Driven Development - implement features with full traceability |
| `/document` | Documentation maintenance - audit, create, update docs |
| `/architect` | Architecture guidance - decisions, planning, reviews |
| `/init-project` | Set up a new project subrepo |
| `/init-data-ai` | First-time setup of this AI team |
| `/improve-ai` | Capture learnings and improve the AI team |

## How It Works

1. **This repo** = AI team configuration + generic platform knowledge
2. **Project subrepos** in `projects/` = your actual work (gitignored)
3. Commands auto-detect your platform (Fabric, Databricks, etc.)

## Quick Start

```bash
/init-data-ai              # First time only - install tools
/init-project <git-url>    # Clone your project
/architect                 # Plan architecture decisions
/sdd "Add customer table"  # Implement with SDD workflow
```

## Documentation Structure

| Location | Content |
|----------|---------|
| `docs/principles/` | Platform-agnostic principles (governance, quality, etc.) |
| `docs/patterns/` | Reusable implementation patterns |
| `docs/platforms/fabric/` | Microsoft Fabric specifics |
| `docs/platforms/azure/` | Azure infrastructure patterns |
| `docs/templates/` | Documentation templates for projects |
| `terraform/modules/` | Infrastructure as Code modules |

## Platform Detection

Commands detect your platform from:
- `*.Notebook/` folders → Fabric
- `databricks.yml` → Databricks
- `terraform/*.tf` → Azure/AWS/GCP

## Key Principles

All platforms follow: Medallion Architecture, Data Governance, Data Quality, Security & Privacy.
See `docs/principles/` for details.

## Project Documentation

- **Generic patterns** → this repo's `docs/`
- **Project-specific** → project's `docs/` (catalog, sources, ADRs, runbooks)
- **Learnings** → generalized here, specified in projects
