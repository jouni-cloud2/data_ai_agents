# {Table Name}

## Overview

| Field | Value |
|-------|-------|
| **Name** | `{lakehouse}.{table_name}` |
| **Domain** | {Domain name} |
| **Layer** | {Bronze / Silver / Gold} |
| **Description** | {One-line description} |
| **Purpose** | {Business value delivered} |

## Ownership

| Role | Name/Team |
|------|-----------|
| **Business Owner** | {Person or team} |
| **Data Steward** | {Person or team} |
| **Technical Owner** | {Engineering team} |

## Data Governance

| Field | Value |
|-------|-------|
| **Classification** | {Public / Internal / Confidential / Restricted} |
| **Retention** | {Duration, e.g., "7 years"} |
| **Retention Reason** | {Why this duration} |
| **PII Fields** | {List of fields or "None"} |
| **PII Treatment** | {Hashed / Masked / N/A} |

## Schema

| Column | Type | Description | Source |
|--------|------|-------------|--------|
| `{column_name}` | {data_type} | {description} | {source field or transformation} |

## Lineage

### Upstream
- `{source_table_1}` - {description}
- `{source_table_2}` - {description}

### Downstream
- `{consuming_table_1}` - {description}
- Power BI: `{report_name}`

## Quality Rules

| Rule | Dimension | Threshold | Severity |
|------|-----------|-----------|----------|
| {rule_name} | {Completeness/Validity/...} | {expected value} | {Error/Warning} |

## Refresh Schedule

| Aspect | Value |
|--------|-------|
| **Frequency** | {Daily / Hourly / Real-time} |
| **Schedule** | {Time in UTC} |
| **Pipeline** | `{pipeline_name}` |

## Notes

{Anything non-obvious for future engineers}

---

*Created: {YYYY-MM-DD}*
*Last Updated: {YYYY-MM-DD}*
