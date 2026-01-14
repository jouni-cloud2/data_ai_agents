---
name: documentation-standards
description: Documentation standards and templates for data platforms.
---

# Documentation Standards Skill

## Documentation Types

### 1. Data Dictionary
Describes tables, columns, and their meanings.

### 2. Pipeline/Workflow Documentation
Describes ETL processes and their configurations.

### 3. Architecture Documentation
Describes system design and data flow.

### 4. Runbook
Operational guide for monitoring and troubleshooting.

### 5. ADR (Architectural Decision Record)
Documents key technical decisions.

## Data Dictionary Template

```markdown
# Data Dictionary: [Schema/Database Name]

## Overview
- **Platform**: [Fabric/Databricks]
- **Layer**: [Bronze/Silver/Gold]
- **Owner**: [Team/Person]
- **Last Updated**: [Date]

---

## Table: [table_name]

### Overview
- **Description**: [What this table contains]
- **Source**: [Where data comes from]
- **Update Frequency**: [Schedule]
- **Grain**: [One row per...]
- **Row Count**: [Approximate]

### Schema

| Column | Type | Nullable | Description | Example | PII |
|--------|------|----------|-------------|---------|-----|
| id | BIGINT | No | Primary key | 12345 | No |
| customer_name | STRING | No | Customer full name | John Doe | Yes |
| email_hash | STRING | No | SHA256 of email | abc123... | No |
| created_at | TIMESTAMP | No | Record creation time | 2024-01-15 10:30:00 | No |
| _ingested_at | TIMESTAMP | No | Ingestion timestamp | 2024-01-15 10:35:00 | No |

### Business Rules
1. `id` is auto-generated surrogate key
2. `email_hash` is SHA256 hash of lowercase email
3. Records are append-only in Bronze

### Data Quality
- Completeness: id, customer_name required (100%)
- Uniqueness: id must be unique
- Validity: email_hash must be 64 hex characters

### Lineage
- **Upstream**: `bronze_salesforce_account`
- **Downstream**: `gold_dim_customer`, `gold_fact_sales`

### SLA
- Freshness: Data within 24 hours
- Availability: 99.9%
```

## Pipeline Documentation Template

```markdown
# Pipeline: [pipeline_name]

## Overview
- **Platform**: [Fabric/Databricks]
- **Type**: [Pipeline/Workflow/DLT]
- **Purpose**: [Brief description]
- **Owner**: [Team/Person]
- **Created**: [Date]
- **Last Modified**: [Date]

## Schedule
- **Trigger**: [Cron expression or event]
- **Timezone**: [UTC/Local]
- **Dependencies**: [Upstream jobs]

## Architecture

```
[Source] --> [Bronze] --> [Silver] --> [Gold]
    |           |            |           |
 Copy Act   Notebook    Notebook    Notebook
```

## Activities/Tasks

### 1. [Activity Name]
- **Type**: [Copy/Notebook/SQL/etc.]
- **Description**: [What it does]
- **Input**: [Source tables/files]
- **Output**: [Target tables/files]
- **Duration**: [Typical runtime]

### 2. [Activity Name]
...

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| watermark | STRING | Yes | None | Last processed timestamp |
| batch_size | INT | No | 1000 | Records per batch |

## Error Handling
- **Retry Policy**: [X retries, Y seconds interval]
- **Timeout**: [Duration]
- **On Failure**: [Alert/Skip/Fail pipeline]

## Monitoring
- **Dashboard**: [Link]
- **Alerts**: [Configuration]
- **Logs**: [Location]

## Troubleshooting

### Issue: [Common Issue 1]
**Symptoms**: [What you see]
**Cause**: [Root cause]
**Solution**: [Steps to fix]

### Issue: [Common Issue 2]
...
```

## Architecture Documentation Template

```markdown
# Architecture: [System Name]

## Overview
[High-level description of the system]

## Architecture Diagram

```
                    +------------------+
                    |   Source Systems |
                    +--------+---------+
                             |
                    +--------v---------+
                    |     Ingestion    |
                    |   (Pipelines)    |
                    +--------+---------+
                             |
         +-------------------+-------------------+
         |                   |                   |
+--------v--------+ +--------v--------+ +--------v--------+
|     Bronze      | |     Silver      | |      Gold       |
|   (Raw Data)    | |  (Cleaned)      | |   (Business)    |
+-----------------+ +-----------------+ +-----------------+
                             |
                    +--------v---------+
                    |   Consumption    |
                    | (BI/ML/Reports)  |
                    +------------------+
```

## Components

### Data Sources
| Source | Type | Frequency | Volume |
|--------|------|-----------|--------|
| Salesforce | API | Daily | 100K records |
| SAP | DB | Hourly | 1M records |

### Storage
- **Platform**: [Fabric OneLake / Databricks Delta Lake]
- **Format**: Delta
- **Retention**: [Policy]

### Compute
- **Type**: [Serverless/Dedicated]
- **Configuration**: [Specs]

### Security
- **Authentication**: [Method]
- **Authorization**: [RBAC details]
- **Encryption**: [At rest/In transit]

## Data Flow

### Ingestion Flow
1. Source system triggers/schedule
2. Pipeline extracts data
3. Data lands in Bronze layer
4. Metadata added

### Transformation Flow
1. Read from Bronze
2. Apply transformations
3. Quality validation
4. Write to Silver/Gold

## Decisions

### ADR-001: [Decision Title]
- **Status**: Accepted
- **Context**: [Why]
- **Decision**: [What]
- **Consequences**: [Impact]
```

## Runbook Template

```markdown
# Runbook: [System/Pipeline Name]

## Overview
[Brief description of what this runbook covers]

## Contacts
| Role | Name | Contact |
|------|------|---------|
| Primary On-Call | [Name] | [Email/Phone] |
| Secondary On-Call | [Name] | [Email/Phone] |
| Escalation | [Name] | [Email/Phone] |

## Monitoring

### Dashboards
- [Dashboard Name]: [Link]

### Key Metrics
| Metric | Normal Range | Alert Threshold |
|--------|--------------|-----------------|
| Pipeline Duration | 10-30 min | > 60 min |
| Record Count | 90-110K | < 80K or > 120K |
| Error Rate | < 0.1% | > 1% |

### Alerts
| Alert | Severity | Action |
|-------|----------|--------|
| Pipeline Failed | Critical | [Link to procedure] |
| High Latency | Warning | [Link to procedure] |

## Common Issues

### Issue: Pipeline Timeout
**Symptoms**:
- Pipeline runs > 60 minutes
- Eventually fails with timeout error

**Diagnosis**:
1. Check source system availability
2. Review data volume
3. Check for resource contention

**Resolution**:
1. If source down: Wait for recovery, restart
2. If volume spike: Increase timeout, investigate cause
3. If resource issue: Scale compute

**Prevention**:
- Monitor source data volume
- Set appropriate timeout

### Issue: Data Quality Failure
**Symptoms**:
- Quality checks fail
- Records quarantined

**Diagnosis**:
1. Review quarantine records
2. Check source data
3. Identify pattern

**Resolution**:
1. If source issue: Contact source owner
2. If transformation bug: Fix and reprocess
3. If valid edge case: Update rules

## Recovery Procedures

### Full Reprocess
```bash
# 1. Clear target tables
DELETE FROM silver_table WHERE date >= 'YYYY-MM-DD';

# 2. Rerun pipeline with parameters
/pipelines/run --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```

### Partial Recovery
```bash
# 1. Identify failed records
SELECT * FROM quarantine WHERE date = 'YYYY-MM-DD';

# 2. Fix and reprocess specific records
/pipelines/reprocess --ids 123,456,789
```

## Maintenance

### Daily
- [ ] Check pipeline status
- [ ] Review error logs

### Weekly
- [ ] Review performance metrics
- [ ] Check storage usage

### Monthly
- [ ] Run vacuum on Delta tables
- [ ] Review and update documentation
```

## ADR Template

```markdown
# ADR-[NNN]: [Title]

**Date**: YYYY-MM-DD
**Status**: [Proposed | Accepted | Deprecated | Superseded]
**Deciders**: [Names]

## Context
[Describe the situation and why a decision is needed]

## Decision
[Clearly state the decision made]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Drawback 1]
- [Drawback 2]

### Neutral
- [Observation 1]

## Alternatives Considered

### Alternative 1: [Name]
- **Description**: [What it is]
- **Pros**: [Benefits]
- **Cons**: [Drawbacks]
- **Rejected Because**: [Reason]

### Alternative 2: [Name]
...

## References
- [Link to relevant documentation]
- [Link to discussions]
```

## Best Practices

- Auto-generate documentation from code where possible
- Keep documentation close to code
- Update documentation with every change
- Include examples and diagrams
- Use consistent formatting
- Review documentation regularly

## Anti-Patterns

- Don't write documentation after the fact
- Don't let documentation drift from reality
- Don't use jargon without definitions
- Don't skip diagrams for complex systems
