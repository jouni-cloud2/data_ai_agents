# Master Data Management Patterns

Patterns for managing master data entities across multiple source systems.

## What is MDM?

Master Data Management (MDM) creates a single, authoritative view of key business entities that exist across multiple systems.

```
┌─────────────────────────────────────────────────────────────────┐
│                    MASTER DATA MANAGEMENT                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Source Systems              MDM Layer              Consumers   │
│  ┌──────────┐               ┌──────────┐          ┌──────────┐ │
│  │   CRM    │──┐            │ Matching │          │ Analytics│ │
│  └──────────┘  │            │   ┌──────┴─────┐    └──────────┘ │
│  ┌──────────┐  ├──────────►│   │  Golden    │──────►           │
│  │   ERP    │──┤            │   │  Record    │    ┌──────────┐ │
│  └──────────┘  │            │   └──────┬─────┘    │ Reporting│ │
│  ┌──────────┐  │            │ Crosswalk│          └──────────┘ │
│  │   HRIS   │──┘            └──────────┘                       │
│  └──────────┘                                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Common Master Data Entities

| Entity | Typical Sources | Match Keys |
|--------|-----------------|------------|
| **Customer** | CRM, ERP, E-commerce | Email, company domain, name |
| **Employee** | HRIS, Payroll, AD | Work email, employee ID |
| **Product** | PIM, ERP, E-commerce | SKU, UPC, name |
| **Vendor** | ERP, Procurement | Tax ID, company name |
| **Location** | Multiple systems | Address, coordinates |

## MDM Architecture

### Lakehouse MDM Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│  BRONZE - Raw Entity Data (per source)                          │
│  ├── bronze_{source}_employees                                  │
│  ├── bronze_{source}_customers                                  │
│  └── bronze_{source}_products                                   │
└────────────────────────┬────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  SILVER - Matching & Resolution                                 │
│  ├── {entity}_match_candidates   (fuzzy match pairs + scores)   │
│  │   • source_a_id, source_b_id, match_score, match_type        │
│  │   • status: pending_review | approved | rejected             │
│  ├── {entity}_crosswalk          (source → golden_id mapping)   │
│  │   • source_system, source_id, golden_id                      │
│  │   • confidence_score, match_method                           │
│  └── match_audit_log             (stewardship decisions)        │
│      • decision_id, match_id, decision, decided_by, timestamp   │
└────────────────────────┬────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  GOLD - Golden Records                                          │
│  ├── golden_{entity}             (mastered record)              │
│  │   • golden_id (GUID)                                         │
│  │   • best values from sources (survivorship)                  │
│  │   • SCD Type 2 history (valid_from, valid_to, is_current)   │
│  └── {entity}_lineage            (field-level source tracking)  │
│      • golden_id, field_name, source_system, source_value       │
└─────────────────────────────────────────────────────────────────┘
```

## Matching Strategies

### Match Key Selection

| Match Key Type | Pros | Cons | Example |
|----------------|------|------|---------|
| **Exact** | Fast, deterministic | Misses variations | Email address |
| **Fuzzy** | Handles variations | False positives | Company name |
| **Probabilistic** | Handles uncertainty | Complex, requires tuning | Multiple attributes |

### Match Key Normalization

```python
# Normalize match keys before matching
def normalize_email(email: str) -> str:
    if not email:
        return None
    email = email.lower().strip()
    # Remove plus addressing: john+test@email.com -> john@email.com
    local, domain = email.split('@')
    local = local.split('+')[0]
    return f"{local}@{domain}"

def normalize_company_name(name: str) -> str:
    if not name:
        return None
    name = name.upper().strip()
    # Remove common suffixes
    for suffix in [' INC', ' LLC', ' LTD', ' CORP', ' OY', ' AB']:
        name = name.replace(suffix, '')
    # Remove punctuation
    name = re.sub(r'[^\w\s]', '', name)
    return name.strip()
```

### Matching Algorithm

```python
from pyspark.sql.functions import col, levenshtein, soundex

def generate_match_candidates(source_a, source_b, match_threshold=0.8):
    """Generate match candidates between two source tables."""

    # Exact match on email
    exact_matches = source_a.join(
        source_b,
        source_a.email_normalized == source_b.email_normalized,
        "inner"
    ).select(
        source_a.source_id.alias("source_a_id"),
        source_b.source_id.alias("source_b_id"),
        lit(1.0).alias("match_score"),
        lit("exact_email").alias("match_type")
    )

    # Fuzzy match on name (Levenshtein distance)
    fuzzy_matches = source_a.crossJoin(source_b).filter(
        source_a.email_normalized != source_b.email_normalized
    ).withColumn(
        "name_distance",
        levenshtein(source_a.name_normalized, source_b.name_normalized)
    ).withColumn(
        "name_score",
        1 - (col("name_distance") / greatest(
            length(source_a.name_normalized),
            length(source_b.name_normalized)
        ))
    ).filter(col("name_score") >= match_threshold)

    return exact_matches.union(fuzzy_matches)
```

## Survivorship Rules

Determine which source value becomes the "golden" value:

### Common Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **Source priority** | Prefer specific source | HR system for employee data |
| **Most recent** | Latest updated value | Frequently changing attributes |
| **Most complete** | Non-null over null | Sparse data sources |
| **Most frequent** | Majority value | Multiple sources with same weight |
| **Custom logic** | Business rules | Complex requirements |

### Survivorship Configuration

```python
# Survivorship rules per field
SURVIVORSHIP_RULES = {
    "employee": {
        "display_name": {"strategy": "source_priority", "sources": ["alexis", "agileday"]},
        "work_email": {"strategy": "source_priority", "sources": ["alexis", "agileday"]},
        "department": {"strategy": "source_priority", "sources": ["alexis", "hris"]},
        "phone": {"strategy": "most_recent"},
        "title": {"strategy": "source_priority", "sources": ["alexis", "agileday"]},
        "cost_center": {"strategy": "source_priority", "sources": ["erp", "hris"]},
    }
}

def apply_survivorship(sources: list, field: str, entity: str) -> str:
    """Apply survivorship rules to determine golden value."""
    rules = SURVIVORSHIP_RULES[entity][field]

    if rules["strategy"] == "source_priority":
        for source in rules["sources"]:
            if source in sources and sources[source].get(field):
                return sources[source][field]

    elif rules["strategy"] == "most_recent":
        latest = max(sources.values(), key=lambda x: x.get("updated_at", ""))
        return latest.get(field)

    elif rules["strategy"] == "most_complete":
        for source in sources.values():
            if source.get(field):
                return source[field]

    return None
```

## Crosswalk Table

Maps source system IDs to golden IDs:

```sql
CREATE TABLE silver_employee_crosswalk (
    crosswalk_id STRING,           -- UUID
    source_system STRING,          -- 'alexis', 'agileday', 'koho'
    source_employee_id STRING,     -- Original ID in source
    golden_employee_id STRING,     -- Golden record ID
    match_confidence DECIMAL(3,2), -- 0.00 to 1.00
    match_method STRING,           -- 'exact_email', 'fuzzy_name', 'manual'
    matched_at TIMESTAMP,
    matched_by STRING,             -- 'system' or user ID for manual
    is_active BOOLEAN              -- For soft deletes
);

-- Index for efficient lookups
CREATE INDEX idx_crosswalk_source ON silver_employee_crosswalk
    (source_system, source_employee_id);
CREATE INDEX idx_crosswalk_golden ON silver_employee_crosswalk
    (golden_employee_id);
```

### Using Crosswalk for Joins

```python
# Join fact table to golden dimension via crosswalk
fact_with_golden = (
    fact_time_entries
    .join(
        crosswalk,
        (fact_time_entries.source_system == crosswalk.source_system) &
        (fact_time_entries.employee_id == crosswalk.source_employee_id),
        "left"
    )
    .join(
        golden_employee,
        crosswalk.golden_employee_id == golden_employee.golden_id,
        "left"
    )
)
```

## Stewardship

### Manual Review Workflow

```
Match Candidates Queue
        │
        ▼
┌───────────────────┐
│  Auto-Approve     │ ←── Confidence > 0.95
│  (No review)      │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Review Queue     │ ←── 0.70 < Confidence ≤ 0.95
│  (Steward review) │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Auto-Reject      │ ←── Confidence ≤ 0.70
│  (No match)       │
└───────────────────┘
```

### Stewardship Interface Requirements

- View pending match candidates
- See source data side-by-side
- Approve/reject/merge options
- Add notes for decisions
- Audit trail of all decisions

## MDM Refresh Pattern

```python
def refresh_mdm(entity: str):
    """Daily MDM refresh process."""

    # 1. Load new/changed source records
    source_changes = load_incremental_sources(entity)

    # 2. Generate new match candidates
    new_candidates = generate_match_candidates(source_changes, existing_golden)

    # 3. Auto-approve high-confidence matches
    auto_approved = new_candidates.filter(col("match_score") >= 0.95)
    update_crosswalk(auto_approved)

    # 4. Queue medium-confidence for review
    for_review = new_candidates.filter(
        (col("match_score") >= 0.70) &
        (col("match_score") < 0.95)
    )
    queue_for_stewardship(for_review)

    # 5. Process stewardship decisions from previous day
    process_stewardship_decisions()

    # 6. Rebuild golden records
    rebuild_golden_records(entity)
```

## Platform-Specific MDM Tools

| Platform | MDM Capability | Reference |
|----------|---------------|-----------|
| **Azure** | Azure Purview, Dataverse | [Azure MDM](https://learn.microsoft.com/azure/architecture/reference-architectures/data/master-data-management) |
| **Databricks** | Unity Catalog, Delta Sharing | Custom implementation |
| **Snowflake** | Snowflake Data Clean Rooms | Custom implementation |
| **AWS** | AWS Entity Resolution | [Entity Resolution](https://aws.amazon.com/entity-resolution/) |

## References

- [Gartner MDM Magic Quadrant](https://www.gartner.com/en/documents/master-data-management-solutions)
- [DAMA DMBOK - Master Data Management](https://www.dama.org/cpages/body-of-knowledge)
- [Azure MDM Reference Architecture](https://learn.microsoft.com/azure/architecture/reference-architectures/data/master-data-management)

---

*Last Updated: 2026-02-09*
