# Data Governance

Principles for data classification, ownership, and stewardship.

## Data Classification

### Classification Levels

| Level | Description | Examples | Access |
|-------|-------------|----------|--------|
| **Public** | No business impact if disclosed | Published reports, public APIs | Anyone |
| **Internal** | Business impact if disclosed externally | Internal metrics, aggregated data | All employees |
| **Confidential** | Significant impact if disclosed | Customer data, PII, contracts | Need-to-know |
| **Restricted** | Severe impact if disclosed | Credentials, financial data, health data | Specific roles only |

### Classification by Layer

| Layer | Typical Classification | Rationale |
|-------|------------------------|-----------|
| Bronze | Confidential/Restricted | Contains raw PII |
| Silver | Internal/Confidential | PII hashed, but still sensitive |
| Gold | Internal | Aggregated, business-ready |

### Classification Decision Tree

```
Is the data publicly available?
├── Yes → PUBLIC
└── No → Is it PII or contains personal data?
    ├── Yes → Is it sensitive PII (health, financial, identity)?
    │   ├── Yes → RESTRICTED
    │   └── No → CONFIDENTIAL
    └── No → Is disclosure harmful to business?
        ├── Yes → CONFIDENTIAL
        └── No → INTERNAL
```

## Data Ownership

### Roles and Responsibilities

| Role | Responsibilities | Example |
|------|-----------------|---------|
| **Data Owner** | Business accountability, classification decisions, access approval | Business unit head |
| **Data Steward** | Quality rules, metadata, issue resolution | Domain expert |
| **Technical Owner** | Pipeline implementation, performance, monitoring | Data engineer |
| **Data Consumer** | Appropriate use, reporting issues | Analyst, application |

### Ownership Matrix

Document ownership in data catalogs:

```yaml
# Example catalog entry
table: gold_dim_customer
owner: Sales Operations
steward: CRM Team Lead
technical_owner: Data Platform Team
classification: confidential
```

## Data Stewardship

### Stewardship Activities

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Data quality review | Weekly | Steward |
| Metadata updates | As needed | Steward |
| Access reviews | Quarterly | Owner + Steward |
| Classification review | Annual | Owner |
| Lineage validation | After changes | Technical Owner |

### Stewardship Workflow

```
Issue Detected → Steward Notified → Root Cause Analysis
                                          ↓
                          ┌───────────────┴───────────────┐
                          ↓                               ↓
                   Data Quality Issue              Metadata Issue
                          ↓                               ↓
              Fix in pipeline/source            Update catalog
                          ↓                               ↓
                   Validate fix                  Notify consumers
                          ↓                               ↓
                   Document lesson              Update documentation
```

## Data Retention

### Retention Principles

1. **Minimum necessary**: Keep only what's needed
2. **Documented rationale**: Why this retention period?
3. **Automated enforcement**: Lifecycle policies, not manual deletion
4. **Legal compliance**: Regulatory requirements override defaults

### Retention Guidelines

| Data Type | Default Retention | Rationale |
|-----------|-------------------|-----------|
| Bronze (audit) | 7 years | Regulatory compliance |
| Silver (operational) | 3 years | Operational needs |
| Gold (analytical) | 5 years | Business analysis |
| Logs/telemetry | 90 days | Troubleshooting |
| Temporary/staging | 7 days | Processing only |

### Retention Implementation

```python
# Delta table lifecycle (Databricks/Fabric)
spark.sql("""
    ALTER TABLE bronze_transactions
    SET TBLPROPERTIES (
        'delta.deletedFileRetentionDuration' = 'interval 30 days',
        'delta.logRetentionDuration' = 'interval 90 days'
    )
""")

# VACUUM to enforce retention
spark.sql("VACUUM bronze_transactions RETAIN 30 DAYS")
```

## Data Lineage

### Lineage Requirements

Track data flow from source to consumption:

| Element | Required Information |
|---------|---------------------|
| **Source** | System, table/API, field |
| **Transformation** | Logic applied, code reference |
| **Target** | System, table, field |
| **Timestamp** | When transformation occurred |

### Lineage Documentation

Include in catalog entries:

```markdown
## Lineage

**Upstream:**
- `bronze_hubspot_companies` (HubSpot CRM API)
- `bronze_salesforce_accounts` (Salesforce API)

**Transformation:**
- Deduplicated by email
- Company names standardized (uppercase, trimmed)
- Classification enriched from manual mapping

**Downstream:**
- `gold_dim_customer` (dimension table)
- `gold_fact_sales` (fact table via FK)
- Power BI Customer Dashboard
```

## Access Control

### Access Principles

1. **Least privilege**: Minimum access for the task
2. **Role-based**: Groups, not individuals
3. **Time-limited**: Temporary access when possible
4. **Audited**: All access logged

### Access Patterns by Layer

| Layer | Read Access | Write Access |
|-------|-------------|--------------|
| Bronze | Data Engineering | Ingestion pipelines only |
| Silver | Data Engineering, Analysts | Transformation pipelines only |
| Gold | All authorized users | Modeling pipelines only |

### Row/Column-Level Security

For sensitive data in shared layers:

```sql
-- Column-level security (Databricks Unity Catalog)
GRANT SELECT ON TABLE gold_dim_customer
    (customer_id, company_name, industry)  -- Exclude PII columns
TO analysts;

-- Row-level security
CREATE VIEW gold_dim_customer_filtered AS
SELECT * FROM gold_dim_customer
WHERE region = current_user_region();
```

## Compliance Frameworks

### Common Requirements

| Framework | Key Data Requirements |
|-----------|----------------------|
| **GDPR** | Consent, right to erasure, data minimization |
| **CCPA** | Disclosure, opt-out, data portability |
| **SOC 2** | Access controls, monitoring, incident response |
| **ISO 27001** | Classification, access control, audit trails |
| **HIPAA** | PHI protection, access logging, encryption |

### Implementation Checklist

- [ ] Data classified at ingestion
- [ ] Ownership documented in catalog
- [ ] Retention policies implemented
- [ ] Access controls configured
- [ ] Audit logging enabled
- [ ] Lineage documented
- [ ] Stewardship process defined

## References

- [DAMA DMBOK](https://www.dama.org/cpages/body-of-knowledge)
- [Azure Data Governance](https://learn.microsoft.com/azure/cloud-adoption-framework/scenarios/data-management/govern)
- [AWS Data Governance](https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/data-governance.html)
- [Databricks Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)

---

*Last Updated: 2026-02-09*
