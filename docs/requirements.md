# Requirements: Agileday Employee Data Source

**Story**: Add Agileday as a new data source for HR domain
**Date**: 2026-01-20
**Author**: Requirements Analyst Agent
**Status**: Draft

## Executive Summary

Implement Agileday employee data ingestion into the HR data domain, creating a complete medallion architecture (Bronze → Silver → Gold) for employee master data management.

## Business Context

**Domain**: Human Resources
**Purpose**: Centralize employee data from Agileday workforce management system
**Stakeholders**: HR Analytics team, People Operations

## Platform

**Selected Platform**: Microsoft Fabric
**Workspace Organization**:
- Development: `HR_Dev`
- Production: `HR_Prod`

## Source System

**System**: Agileday Cloud
**API Endpoint**: `https://cloud2.agileday.io/api/v1/employee`
**Authentication**: Bearer token (stored in Azure Key Vault)
**API Documentation**: Limited - will document schema during implementation

### Source Characteristics
- **API Type**: REST JSON
- **Rate Limits**: Unknown - implement standard retry/backoff
- **Data Volume**: Employee count varies by organization (estimated < 10,000 records)
- **Update Frequency**: Daily full snapshot
- **Historical Data**: Not available via API

## Data Requirements

### Tables to Create

#### Bronze Layer
- **Table**: `bronze_agileday_employee`
- **Purpose**: Raw API response storage
- **Fields**: All fields from API response (to be documented)
- **Format**: Delta Lake
- **Partition**: By `_ingested_date` (YYYY-MM-DD)

#### Silver Layer
- **Table**: `silver_agileday_employee`
- **Purpose**: Cleaned, typed, and PII-masked employee data
- **Transformations**:
  - Type conversions (strings → proper types)
  - PII masking (email, phone, address fields)
  - Data quality validation
  - Deduplication by employee_id
  - SCD Type 2 for historical tracking
- **Quality Rules**:
  - employee_id: NOT NULL, UNIQUE
  - Mandatory fields validation
  - Format validation (email, phone patterns)

#### Gold Layer
- **Table**: `gold_hr_dim_employee`
- **Purpose**: Analytics-ready employee dimension
- **Model Type**: Slowly Changing Dimension Type 2
- **Business Keys**: employee_id
- **Attributes**: All cleaned employee attributes + SCD columns

### Field Mapping

**Bronze Fields**: All fields from API (will document after first ingestion)

**Expected Fields** (based on typical HR systems):
- employee_id (unique identifier)
- first_name, last_name
- email (PII - mask in Silver)
- phone (PII - mask in Silver)
- department
- job_title
- manager_id
- hire_date
- employment_status (active/inactive)
- location/office

**PII Fields to Mask in Silver**:
- email → SHA256 hash + domain preserved for analytics
- phone → Last 4 digits only
- Any address fields → Aggregate to city/country level

**Metadata Columns** (added at each layer):
- `_ingested_at` (timestamp)
- `_source_file` (API endpoint)
- `_pipeline_run_id` (for traceability)

### SCD Type 2 Columns (Silver & Gold)
- `valid_from` (date)
- `valid_to` (date, NULL for current)
- `is_current` (boolean)
- `row_hash` (for change detection)

## Load Strategy

**Type**: Full Load Daily
**Frequency**: Daily at 2:00 AM UTC
**Incremental Logic**: None - full snapshot comparison
**Change Detection**: Hash-based comparison for SCD Type 2

### Load Pattern
1. Bronze: Ingest complete API response daily
2. Silver: Compare with previous day, track changes via SCD Type 2
3. Gold: Rebuild dimension from current Silver records

## Data Quality Requirements

### Critical Rules (Pipeline Failure)
- employee_id must be unique and not null
- API response must be valid JSON
- At least 1 record returned (no empty loads)

### Warning Rules (Log but Continue)
- Missing optional fields (phone, manager_id)
- Unexpected data format (log for investigation)
- Email format validation failures

### Quarantine Strategy
- Invalid records → `quarantine_agileday_employee` table
- Include validation failure reason
- Alert data steward for manual review

## Security & Compliance

### Authentication
- **Token Storage**: Azure Key Vault
- **Secret Name**: `agileday-api-token`
- **Access**: Managed Identity for Fabric pipeline

### PII Handling
- **Regulation**: GDPR compliant
- **Masking Layer**: Bronze → Silver transformation
- **Retention**:
  - Bronze: 90 days (raw data)
  - Silver/Gold: 7 years (masked data)

### Access Control
- Bronze: Data Engineering team only
- Silver: Data Engineering + Data Analysts
- Gold: All HR stakeholders

## Performance Requirements

- **Load Time**: < 5 minutes for < 10K records
- **Freshness**: Data available by 3:00 AM UTC daily
- **Availability**: 99.5% pipeline success rate

## Monitoring & Alerting

### Metrics to Track
- Record count (compare to previous load)
- Load duration
- API response time
- Data quality failures
- PII masking success rate

### Alerts
- Pipeline failure (immediate)
- Record count deviation > 10% (immediate)
- Data quality failures > 5% (daily digest)
- API errors (immediate)

## Dependencies

### Technical
- Azure Key Vault (for API token)
- Fabric Lakehouse (HR_Dev, HR_Prod)
- OneLake storage

### Process
- API token provisioned by IT
- Workspace permissions configured
- Data steward identified for quarantine review

## Success Criteria

- [ ] Daily automated ingestion running
- [ ] PII properly masked in Silver layer
- [ ] SCD Type 2 tracking employee changes
- [ ] Gold dimension queryable by analysts
- [ ] All tests passing (schema, quality, E2E)
- [ ] Documentation complete
- [ ] Monitoring dashboards live

## Migration from Previous Implementation

**Source**: Google Cloud Function + GCS bucket
**Target**: Fabric pipeline + OneLake

**Key Changes**:
- Replace GCS bucket → OneLake Files folder (Bronze)
- Replace Cloud Function → Fabric Data Pipeline
- Same API endpoint and authentication pattern
- Add Silver/Gold layers (not in previous implementation)
- Add PII masking (new requirement)
- Add SCD Type 2 tracking (new requirement)

## Out of Scope

- Historical data backfill (API doesn't support)
- Real-time/streaming ingestion (daily batch sufficient)
- Integration with other HR systems (future phase)
- Custom employee hierarchy modeling (use manager_id as-is)

## Assumptions

1. API token remains valid (no rotation required during implementation)
2. API schema is stable (no breaking changes expected)
3. Employee IDs are immutable unique identifiers
4. Daily snapshot is sufficient for business needs
5. < 10,000 employees in system (scales to millions if needed)

## Questions Resolved

| Question | Answer | Decided By |
|----------|--------|------------|
| Platform? | Microsoft Fabric | User |
| Domain? | HR | User |
| Load type? | Full load daily | User |
| PII handling? | Mask in Silver | User |
| Tables? | HR domain architecture (Bronze/Silver/Gold) | User |
| Fields? | All fields from API | User |
| API endpoints? | /api/v1/employee only | User |

## Next Steps

1. Create ADR-001 documenting architectural decisions
2. Design detailed architecture (schema, pipeline, transformations)
3. Get user approval on design
4. Begin implementation

---

**Prepared by**: Requirements Analyst Agent
**Review Status**: Ready for Architecture Phase
