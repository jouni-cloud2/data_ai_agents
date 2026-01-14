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
   - Platform: Fabric or Databricks? <- CRITICAL
   - If Fabric: Which business domain? (Sales, Finance, HR, etc.)
   - Source details
   - Field list (specific)
   - Load type (full/incremental)
   - Watermark column (if incremental)
   - PII data
   - Quality requirements
3. Create requirements.md
4. Create ADR-001.md

**Output**: docs/requirements.md, docs/ADR-001.md

---

### PHASE 2: Planning (15min - USER APPROVAL REQUIRED)
**Agent**: Data Architect

1. Read requirements.md
2. Detect platform (Fabric or Databricks)
3. Load platform-specific skills
4. Design architecture:
   - Medallion layers (Bronze/Silver/Gold)
   - Schemas/folders for each layer
   - Platform-specific components:
     * Fabric: Pipelines, Lakehouse, OneLake folders
     * Databricks: Workflows/DLT, Unity Catalog schemas
5. Create task breakdown with estimates
6. Generate design documents

**Output**: docs/design.md, docs/architecture.md, docs/tasks.md

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
- Create [Lakehouse folders/Catalog schemas]
- Create Bronze tables with metadata columns
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
- All tests passing
- Documentation complete
- PR created
- Code in DEV environment
- Ready for review

---

### PHASE 7: Continuous Improvement (5min - OPTIONAL)
**Agent**: Learning Agent

**ASK USER**:
```
Development complete! All tests passing, PR ready.

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
Agents and skills updated!

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
