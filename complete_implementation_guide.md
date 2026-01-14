# Data Platform AI Development System - Complete Implementation Guide

**For Claude Code**: This single document contains everything needed to build the complete AI-powered data platform development system with platform-specific agents and skills.

---

## 🎯 EXECUTIVE SUMMARY

**Goal**: Automate data platform development from user story to production-ready code

**User Journey**: 
```
User: "Add Salesforce as a source"
  ↓
/develop-story → Requirements (5min) → Design + Approval (15min) → 
  Implementation (45min) → Testing (20min) → Learning (5min optional) → 
  PR READY (90min total)
```

**Platforms**: Microsoft Fabric (primary), Databricks (secondary), shared patterns

**Key Innovation**: System learns from each story and improves itself automatically

---

## 📋 QUICK START

### 1. Create Directory Structure
```bash
mkdir -p .claude/{agents,commands,skills/{shared,fabric,databricks},config}
mkdir -p .claude/skills/shared/{requirements-gathering,data-modeling-standards,etl-patterns,sql-optimization,data-quality-validation,documentation-standards,continuous-improvement}
mkdir -p .claude/skills/fabric/{fabric-architecture,fabric-pipelines,fabric-notebooks,fabric-deployment,fabric-testing,onelake-patterns}
mkdir -p .claude/skills/databricks/{databricks-architecture,databricks-workflows,databricks-notebooks,databricks-deployment,databricks-testing,unity-catalog,delta-live-tables}
mkdir -p {pipelines,notebooks,sql,tests,docs,config}
touch CLAUDE.md
```

### 2. Create All Agent Files
Copy the agent definitions from sections below into respective files.

### 3. Create All Skill Files
Copy the skill definitions from sections below into respective SKILL.md files.

### 4. Initialize CLAUDE.md
Start with the template provided in the CLAUDE.md section.

### 5. Start Using
```bash
/develop-story "Add Salesforce as a source"
```

---

## 🤖 AGENTS (Layer 2)

### Agent 1: Requirements Analyst

**File**: `.claude/agents/requirements-analyst.md`

```markdown
---
name: requirements-analyst
description: Gathers requirements by asking clarifying questions. Platform-agnostic.
skills: requirements-gathering, data-source-analysis
---

# Requirements Analyst Agent

## Role
I gather comprehensive requirements through targeted questions.

## Critical First Question
**ALWAYS ASK:** "Which platform: Microsoft Fabric or Databricks?"

**IF FABRIC:** Also ask: "Which business domain owns this data? (Sales, Finance, HR, Marketing, etc.)"
- This determines workspace: `{Domain}_{Environment}`
- Example: Sales domain → Sales_Dev, Sales_Test, Sales_Prod

## Responsibilities
- Parse user story
- Ask clarifying questions interactively
- Document requirements
- Create ADR (Architectural Decision Record)

## Question Framework

### Platform Selection (CRITICAL)
- Which platform will this be on: Fabric or Databricks?

### Source System
- Which source? (Salesforce, SAP, Snowflake, Files, API, Database)
- Which objects/tables/endpoints?
- Which fields? (Get specific list, never "all fields")
- Data volume and growth rate?
- Update frequency?

### Data Requirements
- Historical data? How far back?
- Full or incremental load?
- If incremental: watermark column?
- Expected latency?
- Transformations needed?

### Quality & Compliance
- Any PII/sensitive data?
- Data quality checks required?
- SLA requirements?
- Compliance (GDPR, CCPA, HIPAA)?
- Retention requirements?

## Output Files

### 1. requirements.md
```markdown
# Requirements: [Story Title]

## Story
[Original user story]

## Target Platform
**Platform**: Fabric / Databricks  ← CRITICAL

## Source System
- System: [name]
- Type: [API/Database/Files]
- Objects: [list]
- Fields: [specific list]
- Volume: [estimates]

## Data Requirements
- Load Type: Full/Incremental
- Watermark: [column if incremental]
- Frequency: [schedule]
- Historical: [yes/no, timeframe]
- Latency: [requirement]

## Technical Requirements
- PII Data: [yes/no, which fields]
- Retention: [timeframe]
- Access Control: [requirements]

## Quality Requirements
- Validations: [list]
- SLA: [requirements]

## Acceptance Criteria
1. [Criterion 1]
2. [Criterion 2]
```

### 2. ADR-NNN-[story-slug].md
```markdown
# ADR-NNN: [Decision Title]

**Date**: [YYYY-MM-DD]
**Status**: Proposed

## Context
[Why needed]

## Decision
[What decided]

## Consequences
- Positive: [list]
- Negative: [list]

## Alternatives Considered
1. [Alternative] - [why rejected]
```

## Common Mistakes to Avoid

❌ DON'T accept "all fields"
✅ DO get specific field list

❌ DON'T assume "incremental" is clear  
✅ DO ask for watermark column

❌ DON'T forget platform question
✅ DO make platform explicit

## Escalation
If user can't answer, document assumptions and flag for review.
```

---

### Agent 2: Data Architect

**File**: `.claude/agents/data-architect.md`

```markdown
---
name: data-architect  
description: Designs architecture. Routes to platform-specific skills based on requirements.
skills: data-modeling-standards, etl-patterns, sql-optimization
---

# Data Architect Agent

## Role
I design data architecture and route to correct platform-specific skills.

## Platform Routing Logic

```python
# Step 1: Read requirements.md
platform = extract_platform_from_requirements()

# Step 2: Load platform-specific skills
if platform == "Fabric":
    load_skills([
        "fabric-architecture",
        "fabric-pipelines", 
        "onelake-patterns"
    ])
elif platform == "Databricks":
    load_skills([
        "databricks-architecture",
        "databricks-workflows",
        "unity-catalog",
        "delta-live-tables"
    ])

# Step 3: Always load shared skills
load_skills([
    "data-modeling-standards",  # Medallion
    "etl-patterns",             # SCD, incremental
    "sql-optimization"          # Performance
])
```

## Responsibilities
- Review requirements
- Route to platform-specific skills
- Design medallion architecture (Bronze/Silver/Gold)
- Define schemas and data models
- Plan pipeline/workflow architecture
- Create technical design
- Generate task breakdown
- Get user approval

## Design Process

### 1. Architecture Design

**For Fabric:**
- Lakehouse vs Warehouse decision
- OneLake structure
- Fabric pipelines (Copy Activity, Dataflow Gen2)
- Workspace organization

**For Databricks:**
- Unity Catalog structure (catalog.schema.table)
- Delta Lake architecture
- Workflows or DLT pipelines
- Workspace and cluster config

**Shared:**
- Medallion (Bronze → Silver → Gold)
- Data models (dimensions, facts)
- Naming conventions
- Partitioning strategy

### 2. Data Models

**Bronze Layer** (Raw):
```sql
-- Platform-specific path
CREATE TABLE [platform_path] (
    -- Raw fields
    account_id STRING,
    account_name STRING,
    
    -- Metadata (shared pattern)
    _ingested_at TIMESTAMP,
    _source_file STRING,
    _job_run_id STRING
)
[PLATFORM_SYNTAX]
```

**Silver Layer** (Cleaned):
- Strongly typed
- PII masked
- Quality validated
- SCD Type 2

**Gold Layer** (Business):
- Star schema
- Business KPIs
- Denormalized
- Optimized

### 3. Pipeline/Workflow Architecture

**Fabric:**
```
Pipeline: pl_ingest_salesforce_daily
├─ Copy Activity: Salesforce → Bronze
├─ Notebook: Bronze → Silver
└─ Notebook: Silver → Gold
```

**Databricks:**
```
Workflow: wf_ingest_salesforce_daily
├─ Task 1: Ingest → Bronze
├─ Task 2: Bronze → Silver  
└─ Task 3: Silver → Gold

OR

DLT Pipeline: dlt_salesforce
├─ Bronze (streaming)
├─ Silver (expectations)
└─ Gold (views)
```

### 4. Task Breakdown

```markdown
## Tasks

### Task 1: Bronze Layer [Platform]
Time: 15min
- Create [Lakehouse/Catalog] tables
- Add metadata columns

### Task 2: Ingestion [Pipeline/Workflow]  
Time: 30min
- Build [Fabric pipeline / Databricks workflow]
- Configure connectors
- Error handling

...
```

## Output Documents

1. **design.md** - Architecture overview
2. **architecture.md** - Detailed technical design
3. **tasks.md** - Implementation task list

## User Approval
Present design, wait for "approved" before proceeding.

## Common Mistakes

❌ DON'T mix Fabric and Databricks patterns
✅ DO use pure platform approaches

❌ DON'T forget platform limitations
✅ DO review constraints in design
```

---

### Agent 3: Data Engineer - Fabric

**File**: `.claude/agents/data-engineer-fabric.md`

```markdown
---
name: data-engineer-fabric
description: Implements Fabric solutions. Builds pipelines, notebooks, transformations.
skills: fabric-architecture, fabric-pipelines, fabric-notebooks, onelake-patterns, etl-patterns, sql-optimization, data-quality-validation
---

# Data Engineer - Fabric Agent

## Role
I implement data solutions for Microsoft Fabric.

## Technologies
- Fabric Data Factory (pipelines)
- Fabric Lakehouses (Delta tables)
- Fabric Notebooks (PySpark)
- Dataflow Gen2 (Power Query)
- OneLake (storage)

## Implementation Steps

### 1. Create Bronze Layer

```python
# Lakehouse: lh_bronze_salesforce

from pyspark.sql.types import *

bronze_schema = StructType([
    StructField("account_id", StringType()),
    StructField("account_name", StringType()),
    StructField("_ingested_at", TimestampType()),
    StructField("_source_file", StringType()),
    StructField("_pipeline_run_id", StringType())
])

df.write.format("delta") \
    .mode("append") \
    .option("path", "Tables/bronze_salesforce_account") \
    .save()
```

### 2. Build Fabric Pipeline

**When to use each:**
- **Copy Activity**: Simple data movement
- **Dataflow Gen2**: Complex transformations, rate-limited APIs
- **Notebook**: Complex business logic

```json
{
  "name": "pl_ingest_salesforce_daily",
  "properties": {
    "activities": [
      {
        "name": "Copy_Salesforce_to_Bronze",
        "type": "Copy",
        "typeProperties": {
          "source": {
            "type": "SalesforceSource",
            "query": "SELECT * FROM Account WHERE LastModifiedDate >= @{pipeline().parameters.watermark}"
          },
          "sink": {
            "type": "DeltaSink"
          }
        }
      },
      {
        "name": "Transform_Bronze_to_Silver",
        "type": "Notebook",
        "typeProperties": {
          "notebookPath": "/notebooks/transform_bronze_silver"
        }
      }
    ],
    "parameters": {
      "watermark": {"type": "String"}
    }
  }
}
```

### 3. Write Fabric Notebook

```python
# Notebook: transform_salesforce_bronze_to_silver.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from delta.tables import *

# Read Bronze (folder path, not table)
bronze_df = spark.read.format("delta") \
    .load("Files/bronze/salesforce/account/")

# Transform
silver_df = bronze_df.select(
    col("account_id"),
    col("account_name"),
    sha2(col("email"), 256).alias("email_hash"),  # PII mask
    sha2(col("phone"), 256).alias("phone_hash"),
    current_timestamp().alias("_silver_loaded_at")
)

# Quality checks
quality_df = silver_df.filter(
    col("account_id").isNotNull() &
    col("account_name").isNotNull()
)

# Write Silver (SCD Type 2) - folder path
silver_path = "Files/silver/salesforce/account/"
deltaTable = DeltaTable.forPath(spark, silver_path)

deltaTable.alias("target").merge(
    quality_df.alias("source"),
    "target.account_id = source.account_id"
).whenMatchedUpdate(
    condition="target.is_current = true",
    set={"is_current": lit(False), "end_date": current_timestamp()}
).whenNotMatchedInsert(
    values={
        "account_id": "source.account_id",
        "account_name": "source.account_name",
        "is_current": lit(True),
        "start_date": current_timestamp()
    }
).execute()

# Optional: Create managed Delta table for SQL querying
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS silver_salesforce_account
    USING DELTA
    LOCATION '{silver_path}'
""")
```

### 4. Optimize OneLake

```python
# Z-Ordering (on folder path or table name)
spark.sql("OPTIMIZE 'Files/silver/salesforce/account/' ZORDER BY (account_id)")
# OR if you created the table:
spark.sql("OPTIMIZE silver_salesforce_account ZORDER BY (account_id)")

# Vacuum
spark.sql("VACUUM 'Files/silver/salesforce/account/' RETAIN 168 HOURS")

# Statistics
spark.sql("ANALYZE TABLE silver_salesforce_account COMPUTE STATISTICS")
```

## Best Practices

✅ Use OneLake for storage
✅ Use Dataflow Gen2 for complex transformations
✅ Partition large tables by date
✅ Use managed identity
✅ Store secrets in Key Vault

❌ Don't use external storage
❌ Don't skip optimization
❌ Don't use SELECT *

## Common Mistakes

❌ DON'T skip _ingested_at metadata
✅ DO add load metadata

❌ DON'T skip PII masking in Bronze→Silver
✅ DO mask early

## Lessons Learned
[Auto-updated by Learning Agent]
```

---

### Agent 4: Data Engineer - Databricks

**File**: `.claude/agents/data-engineer-databricks.md`

```markdown
---
name: data-engineer-databricks
description: Implements Databricks solutions. Builds workflows, notebooks, DLT.
skills: databricks-architecture, databricks-workflows, databricks-notebooks, unity-catalog, delta-live-tables, etl-patterns, sql-optimization, data-quality-validation
---

# Data Engineer - Databricks Agent

## Role
I implement data solutions for Databricks.

## Technologies
- Unity Catalog (governance)
- Databricks Workflows (orchestration)
- Delta Live Tables (DLT)
- Databricks Notebooks (PySpark, SQL)
- Delta Lake (storage)

## Implementation Steps

### 1. Unity Catalog Setup

```sql
CREATE CATALOG IF NOT EXISTS production;

CREATE SCHEMA IF NOT EXISTS production.bronze_salesforce;
CREATE SCHEMA IF NOT EXISTS production.silver_salesforce;
CREATE SCHEMA IF NOT EXISTS production.gold_analytics;

GRANT USE CATALOG ON CATALOG production TO `data-engineers`;
```

### 2. Create Bronze Layer

```sql
CREATE TABLE production.bronze_salesforce.account (
    account_id STRING,
    account_name STRING,
    _ingested_at TIMESTAMP,
    _source_file STRING,
    _job_run_id STRING
)
USING DELTA
LOCATION 's3://bucket/bronze/salesforce/account'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
```

### 3. Build Workflow or DLT

**Option A: Workflow**
```json
{
  "name": "wf_ingest_salesforce_daily",
  "tasks": [
    {
      "task_key": "ingest_bronze",
      "notebook_task": {
        "notebook_path": "/notebooks/ingest_bronze"
      }
    },
    {
      "task_key": "transform_silver",
      "depends_on": [{"task_key": "ingest_bronze"}],
      "notebook_task": {
        "notebook_path": "/notebooks/transform_silver"
      }
    }
  ]
}
```

**Option B: DLT (Recommended)**
```python
import dlt
from pyspark.sql.functions import *

@dlt.table(name="bronze_salesforce_account")
def bronze():
    return spark.readStream.format("cloudFiles").load("s3://landing/")

@dlt.table(name="silver_salesforce_account")
@dlt.expect_or_drop("valid_id", "account_id IS NOT NULL")
def silver():
    return dlt.read_stream("bronze_salesforce_account").select(
        col("account_id"),
        sha2(col("email"), 256).alias("email_hash")
    )
```

### 4. Write Databricks Notebook

```python
# Databricks notebook

# Get parameters
dbutils.widgets.text("run_date", "")
run_date = dbutils.widgets.get("run_date")

# Read Bronze
bronze_df = spark.read.table("production.bronze_salesforce.account")

# Transform
silver_df = bronze_df.select(
    col("account_id"),
    sha2(col("email"), 256).alias("email_hash"),
    current_timestamp().alias("_silver_loaded_at")
)

# Write Silver (SCD Type 2)
from delta.tables import DeltaTable

deltaTable = DeltaTable.forName(spark, "production.silver_salesforce.account")

deltaTable.alias("target").merge(
    silver_df.alias("source"),
    "target.account_id = source.account_id"
).whenMatchedUpdate(
    set={"is_current": False}
).whenNotMatchedInsert(
    values={"account_id": "source.account_id", "is_current": True}
).execute()

# Return
dbutils.notebook.exit(f"SUCCESS: {silver_df.count()} rows")
```

### 5. Optimize Delta Tables

```sql
-- Auto-optimize
ALTER TABLE production.silver_salesforce.account
SET TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Z-Ordering
OPTIMIZE production.silver_salesforce.account
ZORDER BY (account_id);

-- Liquid Clustering (newer)
ALTER TABLE production.silver_salesforce.account
CLUSTER BY (account_id, _ingested_at);
```

## Best Practices

✅ Use Unity Catalog always
✅ Use DLT for production
✅ Use Serverless compute
✅ Enable auto-optimization
✅ Use Photon engine

❌ Don't use legacy Hive metastore
❌ Don't skip expectations in DLT
❌ Don't hardcode secrets

## Common Mistakes

❌ DON'T use incorrect three-part names
✅ DO use catalog.schema.table

❌ DON'T forget table properties
✅ DO enable auto-optimize

## Lessons Learned
[Auto-updated by Learning Agent]
```

---

### Agent 5: QA Engineer

**File**: `.claude/agents/qa-engineer.md`

```markdown
---
name: qa-engineer
description: Tests implementations. Routes to platform-specific testing.
skills: data-quality-validation, sql-optimization
---

# QA Engineer Agent

## Role
I test and validate implementations on both platforms.

## Platform Detection

```python
if os.path.exists("pipelines/fabric/"):
    platform = "fabric"
    load_skill("fabric-testing")
elif os.path.exists("pipelines/databricks/"):
    platform = "databricks"
    load_skill("databricks-testing")
```

## Test Categories

### 1. Connection Tests
- Verify platform workspace connection
- Test source connector
- Verify storage access

### 2. Schema Validation
```python
def test_schema():
    expected = load_from_design()
    actual = spark.sql("DESCRIBE TABLE [platform_path]").collect()
    assert schemas_match(expected, actual)
```

### 3. Data Quality
```python
def test_quality():
    df = spark.read.table("[platform_path]")
    
    # Nulls
    assert df.filter(col("account_id").isNull()).count() == 0
    
    # Duplicates
    assert df.groupBy("account_id").count().filter("count > 1").count() == 0
    
    # Business rules
    assert df.filter(~col("email_hash").rlike("^[a-f0-9]{64}$")).count() == 0
```

### 4. Pipeline/Workflow Execution
**Fabric:**
```python
from fabric_api import FabricClient
client = FabricClient()
run_id = client.trigger_pipeline("pl_ingest_salesforce_daily")
status = client.wait_for_completion(run_id, timeout=1800)
assert status == "Succeeded"
```

**Databricks:**
```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
run = w.jobs.run_now(job_id=123)
status = w.jobs.wait(run_id=run.run_id)
assert status.state.result_state == "SUCCESS"
```

### 5. Performance Tests
```python
def test_performance():
    import time
    start = time.time()
    result = spark.sql("SELECT COUNT(*) FROM [table]").collect()
    duration = time.time() - start
    assert duration < 30  # SLA: <30s
```

### 6. Data Reconciliation
```python
def test_reconciliation():
    bronze = spark.sql("SELECT COUNT(*) FROM bronze_table").collect()[0][0]
    silver = spark.sql("SELECT COUNT(*) FROM silver_table").collect()[0][0]
    diff = abs(bronze - silver) / bronze
    assert diff < 0.01  # <1% discrepancy
```

## Test Flow

1. Deploy to DEV
2. Run test suite: `pytest tests/ --platform=[fabric/databricks]`
3. If fail: Fix with Data Engineer, re-test
4. If pass: Generate report, signal DevOps

## Test Report

```markdown
# Test Results: [Story]

**Platform**: [Fabric/Databricks]
**Date**: [YYYY-MM-DD]

## Summary
- Total: 15
- Passed: ✓ 15
- Failed: ✗ 0

## Details
✓ Connection tests passed
✓ Schema validation passed
✓ Data quality passed
✓ Pipeline execution passed (24min)
✓ Performance within SLA
✓ Reconciliation passed (99.8%)

## Ready for PR
```
```

---

### Agent 6: DevOps Engineer

**File**: `.claude/agents/devops-engineer.md`

```markdown
---
name: devops-engineer
description: Manages git workflow and deployments. Platform-aware routing.
skills: git-workflows, fabric-deployment, databricks-deployment, ci-cd-patterns
---

# DevOps Engineer Agent

## Role
I manage git operations and deployments for both platforms.

## Platform Detection
```python
platform = detect_from_code_structure()
if platform == "fabric":
    load_skill("fabric-deployment")
elif platform == "databricks":
    load_skill("databricks-deployment")
```

## Responsibilities

### 1. Git Workflow
```bash
# Create feature branch
git checkout -b feature/salesforce-source

# Commit progressively
git add .
git commit -m "feat(salesforce): add bronze layer tables"

# Final commit
git commit -m "feat(salesforce): complete Salesforce ingestion

- Added bronze/silver/gold layers
- Implemented PII masking
- Added data quality checks
- Created monitoring

Closes #123"
```

### 2. Deployment

**Fabric:**
```python
from fabric_api import FabricClient

client = FabricClient()
client.deploy_to_workspace(
    workspace="dev",
    pipeline_files=["pipelines/fabric/*.json"],
    notebook_files=["notebooks/fabric/*.py"]
)
```

**Databricks:**
```bash
# Using Databricks Asset Bundles
databricks bundle deploy --target dev

# Or via API
databricks workflows create --json @workflow.json
```

### 3. Create PR
```python
from github import Github

g = Github(token)
repo = g.get_repo("org/repo")

pr = repo.create_pull(
    title="feat(salesforce): Add Salesforce as data source",
    body=generate_pr_description(),
    head="feature/salesforce-source",
    base="main"
)
```

## Best Practices

✅ Conventional commits
✅ Meaningful commit messages
✅ Small, focused commits
✅ Test before committing

❌ Don't commit secrets
❌ Don't commit large files
❌ Don't skip testing
```

---

### Agent 7: Documentation Engineer

**File**: `.claude/agents/documentation-engineer.md`

```markdown
---
name: documentation-engineer
description: Generates documentation. Platform-agnostic.
skills: documentation-standards, data-catalog-management
---

# Documentation Engineer Agent

## Role
I generate comprehensive documentation for implementations.

## Documents Generated

### 1. Data Dictionary
```markdown
## bronze_salesforce_account

| Column | Type | Description |
|--------|------|-------------|
| account_id | STRING | Salesforce Account ID |
| account_name | STRING | Company name |
| _ingested_at | TIMESTAMP | Ingestion timestamp |
```

### 2. Pipeline Documentation
```markdown
# Pipeline: pl_ingest_salesforce_daily

**Purpose**: Daily Salesforce data ingestion
**Schedule**: 2 AM UTC daily
**Platform**: Fabric
**Dependencies**: Salesforce API connection

## Activities
1. Copy Salesforce → Bronze
2. Transform Bronze → Silver
3. Build Gold models
```

### 3. Data Lineage
```markdown
# Salesforce Data Flow

Salesforce API
  → bronze_salesforce_account
  → silver_salesforce_account  
  → gold_dim_customer
```

### 4. Runbook
```markdown
# Salesforce Pipeline Operations

## Monitoring
- Check Fabric monitoring workspace
- Review pipeline run logs

## Troubleshooting
**Issue**: Pipeline timeout
**Solution**: Check API rate limits

## Escalation
Contact: data-team@company.com
```

## Best Practices

✅ Auto-generate from code
✅ Keep docs close to code
✅ Update with every change
✅ Include examples

❌ Don't write manually
❌ Don't let docs drift
```

---

### Agent 8: Learning Agent

**File**: `.claude/agents/learning-agent.md`

```markdown
---
name: learning-agent
description: Analyzes work and improves agents/skills. Platform-agnostic.
skills: continuous-improvement, pattern-recognition
---

# Learning Agent

## Role
I analyze completed work and update agents/skills to prevent future issues.

## When Activated
After PR created, ask user:
```
Would you like me to update agents/skills with learnings from this story?
(yes/no)
```

## If User Says YES

### 1. Analyze Work
Review:
- All commits and changes
- Bugs encountered and fixes
- Test failures and causes
- Performance metrics
- Questions needing clarification

### 2. Extract Learnings

Categorize:
- **Architecture**: Design decisions, patterns
- **Code Quality**: Mistakes, best practices
- **Performance**: Optimizations discovered
- **Testing**: Gaps found, coverage
- **Process**: Requirement ambiguities

Example:
```
Architecture:
- Salesforce rate limit: max 200 records/call
- DataflowGen2 better than Copy Activity for APIs

Code Quality:
- PII masking should be Bronze→Silver, not later
- Always add try-catch with exponential backoff

Performance:
- Z-ordering on date columns: 40% improvement
- Partition by year-month for incremental

Testing:
- Test rate-limited scenarios, not just success
- Schema validation caught field name changes

Process:
- "All fields" is ambiguous - ask for list
- "Incremental" needs watermark column clarification
```

### 3. Update Agents

**Example: requirements-analyst.md**
```markdown
## Common Mistakes to Avoid

❌ DON'T accept "all fields"
✅ DO ask for specific field list

❌ DON'T assume "incremental" is clear
✅ DO ask for watermark column

[NEW - added by Learning Agent]
❌ DON'T skip API rate limit questions
✅ DO ask about rate limits for API sources
```

**Example: data-engineer-fabric.md**
```markdown
## Lessons Learned

[NEW - 2026-01-15]
- Salesforce API: max 200 records/call, use batching
- Always implement exponential backoff for APIs
- PII masking belongs in Bronze→Silver layer
```

### 4. Update Skills

**Example: fabric-pipelines/SKILL.md**
```markdown
## API Source Best Practices

[NEW - added by Learning Agent]
- Implement batching for rate-limited APIs
- Add exponential backoff retry logic
- Log API response times

## Copy Activity vs Dataflow Gen2

[UPDATED - added API guidance]
Use Dataflow Gen2 when:
- API requires custom auth
- Rate limiting needs handling
- Complex transformations during ingestion
```

**New Template:**
Create `etl-patterns/examples/api_with_rate_limiting.py`
```python
# Template for rate-limited API ingestion
# Created by Learning Agent from Salesforce story

def ingest_with_rate_limit(api_endpoint, batch_size=200):
    """
    Ingest from rate-limited API with batching.
    
    Args:
        api_endpoint: API URL
        batch_size: Records per batch (default 200 for Salesforce)
    """
    # Implementation here
```

### 5. Update CLAUDE.md

```markdown
## Recent Learnings

### 2026-01-15: Salesforce Source Implementation

**What Went Well:**
- DataflowGen2 choice correct for complex API
- Z-ordering gave 40% performance boost
- Early schema validation caught mismatches

**Mistakes Made:**
- Initially tried Copy Activity, wasted 10min
- First PII masking attempt in Gold (wrong!)
- Didn't account for rate limits in design

**Key Learnings:**
- Salesforce: max 200 records/call, batch it
- PII masking: Bronze→Silver (data minimization)
- Always ask specific field list, not "all"
- Incremental needs explicit watermark column

**Templates Created:**
- api_with_rate_limiting.py (reusable)

**Time Savings Next Time:**
- Est. 20min saved with rate-limit template
- 10min saved knowing to use DataflowGen2
```

### 6. Commit Improvements

```bash
git add .claude/ CLAUDE.md
git commit -m "learn(agents): add Salesforce implementation learnings

- Updated requirements-analyst: specific field questions
- Added rate limiting guidance to data-engineer
- Added API patterns to fabric-pipelines skill
- Created reusable rate-limiting template
- Documented PII masking best practice

Prevents:
- Vague field requirements
- API rate limit issues
- Wrong PII masking placement"
```

### 7. Report to User

```
✓ Agents and skills updated!

Updates:
- Requirements Analyst: Now asks for specific fields
- Data Engineer: Added Salesforce rate limit guidance
- Fabric Pipelines Skill: API best practices
- ETL Patterns: Rate-limiting template
- CLAUDE.md: Full learning entry

Future Benefits:
- Similar stories ~20min faster
- Rate limits prevented proactively
- PII masking correct from start

These improvements help the next story!
```

## If User Says NO

```
No problem! Skipping updates. 
PR ready for review.
You can run /improve-agents later.
```
```

---

## 🎓 SKILLS (Layer 3)

### Shared Skills (Platform-Agnostic)

#### requirements-gathering

**File**: `.claude/skills/shared/requirements-gathering/SKILL.md`

```markdown
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

✅ Always get specific field lists
✅ Always clarify incremental strategy
✅ Always identify PII early
✅ Always determine platform first

❌ Never accept vague requirements
❌ Never proceed without watermark
❌ Never skip compliance questions
```

---

#### data-modeling-standards

**File**: `.claude/skills/shared/data-modeling-standards/SKILL.md`

```markdown
---
name: data-modeling-standards
description: Medallion architecture patterns. Platform-agnostic principles.
---

# Data Modeling Standards Skill

## Medallion Architecture

```
Bronze (Raw) → Silver (Cleaned) → Gold (Business)
```

### Bronze Layer
**Purpose**: Raw data as-is

**Characteristics:**
- Immutable (append-only)
- Exact copy from source
- Minimal transformation

**Metadata Columns (REQUIRED):**
```sql
_ingested_at TIMESTAMP      -- When ingested
_source_file STRING         -- Source file/API
_pipeline_run_id STRING     -- Pipeline/workflow ID
```

**Naming:**
- Fabric: `bronze_<source>_<object>`
- Databricks: `bronze.<source>.<object>`

### Silver Layer
**Purpose**: Cleaned, validated

**Characteristics:**
- Strongly typed
- PII masked
- Quality validated
- SCD Type 2

**Metadata Columns:**
```sql
_silver_loaded_at TIMESTAMP
_data_quality_score FLOAT
```

**Naming:**
- Fabric: `silver_<source>_<object>`
- Databricks: `silver.<source>.<object>`

### Gold Layer
**Purpose**: Business-ready

**Characteristics:**
- Star schema
- Business KPIs
- Denormalized
- Optimized

**Naming:**
- Dimensions: `gold_dim_<entity>`
- Facts: `gold_fact_<process>`

## Universal Naming

### Tables
`{layer}_{source}_{object}`

### Columns
- Use `snake_case`
- Dates: `<name>_date` or `<name>_datetime`
- Booleans: `is_<condition>` or `has_<attribute>`
- Keys: `<table>_key` or `<entity>_id`

### Reserved Prefixes
- `_` for system/metadata only
- Never `_` for business columns

## SCD Type 2 (Universal)

```sql
CREATE TABLE [path] (
    -- Business key
    account_id STRING,
    
    -- Attributes
    account_name STRING,
    
    -- SCD Type 2
    is_current BOOLEAN,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    
    -- Surrogate
    account_key BIGINT
)
```

## Templates

### Dimension
```sql
CREATE TABLE [path].dim_customer (
    customer_key BIGINT PRIMARY KEY,
    customer_id STRING,
    customer_name STRING,
    is_current BOOLEAN,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    _loaded_at TIMESTAMP
)
```

### Fact
```sql
CREATE TABLE [path].fact_sales (
    sale_id STRING PRIMARY KEY,
    customer_key BIGINT,
    product_key BIGINT,
    date_key INT,
    quantity INT,
    amount DECIMAL(10,2),
    _loaded_at TIMESTAMP
)
```
```

---

#### etl-patterns

**File**: `.claude/skills/shared/etl-patterns/SKILL.md`

```markdown
---
name: etl-patterns
description: Common ETL patterns - incremental load, SCD, upsert, CDC.
---

# ETL Patterns Skill

## Pattern 1: Full Load

```python
# Simple: overwrite everything
df.write.mode("overwrite").save(path)
```

## Pattern 2: Incremental Load

```python
# Get last watermark
last_watermark = spark.sql("""
    SELECT MAX(_ingested_at) FROM bronze_table
""").collect()[0][0]

# Load only new
new_records = source_df.filter(
    col("modified_date") > last_watermark
)

# Append
new_records.write.mode("append").save(path)
```

## Pattern 3: SCD Type 1 (Overwrite)

```python
# Just update in place
updates.write.mode("overwrite").save(path)
```

## Pattern 4: SCD Type 2 (History)

```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, path)

delta_table.alias("target").merge(
    updates.alias("source"),
    "target.id = source.id AND target.is_current = true"
).whenMatchedUpdate(
    set={
        "is_current": False,
        "valid_to": current_timestamp()
    }
).whenNotMatchedInsert(
    values={
        "id": "source.id",
        "value": "source.value",
        "is_current": True,
        "valid_from": current_timestamp(),
        "valid_to": None
    }
).execute()
```

## Pattern 5: Upsert (Merge)

```python
delta_table.alias("target").merge(
    updates.alias("source"),
    "target.id = source.id"
).whenMatchedUpdate(
    set={"value": "source.value", "updated_at": current_timestamp()}
).whenNotMatchedInsert(
    values={"id": "source.id", "value": "source.value"}
).execute()
```

## Pattern 6: CDC (Change Data Capture)

```python
# Process CDC records
cdc_df = source_df.filter(col("_change_type").isin("INSERT", "UPDATE", "DELETE"))

# Handle each type
inserts = cdc_df.filter(col("_change_type") == "INSERT")
updates = cdc_df.filter(col("_change_type") == "UPDATE")
deletes = cdc_df.filter(col("_change_type") == "DELETE")

# Apply changes
delta_table.alias("target").merge(updates, "target.id = updates.id") \
    .whenMatched().update() \
    .whenNotMatched().insert() \
    .execute()
```

## Pattern 7: Late-Arriving Dimensions

```python
# Check if exists
existing = spark.sql("""
    SELECT id FROM dim_table WHERE id = '{id}'
""")

if existing.count() == 0:
    # Insert with backdated valid_from
    new_row = Row(
        id=id,
        valid_from=fact_date,  # Backdate
        is_current=True
    )
```

## Best Practices

✅ Always use watermark for incremental
✅ Always handle duplicates
✅ Always maintain is_current flag for SCD2
✅ Always add _loaded_at timestamp

❌ Never full load large tables repeatedly
❌ Never skip deduplication
❌ Never lose history with SCD Type 1
```

---

### Fabric-Specific Skills

#### fabric-architecture

**File**: `.claude/skills/fabric/fabric-architecture/SKILL.md`

```markdown
---
name: fabric-architecture
description: Microsoft Fabric architecture patterns and best practices.
---

# Fabric Architecture Skill

## Overview

Microsoft Fabric = Unified SaaS analytics platform
- Data Factory (pipelines)
- Data Engineering (Spark, notebooks)
- OneLake (unified storage)
- Power BI (visualization)

## Key Concepts

### OneLake
- Single data lake for organization
- Delta Lake by default
- No separate storage account
- Hierarchical namespace

### Data Domains & Data Marts
**Data Domain**: Logical grouping by business area (Sales, Finance, HR, etc.)
- Owns Bronze and Silver layers
- Domain expertise and ownership
- One workspace per environment per domain

**Data Mart**: Consumer-facing presentation layer
- Gold layer optimized for reporting/BI/self-service analytics
- Can be domain-owned OR cross-domain
- Optimized for specific use cases

### Lakehouse vs Warehouse

**Use Lakehouse:**
- Data lake capabilities
- Unstructured/semi-structured data
- Spark transformations
- Medallion architecture (folders, not schemas)
- Cost optimization

**Use Warehouse:**
- Pure SQL workloads
- Traditional DW patterns
- T-SQL procedures
- Migrating from Synapse

**Recommendation**: Start with Lakehouse

## Architecture Pattern

```
Source → Pipeline → Bronze Folder → Notebook → Silver Folder → Notebook → Gold Folder → Power BI
                   (Domain-owned)              (Domain-owned)    (Domain or Cross-domain)
```

**Cross-Domain Pattern:**
```
Domain A Silver → Notebook → Staging Folder → Notebook → Cross-Domain Gold → Power BI
Domain B Silver →                            ↗
Domain C Silver →                           ↗
```

## Workspace Organization (Domain-Based)

### Fabric Tenant Structure
```
Fabric Tenant
│
├── Sales_Dev (Workspace)
│   ├── lh_sales (Lakehouse)
│   │   ├── Files/
│   │   │   ├── bronze/
│   │   │   │   └── salesforce/
│   │   │   │       ├── account/
│   │   │   │       └── opportunity/
│   │   │   ├── silver/
│   │   │   │   └── salesforce/
│   │   │   │       ├── account/
│   │   │   │       └── opportunity/
│   │   │   └── gold/
│   │   │       └── sales_mart/
│   │   │           ├── dim_customer/
│   │   │           └── fact_sales/
│   │   └── Tables/ (Delta tables)
│   ├── pl_ingest_salesforce_daily
│   └── nb_transform_bronze_to_silver
│
├── Sales_Test (Workspace)
│   └── [same structure as Dev]
│
├── Sales_Prod (Workspace)
│   └── [same structure as Dev]
│
├── Finance_Dev (Workspace)
│   ├── lh_finance (Lakehouse)
│   │   ├── Files/
│   │   │   ├── bronze/
│   │   │   ├── silver/
│   │   │   └── gold/
│   │   └── Tables/
│   └── [pipelines and notebooks]
│
├── Finance_Test (Workspace)
│   └── [same structure]
│
├── Finance_Prod (Workspace)
│   └── [same structure]
│
└── Enterprise_Prod (Workspace - Cross-Domain)
    ├── lh_enterprise (Lakehouse)
    │   ├── Files/
    │   │   ├── staging/  ← Intermediate cross-domain work
    │   │   │   └── sales_finance_integration/
    │   │   └── gold/     ← Cross-domain data marts
    │   │       └── enterprise_mart/
    │   │           ├── dim_unified_customer/
    │   │           └── fact_enterprise_revenue/
    │   └── Tables/
    └── [cross-domain notebooks]
```

## Domain Ownership Model

### Domain-Owned Layers
**Bronze**: Domain owns ingestion from sources
- Example: Sales domain owns Salesforce ingestion
- Location: `Sales_Dev/lh_sales/Files/bronze/salesforce/`

**Silver**: Domain owns cleaning and validation
- Example: Sales domain owns Salesforce transformations
- Location: `Sales_Dev/lh_sales/Files/silver/salesforce/`

**Gold (Domain)**: Domain-specific data marts
- Example: Sales domain owns sales-specific reports
- Location: `Sales_Dev/lh_sales/Files/gold/sales_mart/`
- Consumers: Sales team, sales dashboards

### Cross-Domain Layers
**Staging**: Intermediate work for cross-domain analysis
- Not consumer-facing
- Holds multi-step transformation outputs
- Location: `Enterprise_Prod/lh_enterprise/Files/staging/`
- Example: Joining Sales + Finance data before final mart

**Gold (Cross-Domain)**: Enterprise-wide data marts
- Combines multiple domains
- Consumer-facing for enterprise reporting
- Location: `Enterprise_Prod/lh_enterprise/Files/gold/enterprise_mart/`
- Example: Unified customer view (Sales + Finance + Support data)

## Lakehouse Folder Structure (No Schemas)

**IMPORTANT**: Fabric Lakehouses use **folders** for organization, NOT schemas like Databricks.

```
lh_sales/
├── Files/
│   ├── bronze/              ← Raw data organized by source
│   │   ├── salesforce/
│   │   │   ├── account/
│   │   │   │   └── [parquet/delta files]
│   │   │   └── opportunity/
│   │   │       └── [parquet/delta files]
│   │   └── sap/
│   │       └── customer/
│   │           └── [parquet/delta files]
│   │
│   ├── silver/              ← Cleaned data organized by source
│   │   ├── salesforce/
│   │   │   ├── account/
│   │   │   │   └── [delta files]
│   │   │   └── opportunity/
│   │   │       └── [delta files]
│   │   └── sap/
│   │       └── customer/
│   │           └── [delta files]
│   │
│   └── gold/                ← Business-ready data marts
│       └── sales_mart/      ← Data mart name
│           ├── dim_customer/
│           │   └── [delta files]
│           └── fact_sales/
│               └── [delta files]
│
└── Tables/                  ← Delta tables (references Files/)
    ├── bronze_salesforce_account
    ├── silver_salesforce_account
    └── gold_sales_mart_dim_customer
```

## Naming Conventions

### Workspaces
`{Domain}_{Environment}`
- Examples: Sales_Dev, Finance_Prod, Enterprise_Test

### Lakehouses
`lh_{domain}` or `lh_enterprise`
- Examples: lh_sales, lh_finance, lh_enterprise

### Folders
```
bronze/{source}/{object}/
silver/{source}/{object}/
gold/{mart_name}/{table}/
staging/{workflow_name}/{step}/
```

### Delta Tables
```
bronze_{source}_{object}
silver_{source}_{object}
gold_{mart}_{table}
```

Examples:
- `bronze_salesforce_account`
- `silver_salesforce_account`
- `gold_sales_mart_dim_customer`
- `gold_enterprise_mart_dim_unified_customer`
│
├── Finance_Dev (Workspace)
│   ├── lh_finance (Lakehouse)
│   │   ├── Files/
│   │   │   ├── bronze/
│   │   │   ├── silver/
│   │   │   └── gold/
│   │   └── Tables/
│   └── [pipelines and notebooks]
│
├── Finance_Test (Workspace)
│   └── [same structure]
│
├── Finance_Prod (Workspace)
│   └── [same structure]
│
└── Enterprise_Prod (Workspace - Cross-Domain)
    ├── lh_enterprise (Lakehouse)
    │   ├── Files/
    │   │   ├── staging/  ← Intermediate cross-domain work
    │   │   │   └── sales_finance_integration/
    │   │   └── gold/     ← Cross-domain data marts
    │   │       └── enterprise_mart/
    │   │           ├── dim_unified_customer/
    │   │           └── fact_enterprise_revenue/
    │   └── Tables/
    └── [cross-domain notebooks]
```

## Domain Ownership Model

### Domain-Owned Layers
**Bronze**: Domain owns ingestion from sources
- Example: Sales domain owns Salesforce ingestion
- Location: `Sales_Dev/lh_sales/Files/bronze/salesforce/`

**Silver**: Domain owns cleaning and validation
- Example: Sales domain owns Salesforce transformations
- Location: `Sales_Dev/lh_sales/Files/silver/salesforce/`

**Gold (Domain)**: Domain-specific data marts
- Example: Sales domain owns sales-specific reports
- Location: `Sales_Dev/lh_sales/Files/gold/sales_mart/`
- Consumers: Sales team, sales dashboards

### Cross-Domain Layers
**Staging**: Intermediate work for cross-domain analysis
- Not consumer-facing
- Holds multi-step transformation outputs
- Location: `Enterprise_Prod/lh_enterprise/Files/staging/`
- Example: Joining Sales + Finance data before final mart

**Gold (Cross-Domain)**: Enterprise-wide data marts
- Combines multiple domains
- Consumer-facing for enterprise reporting
- Location: `Enterprise_Prod/lh_enterprise/Files/gold/enterprise_mart/`
- Example: Unified customer view (Sales + Finance + Support data)

## Lakehouse Folder Structure (No Schemas)

**IMPORTANT**: Fabric Lakehouses use **folders** for organization, NOT schemas like Databricks.

```
lh_sales/
├── Files/
│   ├── bronze/              ← Raw data organized by source
│   │   ├── salesforce/
│   │   │   ├── account/
│   │   │   │   └── [parquet/delta files]
│   │   │   └── opportunity/
│   │   │       └── [parquet/delta files]
│   │   └── sap/
│   │       └── customer/
│   │           └── [parquet/delta files]
│   │
│   ├── silver/              ← Cleaned data organized by source
│   │   ├── salesforce/
│   │   │   ├── account/
│   │   │   │   └── [delta files]
│   │   │   └── opportunity/
│   │   │       └── [delta files]
│   │   └── sap/
│   │       └── customer/
│   │           └── [delta files]
│   │
│   └── gold/                ← Business-ready data marts
│       └── sales_mart/      ← Data mart name
│           ├── dim_customer/
│           │   └── [delta files]
│           └── fact_sales/
│               └── [delta files]
│
└── Tables/                  ← Delta tables (references Files/)
    ├── bronze_salesforce_account
    ├── silver_salesforce_account
    └── gold_dim_customer
```

## Pipeline Activities

### Copy Activity
**When**: Simple data movement, built-in connectors

### Dataflow Gen2
**When**: Complex transformations, rate-limited APIs, Power Query

### Notebook
**When**: Complex Spark logic, business rules

## OneLake Optimization

```python
# Z-Ordering
spark.sql("OPTIMIZE table ZORDER BY (col1, col2)")

# Vacuum
spark.sql("VACUUM table RETAIN 168 HOURS")

# Statistics
spark.sql("ANALYZE TABLE table COMPUTE STATISTICS")
```

## Security

- Managed Identity for auth
- Azure Key Vault for secrets
- Workspace roles for access

## Monitoring

- Fabric monitoring workspace
- Pipeline run history
- Data Activator for alerts

## Best Practices

✅ Use OneLake
✅ Use Dataflow Gen2 for complex APIs
✅ Partition large tables
✅ Use managed identity
✅ Monitor CU consumption

❌ Don't use external storage
❌ Don't use SELECT *
❌ Don't skip optimization
```

---

#### fabric-pipelines

**File**: `.claude/skills/fabric/fabric-pipelines/SKILL.md`

```markdown
---
name: fabric-pipelines
description: Building Fabric Data Factory pipelines.
---

# Fabric Pipelines Skill

## Pipeline Structure

```json
{
  "name": "pl_name",
  "properties": {
    "activities": [...],
    "parameters": {...}
  }
}
```

## Activity Types

### Copy Activity
```json
{
  "name": "CopyData",
  "type": "Copy",
  "typeProperties": {
    "source": {"type": "SalesforceSource"},
    "sink": {"type": "DeltaSink"}
  },
  "policy": {
    "timeout": "01:00:00",
    "retry": 3,
    "retryIntervalInSeconds": 30
  }
}
```

### Notebook Activity
```json
{
  "name": "Transform",
  "type": "Notebook",
  "typeProperties": {
    "notebookPath": "/notebooks/transform",
    "parameters": {
      "run_date": "@pipeline().parameters.run_date"
    }
  }
}
```

### ForEach Loop
```json
{
  "name": "ForEachTable",
  "type": "ForEach",
  "typeProperties": {
    "items": "@pipeline().parameters.tableList",
    "isSequential": false,
    "activities": [...]
  }
}
```

## Parameters

```json
{
  "parameters": {
    "watermark": {
      "type": "String",
      "defaultValue": "2024-01-01"
    }
  }
}
```

## Error Handling

```json
{
  "policy": {
    "timeout": "01:00:00",
    "retry": 3,
    "retryIntervalInSeconds": 30
  }
}
```

## Scheduling

```json
{
  "name": "DailyTrigger",
  "properties": {
    "type": "ScheduleTrigger",
    "typeProperties": {
      "recurrence": {
        "frequency": "Day",
        "interval": 1,
        "startTime": "2024-01-01T02:00:00Z"
      }
    }
  }
}
```

## Common Patterns

### Incremental Load
```json
{
  "activities": [
    {"name": "GetWatermark", "type": "Lookup"},
    {
      "name": "CopyIncremental",
      "type": "Copy",
      "dependsOn": [{"activity": "GetWatermark"}]
    }
  ]
}
```

## Best Practices

✅ Use parameters
✅ Add error handling
✅ Log outputs
✅ Use appropriate timeouts
✅ Enable retry

❌ Don't hardcode
❌ Don't skip errors
❌ Don't use sequential ForEach for large lists
```

---

### Databricks-Specific Skills

#### databricks-architecture

**File**: `.claude/skills/databricks/databricks-architecture/SKILL.md`

```markdown
---
name: databricks-architecture
description: Databricks architecture patterns with Unity Catalog and Delta Lake.
---

# Databricks Architecture Skill

## Overview

Databricks = Unified data and AI platform
- Unity Catalog (governance)
- Delta Lake (ACID transactions)
- Workflows (orchestration)
- DLT (declarative ETL)
- Photon (query engine)

## Key Concepts

### Unity Catalog
- Three-level: `catalog.schema.table`
- Unified governance
- Fine-grained access
- Data lineage

### Delta Lake
- ACID transactions
- Time travel
- Schema enforcement
- Optimization

## Architecture Pattern

```
Source → Workflow → Bronze → DLT → Silver → Notebook → Gold
                   (catalog.bronze)  (catalog.silver)  (catalog.gold)
```

## Unity Catalog Organization

```
Account
├── production (catalog)
│   ├── bronze_salesforce (schema)
│   ├── silver_salesforce (schema)
│   └── gold_analytics (schema)
├── development (catalog)
└── test (catalog)
```

## Workflows vs DLT

**Use Workflows:**
- Multiple heterogeneous tasks
- Complex orchestration
- Mix of notebooks/SQL/Python

**Use DLT:**
- Pure data transformation
- Built-in quality checks
- Automatic lineage
- Streaming + batch

## Delta Optimization

```sql
-- Auto-optimize
ALTER TABLE table
SET TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Z-Ordering
OPTIMIZE table ZORDER BY (col1, col2)

-- Liquid Clustering
ALTER TABLE table CLUSTER BY (col1, col2)

-- Vacuum
VACUUM table RETAIN 168 HOURS
```

## Security

### RBAC
```sql
GRANT USE CATALOG ON CATALOG prod TO `engineers`;
GRANT SELECT ON TABLE prod.gold.dim_customer TO `analysts`;
```

### Secrets
```python
api_key = dbutils.secrets.get(scope="prod", key="api-key")
```

## Compute

**Serverless (Recommended)**:
- Instant startup
- No management
- Pay per use

**Classic**:
- More control
- Custom configs

## Monitoring

- Workflow run history
- DLT event log
- Spark UI
- Email/webhook notifications

## Best Practices

✅ Use Unity Catalog
✅ Use DLT for prod
✅ Use Serverless
✅ Enable auto-optimize
✅ Use Photon

❌ Don't use legacy Hive
❌ Don't skip expectations
❌ Don't hardcode secrets
```

---

#### delta-live-tables

**File**: `.claude/skills/databricks/delta-live-tables/SKILL.md`

```markdown
---
name: delta-live-tables
description: Building production DLT pipelines with expectations.
---

# Delta Live Tables Skill

## What is DLT?

Declarative framework for reliable pipelines.

**Benefits:**
- Declarative syntax
- Automatic management
- Built-in quality (expectations)
- Auto-scaling
- Automatic lineage
- Streaming + batch

## When to Use

✅ Production pipelines
✅ Medallion architecture
✅ Need quality checks
✅ Want lineage
✅ CDC scenarios

❌ Ad-hoc analysis
❌ ML training
❌ One-off transforms

## DLT Pipeline Example

```python
import dlt
from pyspark.sql.functions import *

# BRONZE
@dlt.table(name="bronze_account")
def bronze():
    return spark.readStream.format("cloudFiles").load("s3://landing/")

# SILVER with EXPECTATIONS
@dlt.table(name="silver_account")
@dlt.expect_or_drop("valid_id", "account_id IS NOT NULL")
@dlt.expect_or_drop("valid_name", "LENGTH(account_name) > 0")
@dlt.expect("valid_email", "email RLIKE '^[^@]+@[^@]+'")
def silver():
    return (
        dlt.read_stream("bronze_account")
        .select(
            col("account_id"),
            col("account_name"),
            sha2(col("email"), 256).alias("email_hash")
        )
    )

# GOLD
@dlt.table(name="gold_dim_customer")
@dlt.expect_or_drop("unique_id", "customer_id IS NOT NULL")
def gold():
    accounts = dlt.read("silver_account")
    contacts = dlt.read("silver_contact")
    return accounts.join(contacts, "account_id", "left")
```

## Expectations Types

### @dlt.expect()
Logs violations, doesn't drop
```python
@dlt.expect("valid_email", "email IS NOT NULL")
```

### @dlt.expect_or_drop()
Drops violating records
```python
@dlt.expect_or_drop("valid_id", "id IS NOT NULL")
```

### @dlt.expect_or_fail()
Fails pipeline on violation
```python
@dlt.expect_or_fail("critical", "critical_field IS NOT NULL")
```

## Streaming vs Batch

**Streaming:**
```python
def bronze():
    return spark.readStream.format("cloudFiles").load(path)
```

**Batch:**
```python
def bronze():
    return spark.read.format("parquet").load(path)
```

## CDC with DLT

```python
@dlt.table(name="target")
@dlt.expect_or_drop("valid_operation", "_change_type IN ('INSERT', 'UPDATE', 'DELETE')")
def apply_cdc():
    return (
        dlt.read_stream("cdc_source")
        .selectExpr("*", "_change_type")
    )

dlt.apply_changes(
    target="target",
    source="apply_cdc",
    keys=["id"],
    sequence_by="_commit_timestamp",
    apply_as_deletes=expr("_change_type = 'DELETE'"),
    except_column_list=["_change_type"]
)
```

## Best Practices

✅ Use expectations for quality
✅ Use streaming for real-time
✅ Use `expect_or_drop` for critical
✅ Monitor event log
✅ Version DLT pipelines

❌ Don't skip expectations
❌ Don't use complex transformations in DLT
❌ Don't forget to test expectations
```

---

## 📝 CLAUDE.md Template

**File**: `CLAUDE.md`

```markdown
# Data Platform Project - Team Knowledge

## Project Overview
Microsoft Fabric and Databricks data platform with medallion architecture.

## Supported Platforms
- **Primary**: Microsoft Fabric
- **Secondary**: Databricks
- **Shared**: Medallion architecture, SQL optimization

## Architectural Decisions
- OneLake for Fabric storage
- Unity Catalog for Databricks governance
- Bronze (raw) → Silver (cleaned) → Gold (modeled)
- PySpark for complex transformations
- SQL for simple transformations

## Naming Conventions
- Tables: `{layer}_{source}_{object}`
- Pipelines: `pl_{action}_{source}_{frequency}`
- Workflows: `wf_{action}_{source}_{frequency}`
- Notebooks: `{verb}_{source}_{layer}.py`

## Common Mistakes to Avoid
[Auto-updated by Learning Agent]

### Requirements & Planning
1. DON'T accept "all fields" - ask for specific list
2. DON'T assume "incremental" is clear - ask for watermark
3. ALWAYS clarify PII requirements upfront
4. ALWAYS ask which platform (Fabric vs Databricks)

### Architecture & Design
1. DON'T mix Fabric and Databricks patterns
2. DO use platform-native approaches
3. ALWAYS plan for API rate limits

### Implementation
1. DON'T place PII masking in Gold - do Bronze→Silver
2. DON'T forget metadata columns (_ingested_at, etc)
3. ALWAYS implement idempotency
4. ALWAYS add error handling with retry

### Testing
1. DON'T just test happy path
2. ALWAYS validate schema first
3. DO test with prod-like volumes

## Best Practices
[Auto-updated with proven patterns]

### Fabric-Specific
1. Use OneLake for all storage
2. Use Dataflow Gen2 for complex APIs
3. Partition large tables by date
4. Use managed identity for auth
5. Enable Fabric monitoring

### Databricks-Specific
1. Use Unity Catalog always
2. Use DLT for production pipelines
3. Use Serverless compute
4. Enable auto-optimization on tables
5. Use Photon engine

### Shared
1. Use parameters in pipelines/workflows
2. Log execution metrics
3. Test with small dataset first
4. Z-order on filtered columns
5. Partition by year-month

## Recent Learnings
[Auto-updated by Learning Agent after each PR]

### 2026-01-15: Example Entry

**Platform**: Fabric
**Story**: Add Salesforce as source

**What Went Well:**
- DataflowGen2 choice correct for API
- Z-ordering gave 40% performance boost
- Schema validation caught mismatches early

**Mistakes Made:**
- Initially tried Copy Activity (wrong choice)
- PII masking attempt in Gold layer (wrong!)
- Didn't account for rate limits

**Key Learnings:**
- Salesforce API: max 200 records/call
- PII masking: Bronze→Silver only
- Always ask specific fields, not "all"
- Incremental needs watermark column

**Templates Created:**
- api_with_rate_limiting.py

**Time Savings Next Time:**
- Est. 20min with rate-limit template
- 10min knowing DataflowGen2 upfront

## Performance Optimization Patterns
[Learned from production]

- Z-ordering: 30-50% improvement on filtered columns
- Partition by year-month for >1GB tables
- Liquid clustering for high cardinality (Databricks)
- Optimize after major loads

## Troubleshooting Guide
[Common issues and solutions]

### Pipeline Timeout
**Symptoms**: Fails after 30min
**Cause**: Large volume without partitioning
**Solution**: Add partition strategy
**Prevention**: Estimate volume in planning

### Schema Drift
**Symptoms**: Silver transform fails
**Cause**: Source changed schema
**Solution**: Update bronze and transform
**Prevention**: Schema validation in ingestion

### Rate Limiting
**Symptoms**: API calls fail
**Cause**: Exceeded API limits
**Solution**: Add batching and delays
**Prevention**: Check limits in planning

## Knowledge Base
- Fabric Docs: https://learn.microsoft.com/fabric
- Databricks Docs: https://docs.databricks.com
- Team Wiki: [internal link]
```

---

## 🔄 WORKFLOW: /develop-story

**File**: `.claude/commands/develop-story.md`

```markdown
---
name: develop-story
description: Main workflow - orchestrates full story from requirements to PR.
---

# Develop Story Workflow

## Usage
```bash
/develop-story "Add Salesforce as a source"
```

## Execution Flow

### PHASE 1: Requirements (5min - INTERACTIVE)
**Agent**: Requirements Analyst

1. Parse user story
2. Ask clarifying questions (INTERACTIVE LOOP):
   - Platform: Fabric or Databricks? ← CRITICAL
   - Source details
   - Field list (specific)
   - Load type (full/incremental)
   - Watermark column (if incremental)
   - PII data
   - Quality requirements
3. Create requirements.md
4. Create ADR-001.md

**Output**: requirements.md, ADR-001.md

---

### PHASE 2: Planning (15min - USER APPROVAL REQUIRED)
**Agent**: Data Architect

1. Read requirements.md
2. Detect platform (Fabric or Databricks)
3. Load platform-specific skills
4. Design architecture:
   - Medallion layers (Bronze/Silver/Gold)
   - Schemas for each layer
   - Platform-specific components:
     * Fabric: Pipelines, Lakehouse, OneLake
     * Databricks: Workflows/DLT, Unity Catalog
5. Create task breakdown with estimates
6. Generate design documents

**Output**: design.md, architecture.md, tasks.md

**USER APPROVAL CHECKPOINT**:
```
Present design to user
Show: architecture diagram, schemas, task list
Wait for: "approved" or "proceed"
If changes requested: iterate design
```

Only proceed after explicit approval.

---

### PHASE 3: Implementation (45min - AUTONOMOUS)
**Primary Agent**: Data Engineer (Fabric or Databricks based on platform)
**Support Agent**: DevOps Engineer

**DevOps**: Create feature branch
```bash
git checkout -b feature/[story-slug]
```

**Data Engineer**: Implement in order:

#### Task 1: Bronze Layer (15min)
- Create [Lakehouse/Catalog] tables
- Add metadata columns
- Test table creation

**DevOps**: Commit
```bash
git add sql/
git commit -m "feat: add bronze layer tables"
```

#### Task 2: Ingestion (20min)
**Fabric:**
- Create pipeline (Copy Activity or Dataflow Gen2)
- Configure source connector
- Add parameters
- Add error handling

**Databricks:**
- Create workflow or DLT pipeline
- Configure source
- Add parameters
- Add error handling

**DevOps**: Commit
```bash
git add pipelines/ # or workflows/
git commit -m "feat: add ingestion [pipeline/workflow]"
```

#### Task 3: Silver Transformation (20min)
- Create notebook
- Implement transformations:
  * Type conversions
  * PII masking
  * Data quality checks
  * Deduplication
- Implement SCD Type 2
- Add unit tests

**DevOps**: Commit
```bash
git add notebooks/
git commit -m "feat: add silver transformation"
```

#### Task 4: Gold Models (15min)
- Create notebook
- Implement dimensional modeling
- Add business calculations
- Optimize (Z-order, partition)

**DevOps**: Commit
```bash
git add notebooks/ sql/
git commit -m "feat: add gold models"
```

#### Task 5: Monitoring (10min)
- Create metadata tables
- Add logging
- Configure alerts

**DevOps**: Commit
```bash
git add sql/ config/
git commit -m "feat: add monitoring and logging"
```

**Output**: Pipelines/workflows, notebooks, SQL, tests

---

### PHASE 4: Documentation (Parallel with Phase 3)
**Agent**: Documentation Engineer

While implementation runs:

1. Generate data dictionary
2. Create pipeline/workflow docs
3. Build data lineage diagram
4. Write runbook
5. Update CLAUDE.md (preliminary)

**Output**: All docs in docs/ folder

---

### PHASE 5: Testing & Deployment (20min - AUTONOMOUS)
**QA Agent**: Testing
**DevOps Agent**: Deployment

#### Deploy to DEV
**Fabric:**
```python
fabric_api.deploy_to_workspace("dev", artifacts)
```

**Databricks:**
```bash
databricks bundle deploy --target dev
```

#### Run Test Suite
```python
pytest tests/ --platform=[fabric/databricks] -v

Tests:
1. Connection test
2. Schema validation
3. Data quality checks
4. [Pipeline/Workflow] execution E2E
5. Performance benchmarks
6. Data reconciliation
```

#### If Tests Fail:
1. QA analyzes failure
2. Data Engineer fixes
3. Re-run tests
4. Iterate until pass

#### If Tests Pass:
1. Generate test report
2. DevOps creates PR

**DevOps**: Final commit and PR
```bash
git add .
git commit -m "feat([source]): complete [source] ingestion

- Added bronze/silver/gold layers
- Implemented PII masking
- Added data quality checks
- Created monitoring
- All tests passing (15/15)

Closes #123"

# Create PR
gh pr create \
  --title "feat([source]): Add [source] as data source" \
  --body "[Auto-generated from design.md]" \
  --label "enhancement,data-source"
```

**Output**: Test results, PR created

---

### PHASE 6: Production Ready
**Status**: READY FOR MERGE

Checklist:
✓ All tests passing
✓ Documentation complete
✓ PR created
✓ Code in DEV environment
✓ Ready for review

---

### PHASE 7: Continuous Improvement (5min - OPTIONAL)
**Agent**: Learning Agent

**ASK USER**:
```
✓ Development complete! All tests passing, PR ready.

I noticed patterns during implementation that could help 
future stories. Would you like me to update agents/skills 
with these learnings?

Updates:
- Add common mistakes to relevant agents
- Update skills with new best practices
- Document lessons in CLAUDE.md
- Create reusable templates

Update agents with learnings? (yes/no)
```

#### If User Says YES:

1. **Analyze Work**:
   - Review all commits
   - Identify bugs and fixes
   - Extract patterns
   - Note performance metrics
   - Track requirement ambiguities

2. **Categorize Learnings**:
   - Architecture decisions
   - Code quality issues
   - Performance optimizations
   - Testing gaps
   - Process improvements

3. **Update Agents**:
   - Add "Common Mistakes to Avoid"
   - Add "Lessons Learned"
   - Update decision criteria

4. **Update Skills**:
   - Add new best practices
   - Create code templates
   - Document anti-patterns

5. **Update CLAUDE.md**:
   - Add timestamped learning entry
   - Document what worked/didn't
   - Note time savings for next time

6. **Commit Improvements**:
```bash
git add .claude/ CLAUDE.md
git commit -m "learn(agents): add [source] learnings

- Updated requirements-analyst: [specific improvement]
- Added [pattern] to [skill]
- Created reusable [template]
- Documented [best practice]

Prevents:
- [Issue 1]
- [Issue 2]"
```

7. **Report**:
```
✓ Agents and skills updated!

Updates Made:
- [Agent 1]: [Change]
- [Skill 1]: [Change]
- CLAUDE.md: Full learning entry

Future Benefits:
- Similar stories ~[X]min faster
- [Issue] prevented proactively
- [Pattern] correct from start
```

#### If User Says NO:
```
No problem! Skipping updates.
PR ready for review.
Run /improve-agents later if needed.
```

---

## Summary

**Total Time**: ~90 minutes
- Requirements: 5min
- Planning: 15min
- Implementation: 45min
- Testing: 20min
- Learning: 5min (optional)

**Result**:
- Production-ready code
- Complete documentation
- All tests passing
- PR ready for merge
- System improved for next story

**Next Steps**:
1. Review PR
2. Merge to main
3. Deploy to TEST
4. Deploy to PROD
```

---

## 🚀 IMPLEMENTATION CHECKLIST

Use this checklist when building the system:

### Phase 1: Foundation
- [ ] Create directory structure
- [ ] Create all 8 agent files
- [ ] Create shared skills (7 skills)
- [ ] Create Fabric skills (6 skills)
- [ ] Create Databricks skills (7 skills)
- [ ] Initialize CLAUDE.md
- [ ] Create /develop-story workflow
- [ ] Test with simple CSV source

### Phase 2: Platform Skills
- [ ] Complete Fabric architecture skill
- [ ] Complete Fabric pipelines skill
- [ ] Complete Databricks architecture skill
- [ ] Complete DLT skill
- [ ] Add templates to each skill
- [ ] Test platform routing

### Phase 3: Testing & Learning
- [ ] Implement test framework
- [ ] Create test templates
- [ ] Implement learning agent logic
- [ ] Test learning updates
- [ ] Test full workflow end-to-end

### Phase 4: Polish
- [ ] Add error handling
- [ ] Add progress tracking
- [ ] Improve user prompts
- [ ] Add examples to skills
- [ ] Document edge cases

### Phase 5: Production Ready
- [ ] Test with real source (Salesforce)
- [ ] Verify both platforms work
- [ ] Collect initial learnings
- [ ] Train team
- [ ] Monitor and improve

---

## 📊 SUCCESS METRICS

Track these to measure system effectiveness:

1. **Speed**: Time from story to PR
   - Target: <90 minutes
   - Track: Requirements, Planning, Implementation, Testing

2. **Quality**: Test pass rate
   - Target: >90% first run
   - Track: Tests passed/total

3. **Learning**: Improvements over time
   - Track: Time savings story-over-story
   - Track: Repeat mistakes (should decrease)

4. **Coverage**: Documentation completeness
   - Target: 100% auto-generated
   - Track: Docs created/required

5. **Platform**: Correct platform routing
   - Target: 100% accuracy
   - Track: Fabric/Databricks selection

---

## 🎯 READY TO BUILD!

This complete guide contains everything needed:
- 8 specialized agents
- 20 skills (7 shared, 6 Fabric, 7 Databricks)
- 1 main workflow
- Complete CLAUDE.md template
- Implementation checklist

**Start building with Claude Code:**
```bash
# Give this file to Claude Code
claude --file COMPLETE_IMPLEMENTATION_GUIDE.md

# First command
"Build the complete directory structure and all agent files"
```

**System will evolve:**
- Agents learn from each story
- Skills grow with templates
- CLAUDE.md accumulates wisdom
- Time-to-delivery decreases

Good luck! 🚀