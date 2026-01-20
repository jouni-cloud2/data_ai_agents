# Data Platform Project - Team Knowledge

## Project Overview

AI-powered data platform development system with specialized agents and skills for Microsoft Fabric and Databricks. Automates the journey from user story to production-ready code.

## Supported Platforms

- **Primary**: Microsoft Fabric
- **Secondary**: Databricks
- **Shared**: Medallion architecture, SQL optimization, ETL patterns

## Available CLI Tools

The following CLI tools are available for agents to use:

| Tool | Purpose | Platform |
|------|---------|----------|
| `az` | Azure CLI for Fabric/Azure resource management | Fabric, Azure |
| `azcopy` | High-performance data transfer to/from Azure | Fabric, Azure |
| `jq` | JSON processing for API responses | All |
| `terraform` | Infrastructure as Code for Azure/Databricks | Both |
| `gh` | GitHub CLI for PR/issue management | Both |
| `databricks` | Databricks CLI for workspace operations | Databricks |

### Usage Examples

```bash
# Azure CLI - Fabric REST API
az rest --method GET --url "https://api.fabric.microsoft.com/v1/workspaces" | jq '.value[]'

# azcopy - Transfer to OneLake
azcopy copy "./data/*" "https://onelake.dfs.fabric.microsoft.com/workspace/lakehouse.Lakehouse/Files/" --recursive

# Terraform - Deploy infrastructure
terraform plan -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/dev.tfvars"

# GitHub CLI - Create PR
gh pr create --title "feat: add new source" --body "Description"

# Databricks CLI
databricks bundle deploy --target dev
```

## Quick Start

```bash
# Main workflow - takes a user story to PR-ready code
/develop-story "Add Salesforce as a source"
```

## Directory Structure

```
.claude/
├── agents/                    # Specialized AI agents
│   ├── requirements-analyst.md
│   ├── data-architect.md
│   ├── data-engineer-fabric.md
│   ├── data-engineer-databricks.md
│   ├── qa-engineer.md
│   ├── devops-engineer.md
│   ├── documentation-engineer.md
│   └── learning-agent.md
├── commands/                  # Workflow commands
│   └── develop-story.md
├── skills/                    # Reusable knowledge modules
│   ├── shared/               # Platform-agnostic skills
│   ├── fabric/               # Fabric-specific skills
│   └── databricks/           # Databricks-specific skills
└── config/                    # Configuration files
```

## Architectural Decisions

- OneLake for Fabric storage
- Unity Catalog for Databricks governance
- Medallion architecture: Bronze (raw) -> Silver (cleaned) -> Gold (modeled)
- PySpark for complex transformations
- SQL for simple transformations
- Delta Lake as default format

## Naming Conventions

### Tables
- Bronze: `bronze_{source}_{object}` (e.g., bronze_salesforce_account)
- Silver: `silver_{source}_{object}` (e.g., silver_salesforce_account)
- Gold: `gold_{mart}_{table}` (e.g., gold_sales_mart_dim_customer)

### Pipelines/Workflows
- Fabric: `pl_{action}_{source}_{frequency}` (e.g., pl_ingest_salesforce_daily)
- Databricks: `wf_{action}_{source}_{frequency}` (e.g., wf_ingest_salesforce_daily)

### Notebooks
- Format: `{verb}_{source}_{layer}.py` (e.g., transform_salesforce_bronze_to_silver.py)

## Common Mistakes to Avoid

[Auto-updated by Learning Agent]

### Requirements & Planning
1. DON'T accept "all fields" - ask for specific list
2. DON'T assume "incremental" is clear - ask for watermark column
3. ALWAYS clarify PII requirements upfront
4. ALWAYS ask which platform (Fabric vs Databricks)
5. ALWAYS ask which business domain (for Fabric workspace organization)

### Architecture & Design
1. DON'T mix Fabric and Databricks patterns
2. DO use platform-native approaches
3. ALWAYS plan for API rate limits
4. Fabric uses FOLDERS, Databricks uses SCHEMAS

### Implementation
1. DON'T place PII masking in Gold - do Bronze->Silver
2. DON'T forget metadata columns (_ingested_at, _source_file, _pipeline_run_id)
3. ALWAYS implement idempotency
4. ALWAYS add error handling with retry

### Testing
1. DON'T just test happy path
2. ALWAYS validate schema first
3. DO test with prod-like volumes

## Best Practices

[Auto-updated with proven patterns]

### Fabric-Specific
1. Use OneLake for all storage
2. Use Dataflow Gen2 for complex APIs
3. Partition large tables by date
4. Use managed identity for auth
5. Enable Fabric monitoring
6. Organize by domain: {Domain}_{Environment} workspaces

### Databricks-Specific
1. Use Unity Catalog always (catalog.schema.table)
2. Use DLT for production pipelines
3. Use Serverless compute
4. Enable auto-optimization on tables
5. Use Photon engine
6. Use expectations for data quality

### Shared
1. Use parameters in pipelines/workflows
2. Log execution metrics
3. Test with small dataset first
4. Z-order on filtered columns
5. Partition by year-month for large tables

## Recent Learnings

[Auto-updated by Learning Agent after each PR]

_No learnings recorded yet. Complete your first story to populate this section._

## Performance Optimization Patterns

[Learned from production]

- Z-ordering: 30-50% improvement on filtered columns
- Partition by year-month for >1GB tables
- Liquid clustering for high cardinality (Databricks)
- Optimize after major loads
- Use broadcast joins for small dimension tables

## Troubleshooting Guide

[Common issues and solutions]

### Pipeline Timeout
**Symptoms**: Fails after configured timeout
**Cause**: Large volume without partitioning
**Solution**: Add partition strategy, increase timeout
**Prevention**: Estimate volume in planning

### Schema Drift
**Symptoms**: Silver transform fails
**Cause**: Source changed schema
**Solution**: Update bronze and transform logic
**Prevention**: Schema validation in ingestion

### Rate Limiting
**Symptoms**: API calls fail with 429 errors
**Cause**: Exceeded API limits
**Solution**: Add batching and delays
**Prevention**: Check limits in planning, use backoff

### Data Quality Failures
**Symptoms**: Records quarantined or pipeline fails
**Cause**: Invalid source data
**Solution**: Review quarantine, fix source or update rules
**Prevention**: Validate early, document expectations

## Knowledge Base

- Fabric Docs: https://learn.microsoft.com/fabric
- Databricks Docs: https://docs.databricks.com
- Delta Lake: https://delta.io
