---
name: requirements-gathering
description: Systematic framework for gathering requirements through questions.
---

# Requirements Gathering Skill

## Critical First Question
**ALWAYS ASK:** "Which platform: Microsoft Fabric or Databricks?"

## Question Categories

### Platform (CRITICAL)
- Which platform for implementation?

### Source System
- Which source? (Salesforce, SAP, Snowflake, Files, API, DB)
- Which objects/tables/endpoints?
- Which fields? (Specific list, never "all")
- Data volume and growth?
- Update frequency?

### Data Requirements
- Historical data? How far back?
- Full or incremental?
- If incremental: watermark column?
- Expected latency?

### Quality & Compliance
- PII/sensitive data?
- Quality checks required?
- SLA requirements?
- Compliance needs?
- Retention period?

## Best Practices

- Always get specific field lists
- Always clarify incremental strategy
- Always identify PII early
- Always determine platform first

## Anti-Patterns

- Never accept vague requirements
- Never proceed without watermark
- Never skip compliance questions

## Question Templates

### For API Sources
```
1. What is the API endpoint?
2. What authentication method? (OAuth, API Key, etc.)
3. Are there rate limits? What are they?
4. What is the pagination strategy?
5. What fields should we extract? (List specifically)
6. Is there a last-modified field for incremental?
```

### For Database Sources
```
1. What database type? (SQL Server, PostgreSQL, Oracle, etc.)
2. Which tables/views?
3. What columns? (List specifically)
4. What is the primary key?
5. Is there a timestamp column for incremental?
6. Expected row count and growth rate?
```

### For File Sources
```
1. What file format? (CSV, JSON, Parquet, etc.)
2. Where are files located? (S3, ADLS, local, etc.)
3. What is the file naming pattern?
4. What is the delivery schedule?
5. What columns? (List specifically)
6. Is there a header row?
7. What is the delimiter? (for CSV)
```

## Output Format

### Requirements Document Structure
```markdown
# Requirements: [Story Title]

## Story
[Original user story]

## Target Platform
**Platform**: [Fabric/Databricks]
**Workspace/Catalog**: [Name]

## Source System
- **System**: [Name]
- **Type**: [API/Database/Files]
- **Connection**: [Details]

## Objects and Fields
### [Object 1]
| Field | Type | Description | Required |
|-------|------|-------------|----------|
| field1 | STRING | desc | Yes |

## Load Strategy
- **Type**: [Full/Incremental]
- **Watermark**: [Column name]
- **Frequency**: [Schedule]

## Data Quality
- **Validations**: [List]
- **SLA**: [Requirements]

## Compliance
- **PII Fields**: [List]
- **Retention**: [Period]
- **Regulations**: [GDPR/CCPA/etc.]

## Acceptance Criteria
1. [Criterion 1]
2. [Criterion 2]
```
