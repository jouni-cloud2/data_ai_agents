# Security & Privacy

Principles for protecting sensitive data in data platforms.

## PII Handling

### What is PII?

Personally Identifiable Information (PII) includes:

| Category | Examples | Sensitivity |
|----------|----------|-------------|
| **Direct identifiers** | Name, SSN, email, phone | High |
| **Quasi-identifiers** | Birthdate, ZIP code, job title | Medium (can identify when combined) |
| **Sensitive attributes** | Salary, health data, religion | High |
| **Behavioral data** | Browsing history, purchases | Medium |

### PII Treatment by Layer

| Layer | PII Treatment | Rationale |
|-------|---------------|-----------|
| **Bronze** | Raw PII retained | Audit trail, recovery |
| **Silver** | PII hashed or masked | Enable joins without exposure |
| **Gold** | No raw PII | Business consumption |

### Hashing Strategy

**Recommended: Salted SHA-256 hashing**

```python
from pyspark.sql.functions import sha2, concat, lit, col

# Salt stored in Key Vault (never in code)
SALT = spark.conf.get("spark.secret.pii_salt")

# Hash PII fields in Silver transformation
df = df.withColumn("email_hash", sha2(concat(col("email"), lit(SALT)), 256))
df = df.withColumn("phone_hash", sha2(concat(col("phone"), lit(SALT)), 256))

# Drop original PII
df = df.drop("email", "phone")
```

**Why salted hashing?**
- Irreversible (cannot recover original)
- Deterministic (same input = same hash, enables joins)
- Salt prevents rainbow table attacks
- Simple to implement

**Hash Properties:**
| Property | Value |
|----------|-------|
| Algorithm | SHA-256 |
| Output length | 64 characters (hex) |
| Collision resistance | Extremely low probability |

### Masking Patterns

For cases where hashing isn't suitable:

| Pattern | Original | Masked | Use Case |
|---------|----------|--------|----------|
| **Partial** | john.doe@email.com | j***@e***.com | Display to users |
| **Redaction** | 555-123-4567 | [REDACTED] | Logs, exports |
| **Tokenization** | 4532-1234-5678-9012 | tok_abc123 | Payment data |
| **Generalization** | Age: 34 | Age group: 30-40 | Analytics |

### Implementation Example

```python
from pyspark.sql.functions import when, regexp_replace, col

def mask_email(column):
    """Partial masking for emails: j***@e***.com"""
    return regexp_replace(
        column,
        r"^(.).*@(.).*\.(.*)$",
        r"$1***@$2***.$3"
    )

def mask_phone(column):
    """Show last 4 digits only: ***-***-1234"""
    return regexp_replace(
        column,
        r"^\d{3}-\d{3}-(\d{4})$",
        r"***-***-$1"
    )
```

## Access Control

### Least Privilege Principle

Grant minimum access required for the task:

```
┌─────────────────────────────────────────────────────────────┐
│                    ACCESS CONTROL MODEL                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Bronze Layer                                               │
│  └── Data Engineering Team only                            │
│      └── Read/Write for ingestion pipelines                │
│                                                             │
│  Silver Layer                                               │
│  └── Data Engineering Team                                 │
│      └── Read/Write for transformations                    │
│  └── Data Analysts                                         │
│      └── Read only (hashed PII)                           │
│                                                             │
│  Gold Layer                                                 │
│  └── All authorized business users                         │
│      └── Read only (no raw PII)                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Role-Based Access Control (RBAC)

| Role | Bronze | Silver | Gold | Semantic Models |
|------|--------|--------|------|-----------------|
| **Data Engineer** | Read/Write | Read/Write | Read/Write | None |
| **Data Analyst** | None | Read | Read | Read |
| **Business User** | None | None | Read | Read |
| **Data Steward** | Read | Read/Write | Read/Write | Read |

### Column-Level Security

For sensitive columns in shared tables:

```sql
-- Databricks Unity Catalog
GRANT SELECT ON TABLE gold_dim_customer
    (customer_id, name, industry)  -- Exclude sensitive columns
TO GROUP analysts;

-- Snowflake
CREATE MASKING POLICY salary_mask AS (val NUMBER) RETURNS NUMBER ->
    CASE WHEN current_role() IN ('HR', 'FINANCE') THEN val
         ELSE NULL
    END;

ALTER TABLE employees MODIFY COLUMN salary SET MASKING POLICY salary_mask;
```

### Row-Level Security

For multi-tenant or region-restricted data:

```sql
-- Dynamic row filtering
CREATE VIEW gold_orders_filtered AS
SELECT * FROM gold_orders
WHERE region = current_user_region()
   OR current_role() = 'ADMIN';
```

## Secret Management

### Principles

1. **Never in code**: No secrets in source control
2. **Centralized storage**: Use Key Vault / Secrets Manager
3. **Rotation ready**: Design for secret rotation
4. **Audit access**: Log all secret retrievals

### Platform Secret Storage

| Platform | Secret Store | Reference |
|----------|--------------|-----------|
| **Azure/Fabric** | Azure Key Vault | [Key Vault Docs](https://learn.microsoft.com/azure/key-vault/) |
| **AWS** | AWS Secrets Manager | [Secrets Manager Docs](https://docs.aws.amazon.com/secretsmanager/) |
| **GCP** | Secret Manager | [Secret Manager Docs](https://cloud.google.com/secret-manager) |
| **Databricks** | Secret Scopes | [Databricks Secrets](https://docs.databricks.com/en/security/secrets/index.html) |

### Usage Example

```python
# Azure Key Vault (Fabric)
from notebookutils import mssparkutils
api_key = mssparkutils.credentials.getSecret("keyvault-name", "api-key-name")

# Databricks
api_key = dbutils.secrets.get(scope="my-scope", key="api-key")

# AWS (Glue/EMR)
import boto3
client = boto3.client('secretsmanager')
api_key = client.get_secret_value(SecretId='my-api-key')['SecretString']
```

## Encryption

### Encryption at Rest

| Platform | Default Encryption | Customer-Managed Keys |
|----------|-------------------|----------------------|
| **Fabric/OneLake** | Microsoft-managed | Supported |
| **Databricks** | Platform-managed | Supported via Unity Catalog |
| **Snowflake** | Automatic | Tri-Secret Secure |
| **S3/ADLS/GCS** | Default encryption | CMK supported |

### Encryption in Transit

- All connections must use TLS 1.2+
- Verify certificates
- Use private endpoints where available

## Audit Logging

### What to Log

| Event | Details to Capture |
|-------|-------------------|
| **Data access** | Who, what table, when, query |
| **Data modification** | Who, what changed, before/after |
| **Failed access** | Who, what attempted, why denied |
| **Schema changes** | Who, what DDL, when |
| **Export/download** | Who, what data, destination |

### Log Retention

| Log Type | Retention | Rationale |
|----------|-----------|-----------|
| Security events | 2 years | Compliance requirement |
| Access logs | 1 year | Audit support |
| Query logs | 90 days | Troubleshooting |

## Compliance Requirements

### GDPR Considerations

| Requirement | Implementation |
|-------------|----------------|
| **Right to access** | Ability to export user's data |
| **Right to erasure** | Soft delete with propagation |
| **Data minimization** | Only collect necessary data |
| **Purpose limitation** | Document and enforce data use |
| **Consent** | Track consent with timestamps |

### Deletion Pattern

```python
# Soft delete for GDPR compliance
def delete_user_data(user_id: str):
    # Mark as deleted (soft delete)
    spark.sql(f"""
        UPDATE silver_users
        SET is_deleted = true, deleted_at = current_timestamp()
        WHERE user_id = '{user_id}'
    """)

    # Anonymize in Gold (hard delete not always possible)
    spark.sql(f"""
        UPDATE gold_dim_customer
        SET name = '[DELETED]', email_hash = 'DELETED'
        WHERE source_user_id = '{user_id}'
    """)

    # Log deletion for audit
    log_deletion_event(user_id)
```

## Security Checklist

Before deploying a data pipeline:

- [ ] PII fields identified and documented
- [ ] Hashing/masking implemented in Silver
- [ ] Access controls configured
- [ ] Secrets stored in vault (not code)
- [ ] Encryption at rest enabled
- [ ] Audit logging enabled
- [ ] GDPR deletion path defined (if applicable)
- [ ] Security review completed

## References

- [OWASP Data Security](https://owasp.org/www-project-data-security/)
- [NIST Privacy Framework](https://www.nist.gov/privacy-framework)
- [Azure Security Best Practices](https://learn.microsoft.com/azure/security/fundamentals/best-practices-and-patterns)
- [AWS Security Best Practices](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)

---

*Last Updated: 2026-02-09*
