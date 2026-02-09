# Environment Separation

Principles for separating development, test, and production environments for compliance.

## Compliance Requirements

### Regulatory Drivers

| Framework | Requirement | Implementation |
|-----------|-------------|----------------|
| **ISO 27001** | A.12.1.4: Separation of environments | Dev/Test isolated from Prod |
| **SOC 2** | CC6.7: System changes | Controlled promotion between environments |
| **GDPR** | Art. 25: Data protection by design | No production PII in dev/test |
| **HIPAA** | 164.312: Access controls | PHI restricted to production |

### Core Principle

> **Production data with PII must never exist in non-production environments.**

## Environment Model

### Three-Environment Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                     ENVIRONMENT MODEL                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐              │
│  │   DEV    │ ───► │   TEST   │ ───► │   PROD   │              │
│  └──────────┘      └──────────┘      └──────────┘              │
│       │                 │                 │                     │
│       ▼                 ▼                 ▼                     │
│   Synthetic         Masked           Production                │
│   or Test           Production        Data                     │
│   Data              Data                                        │
│                                                                 │
│  Full access       Restricted        Very restricted           │
│  for devs          access            access                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Environment Purposes

| Environment | Purpose | Data | Access |
|-------------|---------|------|--------|
| **Dev** | Development, experimentation | Synthetic/test only | Developers (full) |
| **Test** | Integration testing, UAT | Masked production | QA, limited devs |
| **Prod** | Production workloads | Real production data | Operations only |

## Data Strategies by Environment

### Strategy Comparison

| Strategy | Compliance | Realism | Effort | Recommended For |
|----------|------------|---------|--------|-----------------|
| **Separate sources** | High | Low | Low | APIs with test environments |
| **Synthetic data** | High | Medium | Medium | Schema-stable systems |
| **Masked export** | High | High | High | Complex data relationships |

### Strategy 1: Separate Data Sources

Use different API endpoints/databases per environment:

```hcl
# Terraform environment routing
variable "environment" {
  type = string
}

locals {
  api_endpoints = {
    dev  = "https://sandbox.api.example.com"
    test = "https://staging.api.example.com"
    prod = "https://api.example.com"
  }

  api_endpoint = local.api_endpoints[var.environment]
}
```

**Pros:** Complete isolation, simple compliance
**Cons:** Test data may not reflect production patterns

### Strategy 2: Synthetic Data Generation

Generate fake data matching production schemas:

```python
from faker import Faker
import pandas as pd

fake = Faker()

def generate_synthetic_customers(count: int) -> pd.DataFrame:
    """Generate synthetic customer data matching production schema."""
    return pd.DataFrame({
        "customer_id": [fake.uuid4() for _ in range(count)],
        "name": [fake.company() for _ in range(count)],
        "email": [fake.company_email() for _ in range(count)],
        "phone": [fake.phone_number() for _ in range(count)],
        "industry": [fake.random_element(["Tech", "Finance", "Healthcare"]) for _ in range(count)],
        "created_at": [fake.date_time_this_year() for _ in range(count)],
    })

# Match production volume distributions
customers = generate_synthetic_customers(10000)
```

**Pros:** Zero production data exposure, scalable
**Cons:** May miss edge cases from real data

### Strategy 3: Masked Production Export

Export production data with PII masked:

```python
def export_masked_data(source_table: str, target_environment: str):
    """Export masked production data to non-prod environment."""

    # Read from production Silver (already partially cleaned)
    df = spark.table(f"prod.{source_table}")

    # Apply additional masking for non-prod
    df = df.withColumn("email", hash_column("email"))
    df = df.withColumn("phone", lit("000-000-0000"))
    df = df.withColumn("name", anonymize_name("name"))

    # Randomize amounts (preserve distribution)
    df = df.withColumn("amount", col("amount") * (rand() * 0.4 + 0.8))

    # Write to target environment
    df.write.format("delta").mode("overwrite").saveAsTable(
        f"{target_environment}.{source_table}"
    )
```

**Pros:** Real data patterns, relationships preserved
**Cons:** Requires export pipeline maintenance

## Implementation Pattern

### Environment Configuration

```yaml
# config/environments.yaml
environments:
  dev:
    data_source: synthetic
    access_level: full
    capacity: small
    retention_days: 7

  test:
    data_source: masked_export
    access_level: restricted
    capacity: medium
    retention_days: 30

  prod:
    data_source: production
    access_level: very_restricted
    capacity: production
    retention_days: regulatory
```

### Pipeline Environment Awareness

```python
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

def get_data_source():
    """Return appropriate data source for current environment."""
    if ENVIRONMENT == "prod":
        return "production_api"
    elif ENVIRONMENT == "test":
        return "masked_export"
    else:
        return "synthetic"

def get_connection_config():
    """Return environment-specific connection configuration."""
    configs = {
        "dev": {
            "api_base_url": "https://sandbox.api.example.com",
            "key_vault": "kv-dataplatform-dev",
            "lakehouse": "lh_domain_dev"
        },
        "test": {
            "api_base_url": "https://staging.api.example.com",
            "key_vault": "kv-dataplatform-test",
            "lakehouse": "lh_domain_test"
        },
        "prod": {
            "api_base_url": "https://api.example.com",
            "key_vault": "kv-dataplatform-prod",
            "lakehouse": "lh_domain_prod"
        }
    }
    return configs[ENVIRONMENT]
```

## Access Controls by Environment

### Role Mapping

| Role | Dev | Test | Prod |
|------|-----|------|------|
| **Developer** | Read/Write | Read | None |
| **Tester/QA** | Read | Read/Write | None |
| **Data Engineer** | Read/Write | Read/Write | Read |
| **Operations** | Read | Read | Read/Write |
| **Business User** | None | Read | Read |

### Network Isolation

```
┌─────────────────────────────────────────────────────────────────┐
│                    NETWORK SEGMENTATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Dev Network              Test Network          Prod Network    │
│  ┌──────────────┐        ┌──────────────┐      ┌──────────────┐│
│  │ Dev resources│        │Test resources│      │Prod resources││
│  │              │        │              │      │              ││
│  │ Open access  │   ──►  │ VPN required │ ──►  │ PIM/JIT only ││
│  │ from corp    │        │              │      │              ││
│  └──────────────┘        └──────────────┘      └──────────────┘│
│                                                                 │
│       ❌ No direct access from Dev to Prod                     │
│       ❌ No data flow from Prod to Dev                         │
│       ✅ Code promotion: Dev → Test → Prod                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Compliance Checklist

### Environment Setup

- [ ] Each environment has isolated resources
- [ ] No production credentials in non-prod
- [ ] Network segmentation in place
- [ ] Access controls configured per environment

### Data Handling

- [ ] Dev environment uses synthetic/test data only
- [ ] Test environment uses masked data (if production-based)
- [ ] No raw PII exists outside production
- [ ] Data masking/anonymization validated

### Access Control

- [ ] Developers cannot access production directly
- [ ] Production changes require approval
- [ ] Access logged and auditable
- [ ] Regular access reviews scheduled

### Monitoring

- [ ] Cross-environment data flows monitored
- [ ] Alerts for unexpected production access
- [ ] Compliance audit trail maintained

## Migration Path

### From Shared Environment to Separated

1. **Inventory** current data and access patterns
2. **Classify** data by sensitivity
3. **Design** environment-specific architectures
4. **Implement** data generation/masking for non-prod
5. **Migrate** to separated environments
6. **Validate** no production data in non-prod
7. **Monitor** ongoing compliance

## Platform-Specific Guidance

| Platform | Environment Separation | Reference |
|----------|----------------------|-----------|
| **Fabric** | Separate workspaces per environment | [Fabric Deployment](../platforms/fabric/) |
| **Databricks** | Separate workspaces or catalogs | [Unity Catalog Isolation](https://docs.databricks.com/en/data-governance/unity-catalog/manage-external-locations.html) |
| **Snowflake** | Separate accounts or databases | [Snowflake Environments](https://docs.snowflake.com/en/user-guide/organizations-manage-accounts) |
| **Azure** | Separate subscriptions/resource groups | [Azure Landing Zones](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/) |

## References

- ISO 27001:2022 Annex A.12.1.4 (Separation of development, testing and operational environments)
- GDPR Article 25 (Data protection by design and by default)
- [Azure Security Best Practices](https://learn.microsoft.com/azure/security/fundamentals/best-practices-and-patterns)
- [AWS Environment Isolation](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/protecting-networks.html)

---

*Last Updated: 2026-02-09*
