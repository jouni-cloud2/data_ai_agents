# ADR-001: Agileday Employee Data Architecture

**Status**: Proposed
**Date**: 2026-01-20
**Decision Makers**: Data Architect, Requirements Analyst
**Stakeholders**: HR Analytics Team, Data Engineering

## Context

We need to ingest employee data from Agileday workforce management system into our data platform. The previous implementation used Google Cloud Functions and GCS buckets for raw storage only. This implementation requires a complete data pipeline with proper governance, PII handling, and analytics-ready outputs.

## Decision Drivers

1. **Platform Standardization**: Migrate from GCP to Microsoft Fabric
2. **Data Governance**: Implement proper PII masking and access controls
3. **Analytics Requirements**: Create analytics-ready dimensional model
4. **Compliance**: GDPR-compliant data handling
5. **Maintainability**: Standard medallion architecture pattern
6. **Historical Tracking**: Track employee changes over time (SCD Type 2)

## Considered Options

### Option 1: Direct Bronze → Gold (Minimal Layers)
**Description**: Ingest to Bronze, transform directly to Gold dimension

**Pros**:
- Simpler pipeline
- Fewer storage costs
- Faster initial development

**Cons**:
- PII remains in Bronze, accessible to too many users
- No intermediate cleaned layer for data quality checks
- Mixing raw and business logic in single transformation
- Hard to debug and maintain

**Decision**: ❌ Rejected

### Option 2: Full Medallion (Bronze → Silver → Gold) - SELECTED
**Description**: Three-layer architecture with clear separation of concerns

**Pros**:
- Clear separation: raw (Bronze), cleaned (Silver), modeled (Gold)
- PII masked at Silver layer, proper access controls
- Intermediate layer for data quality validation
- Follows company standard pattern
- Easier to debug and maintain
- Reusable Silver layer for multiple Gold models

**Cons**:
- More complex pipeline
- Higher storage costs (minimal for employee data volume)
- Longer development time

**Decision**: ✅ **SELECTED**

**Rationale**: The benefits of proper governance, maintainability, and compliance outweigh the minimal additional complexity. Employee data volume is small enough that storage costs are negligible.

### Option 3: Real-time Streaming
**Description**: Stream changes from Agileday API in real-time

**Pros**:
- Near real-time data availability
- Capture changes as they happen

**Cons**:
- Agileday API doesn't support webhooks/streaming
- Would require constant polling (API rate limits)
- Over-engineered for daily HR analytics needs
- Higher costs and complexity

**Decision**: ❌ Rejected

## Architectural Decisions

### 1. Platform: Microsoft Fabric
**Decision**: Use Microsoft Fabric with OneLake storage
**Rationale**:
- Company standard platform for data
- Native integration with Azure services
- Built-in governance features
- Cost-effective for this scale

**Alternatives Considered**:
- Databricks: More expensive, overkill for this use case
- Azure Data Factory only: Missing lakehouse and query capabilities

### 2. Load Strategy: Full Load Daily
**Decision**: Daily full snapshot load at 2:00 AM UTC
**Rationale**:
- API doesn't provide incremental endpoints
- Employee data changes infrequently
- Small data volume (< 10K records = < 10 MB)
- Simpler implementation and debugging
- Hash comparison enables SCD Type 2 tracking

**Alternatives Considered**:
- Incremental: Not supported by API
- Real-time: Over-engineered for use case
- Weekly: Too infrequent for active HR operations

### 3. Storage Format: Delta Lake
**Decision**: Use Delta Lake format for all layers
**Rationale**:
- ACID transactions
- Time travel capabilities
- Schema evolution support
- Industry standard
- Native Fabric support

**Alternatives Considered**:
- Parquet: No ACID, harder to manage updates
- CSV: No schema enforcement, poor performance

### 4. PII Masking Strategy
**Decision**: Mask PII in Bronze → Silver transformation
**Rationale**:
- Bronze retains raw data for debugging (restricted access)
- Silver is accessible to analysts (masked data)
- Centralized masking logic
- Audit trail of raw data

**Masking Rules**:
- **Email**: SHA256 hash + preserve domain
  - `john.doe@company.com` → `a3f5b2...@company.com`
  - Enables domain analytics while protecting identity
- **Phone**: Last 4 digits only
  - `+358401234567` → `****4567`
- **Address**: City/Country level only
  - `123 Main St, Helsinki 00100` → `Helsinki, Finland`

**Alternatives Considered**:
- No masking: Violates GDPR principles
- Masking in Gold only: Analysts could still access Silver PII
- Encryption: Harder to query, requires key management

### 5. Change Tracking: SCD Type 2
**Decision**: Implement Slowly Changing Dimension Type 2 in Silver and Gold
**Rationale**:
- Track employee changes over time (job title, department, manager)
- Enable historical reporting ("Who reported to whom in Q1 2025?")
- Standard pattern for employee dimensions
- Hash-based change detection efficient for full loads

**Implementation**:
```
Columns:
- valid_from: DATE (when record became effective)
- valid_to: DATE (when record was superseded, NULL for current)
- is_current: BOOLEAN (quick filter for latest)
- row_hash: STRING (MD5 of business attributes for change detection)
```

**Alternatives Considered**:
- No history: Can't answer historical questions
- SCD Type 1 (overwrite): Loses history
- Separate history table: More complex queries

### 6. Data Quality Strategy
**Decision**: Three-tier quality checks
**Rationale**:
- Critical failures stop pipeline (data integrity)
- Warnings logged but don't block (operational continuity)
- Quarantine for investigation (continuous improvement)

**Tiers**:
1. **Critical** (Pipeline Fails):
   - employee_id NOT NULL and UNIQUE
   - Valid JSON response
   - At least 1 record

2. **Warning** (Log Only):
   - Missing optional fields
   - Format validation failures

3. **Quarantine** (Investigate):
   - Records failing validation → separate table
   - Alert data steward
   - Manual resolution

**Alternatives Considered**:
- Fail on any issue: Too brittle
- No validation: Data quality issues
- Fix automatically: Risk of incorrect assumptions

### 7. Workspace Organization
**Decision**: Domain-based workspaces
- Development: `HR_Dev`
- Production: `HR_Prod`

**Rationale**:
- Aligns with company's domain-driven design
- Clear ownership (HR team)
- Simplified access control
- Logical grouping of HR data sources

**Alternatives Considered**:
- Source-based: `Agileday_Dev` - doesn't scale with multiple HR sources
- Centralized: `DataPlatform_Dev` - too broad, access control issues

### 8. Authentication
**Decision**: Azure Key Vault + Managed Identity
**Rationale**:
- Secure secret storage
- No credentials in code
- Automatic rotation support
- Audit logging

**Implementation**:
- Secret: `agileday-api-token` in Key Vault
- Access: Fabric pipeline Managed Identity
- Rotation: Manual (API token doesn't expire)

**Alternatives Considered**:
- Environment variables: Less secure
- Parameter files: Risk of exposure
- Service principal: More complex, unnecessary

## Consequences

### Positive
- ✅ GDPR-compliant PII handling
- ✅ Historical employee change tracking
- ✅ Reusable Silver layer for future HR analytics
- ✅ Standard pattern (easier onboarding new engineers)
- ✅ Clear separation of concerns (easier debugging)
- ✅ Robust data quality framework

### Negative
- ⚠️ Three layers = more code to maintain
- ⚠️ Slightly longer development time vs. simple Bronze → Gold
- ⚠️ More storage (minimal cost impact for this data volume)

### Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| API schema change breaks pipeline | High | Medium | Schema validation in Bronze, alerts on failure |
| API token expires unexpectedly | High | Low | Monitoring alerts, Key Vault access logging |
| Data volume grows 10x | Medium | Low | Partitioning by date already in place, scales easily |
| PII masking insufficient for compliance | High | Low | Legal review of masking rules, documented in ADR |

## Implementation Notes

### File Structure
```
/fabric/
  /hr_domain/
    /pipelines/
      pl_ingest_agileday_employee_daily.json
    /notebooks/
      transform_agileday_bronze_to_silver.py
      transform_agileday_silver_to_gold.py
    /sql/
      bronze_agileday_employee.sql
      silver_agileday_employee.sql
      gold_hr_dim_employee.sql
      quarantine_agileday_employee.sql
    /tests/
      test_agileday_ingestion.py
      test_agileday_pii_masking.py
      test_agileday_scd.py
```

### Deployment Strategy
1. Deploy to HR_Dev first
2. Run with sample data
3. Validate PII masking
4. Run full test suite
5. Deploy to HR_Prod after approval

## References

- [CLAUDE.md](../CLAUDE.md) - Project guidelines
- [Requirements](./requirements.md) - Detailed requirements
- [Fabric Best Practices](https://learn.microsoft.com/fabric)
- Company GDPR Policy (internal)

## Review & Approval

- [ ] Data Architect Review
- [ ] Security Team Review (PII masking)
- [ ] HR Stakeholder Review
- [ ] Data Engineering Lead Review

---

**Next Steps**: Proceed to detailed design document
