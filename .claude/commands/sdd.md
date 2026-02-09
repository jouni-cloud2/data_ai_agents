---
name: sdd
description: Spec-Driven Development - gated agentic pipeline for implementing stories, bugs, and ideas with full traceability.
---

# Spec-Driven Development (SDD)

A gated workflow for implementing changes with full traceability. Takes a request through complexity assessment, spec authoring, implementation, and documentation.

## Usage

```bash
/sdd "Add Salesforce as a data source"
/sdd "Fix null pointer exception in customer transform"
/sdd "Refactor pipeline error handling"
```

## Behavior

When invoked, Claude acts as the **Spec Authoring Agent** and:

1. **Detects the environment** - Identifies platform (Fabric, Databricks, etc.)
2. **Analyzes the input** - Understands the request, identifies scope and complexity
3. **Explores the codebase** - Finds relevant files, patterns, and dependencies
4. **Suggests workflow** - Recommends Quick Fix or Full SDD based on complexity
5. **Gate #1**: User selects workflow path

---

## Phase 0: Environment Detection

**ALWAYS run this first before any implementation work.**

### 0.1 Detect Current Location

```bash
# Check if we're in a project subrepo
pwd
ls -la  # Look for project indicators
```

### 0.2 Detect Platform

| Indicator | Platform |
|-----------|----------|
| `*.Notebook/` folders | Microsoft Fabric |
| `databricks.yml` or `.databricks/` | Databricks |
| `snowflake.yml` or `snowflake/` | Snowflake |
| `dbt_project.yml` | dbt (check underlying platform) |

```bash
# Fabric check
find . -maxdepth 3 -name "*.Notebook" -type d 2>/dev/null | head -1

# Databricks check
ls databricks.yml .databricks/ 2>/dev/null

# Terraform check (for infrastructure)
ls terraform/*.tf 2>/dev/null
```

### 0.3 Load Platform Documentation

Based on detected platform, read relevant docs:

**For Microsoft Fabric:**
- `docs/platforms/fabric/notebook-standards.md` - Development patterns
- `docs/platforms/fabric/pipeline-patterns.md` - Orchestration
- `docs/platforms/fabric/onelake-patterns.md` - Storage patterns
- `docs/platforms/fabric/pitfalls.md` - Common mistakes to avoid
- `docs/platforms/fabric/workspace-patterns.md` - Organization

**For Azure Infrastructure:**
- `docs/platforms/azure/` - Azure patterns
- `terraform/modules/azure/` - Terraform modules

**For Databricks:**
- `docs/platforms/databricks/` - Databricks patterns (when available)

**Always load these:**
- `docs/principles/medallion-architecture.md` - Bronze/Silver/Gold
- `docs/principles/data-governance.md` - Classification, ownership
- `docs/principles/data-quality.md` - Validation rules

### 0.4 Confirm Environment

```markdown
## Environment Detection

**Working Directory:** [path]
**Platform:** [Fabric/Databricks/Unknown]
**Project:** [project name from path]

**Loaded Documentation:**
- [List of loaded platform docs]

Is this correct? (yes/change)
```

---

## Phase 1: Complexity Assessment

Analyze the request and categorize:

| Category | Indicators | Suggested Workflow |
|----------|------------|-------------------|
| **Trivial** | Typo, single-line fix, config change | Quick Fix |
| **Simple** | Small bug, minor tweak, clear scope | Quick Fix |
| **Medium** | New endpoint, component, multi-file change | Full SDD |
| **Complex** | New feature, architectural change, cross-cutting concern | Full SDD |

### Assessment Process

1. **Parse the request** - Extract key requirements
2. **Search codebase** - Find related files, patterns, existing implementations
3. **Check platform docs** - Look for relevant patterns in `docs/platforms/{platform}/`
4. **Estimate scope** - Count files affected, identify dependencies
5. **Check for precedents** - Look for similar past implementations

### Present to User

```markdown
## Complexity Assessment

**Request**: [User's request]
**Platform**: [Detected platform]

**Analysis**:
- Files likely affected: [count]
- Key dependencies: [list]
- Similar patterns found: [yes/no - where]
- Platform-specific considerations: [list]
- Estimated complexity: [Trivial/Simple/Medium/Complex]

**Recommendation**: [Quick Fix / Full SDD]

**Rationale**: [Why this recommendation]

---

Which workflow would you like to use?
1. Quick Fix - Direct implementation with minimal ceremony
2. Full SDD - Spec authoring, implementation, documentation
```

---

## Gate #1: Workflow Selection

**Wait for user to select**:
- "Quick Fix" or "1" → Proceed to [Quick Fix Workflow](../workflows/quick-fix.md)
- "Full SDD" or "2" → Proceed to [Full SDD Workflow](../workflows/full-sdd.md)

---

## What Happens After Gate #1

### Quick Fix Path

```
Gate #1: Quick Fix Selected
           ↓
    Create Feature Branch
           ↓
    Direct Implementation (platform-aware)
           ↓
    Validate Changes
           ↓
    Gate #2: Approval
           ↓
    Merge Decision
```

See [quick-fix.md](../workflows/quick-fix.md) for details.

### Full SDD Path

```
Gate #1: Full SDD Selected
           ↓
    Spec Authoring (gap-filling questions)
           ↓
    Create Feature Branch
           ↓
    Gate #2: Spec Approval
           ↓
    Implementation (platform-aware)
           ↓
    Verification
           ↓
    Gate #3: Implementation Approval
           ↓
    Documentation Update
           ↓
    Gate #4: Merge Decision
```

See [full-sdd.md](../workflows/full-sdd.md) for details.

---

## Platform-Specific Implementation

### Microsoft Fabric

When implementing on Fabric, follow:

| Task | Reference |
|------|-----------|
| Notebook development | `docs/platforms/fabric/notebook-standards.md` |
| Pipeline design | `docs/platforms/fabric/pipeline-patterns.md` |
| Storage patterns | `docs/platforms/fabric/onelake-patterns.md` |
| Workspace organization | `docs/platforms/fabric/workspace-patterns.md` |
| Common mistakes | `docs/platforms/fabric/pitfalls.md` |

Key patterns:
- Use medallion architecture (Bronze → Silver → Gold)
- Follow naming conventions: `{layer}_{source}_{entity}`
- Implement incremental loads where possible
- Add data quality checks at Silver layer

### Azure Infrastructure

When implementing Azure infrastructure:

| Task | Reference |
|------|-----------|
| Resource modules | `terraform/modules/azure/` |
| Naming conventions | `docs/platforms/azure/` |
| Security patterns | `docs/principles/security-privacy.md` |

### Databricks

When implementing on Databricks:

| Task | Reference |
|------|-----------|
| Development patterns | `docs/platforms/databricks/` |
| Unity Catalog | Platform docs (when available) |

---

## Documentation Rules

### Where Documentation Goes

| Documentation Type | Location | Repo |
|-------------------|----------|------|
| Data catalog entries | `docs/catalog/{domain}/` | **Project subrepo** |
| Source integrations | `docs/sources/` | **Project subrepo** |
| Architecture decisions (ADRs) | `docs/architecture/decisions/` | **Project subrepo** |
| Runbooks | `docs/runbooks/` | **Project subrepo** |
| SDD specs | `docs/specs/` | **Project subrepo** |
| Platform patterns | `docs/platforms/` | **Parent repo (data_ai_agents)** |
| Principles | `docs/principles/` | **Parent repo (data_ai_agents)** |

**NEVER put project-specific documentation in the parent repo.**

### Documentation Templates

Use templates from `docs/templates/`:
- `catalog-entry.md` - For new tables/datasets
- `source-integration.md` - For new source systems
- `adr.md` - For architecture decisions
- `runbook.md` - For operational procedures

---

## Final Step: Update AI (Both Workflows)

After merge decision, ask:

```markdown
Development complete!

Would you like me to capture learnings from this work?

**Generalizable learnings** → Update parent repo (docs/, .claude/)
**Project-specific learnings** → Update project docs only

Updates may include:
- Common mistakes to avoid (generalized)
- New patterns discovered (generalized)
- Project-specific configurations (project only)

Capture learnings? (yes/no)
```

### If User Says YES

1. **Analyze the work**:
   - Review changes made
   - Identify any issues encountered
   - Extract reusable patterns
   - Separate generalizable vs project-specific learnings

2. **For generalizable learnings** (update parent repo):
   - Add to `docs/platforms/{platform}/pitfalls.md` if new pitfall
   - Add to `docs/patterns/` if new reusable pattern
   - Update `docs/principles/` if principle clarification needed

3. **For project-specific learnings** (update project repo):
   - Update project's architecture docs
   - Add to project's runbooks

4. **Commit improvements**:
```bash
# Parent repo (if generalizable)
cd ../..  # Back to data_ai_agents root
git add docs/
git commit -m "learn: capture learnings from [project]/[spec-id]

- [Generalized learning 1]
- [Generalized learning 2]"

# Project repo (if project-specific)
cd projects/{project}
git add docs/
git commit -m "docs: capture project learnings from [spec-id]

- [Project-specific learning 1]"
```

### If User Says NO

```
No problem! Skipping AI updates.
Work complete.
```

---

## Spec File Location

Specs are stored in the **project subrepo**'s `docs/specs/` during development:

```
projects/{project}/
└── docs/
    └── specs/{spec-id}/
        ├── spec.md           # BDD specification (Full SDD only)
        └── implementation.md # Implementation notes (created during impl)
```

### Spec ID Convention

Format: `SDD-YYYYMMDD-short-slug`

Examples:
- `SDD-20260209-salesforce-source`
- `SDD-20260209-fix-null-pointer`
- `SDD-20260209-refactor-error-handling`

---

## Quick Reference

| Gate | Decision Point | Options |
|------|---------------|---------|
| #1 | Workflow Selection | Quick Fix / Full SDD |
| #2 | Spec Approval (Full SDD) | Approve / Request Changes |
| #3 | Implementation Approval | Approve / Request Changes |
| #4 | Merge Decision | Merge / Hold |

| Platform | Primary Docs |
|----------|-------------|
| Fabric | `docs/platforms/fabric/` |
| Databricks | `docs/platforms/databricks/` |
| Azure (Terraform) | `docs/platforms/azure/`, `terraform/modules/azure/` |

| Learning Type | Goes To |
|--------------|---------|
| Generalizable | Parent repo (`docs/`, `.claude/`) |
| Project-specific | Project subrepo (`docs/`) |
