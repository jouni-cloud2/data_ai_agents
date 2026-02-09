# Well-Architected Framework for Data Platforms

Apply cloud provider Well-Architected Framework principles to data platform design.

## Framework References

| Provider | Framework | Data-Specific Guidance |
|----------|-----------|------------------------|
| **AWS** | [AWS Well-Architected](https://aws.amazon.com/architecture/well-architected/) | [Analytics Lens](https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/analytics-lens.html) |
| **Azure** | [Azure Well-Architected](https://learn.microsoft.com/azure/well-architected/) | [Data Platform Workloads](https://learn.microsoft.com/azure/well-architected/service-guides/azure-databricks) |
| **GCP** | [Google Cloud Architecture Framework](https://cloud.google.com/architecture/framework) | [Data Analytics](https://cloud.google.com/architecture/framework/system-design/data-analytics) |

## Core Pillars Applied to Data Platforms

### 1. Operational Excellence

**Principle**: Automate operations, monitor proactively, learn from failures.

**Data Platform Application:**
- Infrastructure as Code for all data resources
- Automated data quality monitoring
- Pipeline observability and alerting
- Runbooks for common failure scenarios
- Post-incident reviews for data issues

**Key Metrics:**
- Pipeline success rate (target: >99%)
- Mean time to detect data issues
- Mean time to resolve data issues

### 2. Security

**Principle**: Protect data, systems, and assets through defense in depth.

**Data Platform Application:**
- Data classification at ingestion (see [Data Governance](data-governance.md))
- Encryption at rest and in transit
- Least-privilege access control
- PII handling (see [Security & Privacy](security-privacy.md))
- Audit logging for data access
- Secret management (Key Vault, Secrets Manager)

**Key Controls:**
- No credentials in code
- Managed identities where possible
- Row/column-level security for sensitive data

### 3. Reliability

**Principle**: Recover from failures and meet demand.

**Data Platform Application:**
- Idempotent data pipelines (rerunnable without side effects)
- Checkpoint and recovery mechanisms
- Data backup and retention policies
- Schema evolution handling
- Graceful degradation on source failures

**Key Patterns:**
- Delta/Iceberg tables for ACID transactions
- Watermark-based incremental loading
- Dead-letter queues for failed records

### 4. Performance Efficiency

**Principle**: Use resources efficiently to meet requirements.

**Data Platform Application:**
- Partition strategies aligned with query patterns
- Appropriate file formats (Parquet, Delta)
- Query optimization (predicate pushdown, Z-ordering)
- Right-sized compute (auto-scaling where available)
- Caching strategies for hot data

**Key Considerations:**
- Partition by date for time-series data
- Cluster/Z-order by common filter columns
- Compact small files regularly

### 5. Cost Optimization

**Principle**: Avoid unnecessary costs, understand spending.

**Data Platform Application:**
- Choose appropriate storage tiers (hot/cool/archive)
- Serverless/consumption-based where suitable
- Data lifecycle policies (retention, archival)
- Monitor and alert on cost anomalies
- Reserved capacity for predictable workloads

**Key Practices:**
- Tag resources for cost allocation
- Review unused resources regularly
- Optimize expensive queries

### 6. Sustainability (Azure/AWS)

**Principle**: Minimize environmental impact.

**Data Platform Application:**
- Efficient data formats reduce storage and compute
- Right-sized resources avoid waste
- Batch processing during low-carbon periods (where available)
- Data retention policies reduce storage footprint

## Platform-Specific Guidance

| Platform | Well-Architected Resources |
|----------|---------------------------|
| **Fabric** | [Fabric Well-Architected](https://learn.microsoft.com/fabric/well-architected/) |
| **Databricks** | [Databricks Best Practices](https://docs.databricks.com/en/lakehouse-architecture/index.html) |
| **Snowflake** | [Snowflake Best Practices](https://docs.snowflake.com/en/user-guide/performance-optimization) |
| **Synapse** | [Synapse Best Practices](https://learn.microsoft.com/azure/synapse-analytics/guidance/implementation-success-overview) |
| **Redshift** | [Redshift Best Practices](https://docs.aws.amazon.com/redshift/latest/dg/best-practices.html) |
| **BigQuery** | [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices-performance-overview) |

## Review Checklist

Before deploying a data platform component, verify:

- [ ] **Operational**: Is it monitored? Are runbooks ready?
- [ ] **Secure**: Is data classified? Are secrets managed?
- [ ] **Reliable**: Is it idempotent? Can it recover?
- [ ] **Performant**: Are partitions optimal? Queries efficient?
- [ ] **Cost-effective**: Is sizing appropriate? Lifecycle policies set?

---

*Last Updated: 2026-02-09*
