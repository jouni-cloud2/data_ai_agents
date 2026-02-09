---
name: document
description: Maintain project documentation holistically - audit, create, and update docs following established rules.
---

# Documentation Maintenance Command

Maintains documentation as a cohesive system. Understands the separation between **parent repo** (generic knowledge) and **project subrepo** (project-specific docs).

## Usage

```bash
/document                          # Full documentation audit
/document audit                    # Same as above
/document <domain>                 # Audit specific domain (sales, hr, etc.)
/document <table_name>             # Document specific table
/document recent                   # Document recent changes (git diff)
/document catalog                  # Audit data catalog only
/document adrs                     # Audit ADRs only
/document sources                  # Audit source documentation only
/document runbooks                 # Audit runbooks only
/document "<topic>"                # Document a specific topic or concept
/document improve "<doc_path>"     # Improve specific existing documentation
```

### Examples

```bash
# Audit modes
/document                          # Full audit of project docs
/document sales                    # Audit Sales domain docs
/document hr                       # Audit HR domain docs

# Create specific documentation
/document bronze_hubspot_contacts  # Document a specific table
/document "OAuth2 token refresh"   # Document a concept/process
/document "error handling patterns" # Document a technical topic

# Improve existing docs
/document improve docs/sources/hubspot.md  # Enhance a specific doc
/document improve "runbooks"       # Improve all runbooks
```

## Behavior

When invoked, Claude acts as the **Documentation Agent** and maintains documentation following the rules in `docs/DOCUMENTATION-PLAN.md`.

---

## Critical: Parent vs Project Separation

### Documentation Locations

| Documentation Type | Location | Repo | Example |
|-------------------|----------|------|---------|
| Platform patterns | `docs/platforms/{platform}/` | **Parent (data_ai_agents)** | Fabric notebook standards |
| Principles | `docs/principles/` | **Parent** | Medallion architecture |
| Reusable patterns | `docs/patterns/` | **Parent** | API ingestion patterns |
| Templates | `docs/templates/` | **Parent** | Catalog entry template |
| Data catalog | `docs/catalog/` | **Project subrepo** | bronze_hubspot_companies.md |
| Source docs | `docs/sources/` | **Project** | hubspot.md |
| ADRs | `docs/architecture/decisions/` | **Project** | ADR-0001-domain-model.md |
| Runbooks | `docs/runbooks/` | **Project** | pipeline-failures.md |
| Specs | `docs/specs/` | **Project** | SDD-20260209-xyz/ |

### Rules

1. **NEVER create project-specific documentation in the parent repo**
2. **Reference parent docs from project docs** (don't duplicate)
3. **Generalizable patterns** found in projects → suggest adding to parent
4. **Project-specific details** → always in project subrepo

---

## Phase 0: Environment Detection

### 0.1 Detect Location

```bash
# Check current location
pwd

# Are we in a project subrepo?
# projects/{project-name}/ → Project context
# data_ai_agents/ → Parent repo context
```

### 0.2 Determine Context

```markdown
## Documentation Context

**Current Location:** [path]
**Context:** [Parent Repo / Project: {name}]

Based on your location, I will:
- [Parent] Audit/update platform patterns and principles
- [Project] Audit/update project-specific documentation

Is this the correct context? (yes/change)
```

### 0.3 Load Documentation Rules

Read these files to understand the documentation system:

```
docs/DOCUMENTATION-PLAN.md          # Master plan, templates, rules
```

---

## Invocation Modes

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Audit** | `/document`, `/document audit`, `/document <scope>` | Full discovery → analysis → present → action |
| **Create** | `/document <table_name>`, `/document "<topic>"` | Skip to creation, use discovery for context |
| **Improve** | `/document improve <target>` | Analyze existing doc and enhance it |

---

## Phase 1: Discovery

Understand the current state of documentation vs reality.

### 1.1 Scan for Assets (Project Context)

**Tables (from platform-specific locations):**

For Fabric:
```bash
grep -r "saveAsTable\|CREATE TABLE\|bronze_\|silver_\|gold_\|dim_\|fact_" . --include="*.py" --include="*.sql"
find . -name "*.Notebook" -type d
```

For Databricks:
```bash
grep -r "spark.table\|CREATE TABLE" . --include="*.py" --include="*.sql"
```

**Source integrations:**
```bash
grep -r "api\|endpoint\|connection" . --include="*.py" --include="*.json"
```

**Recent changes (if /document recent):**
```bash
git diff --name-only HEAD~10
git log --oneline -20
```

### 1.2 Scan Existing Documentation

**Project documentation (in project subrepo):**
```bash
find docs/catalog -name "*.md" -not -name "README.md" 2>/dev/null
find docs/architecture/decisions -name "ADR-*.md" 2>/dev/null
find docs/sources -name "*.md" -not -name "README.md" 2>/dev/null
find docs/runbooks -name "*.md" -not -name "README.md" 2>/dev/null
```

### 1.3 Build Gap Analysis

| Category | Exists in Code | Documented | Gap |
|----------|---------------|------------|-----|
| Bronze tables | [list] | [list] | [missing] |
| Silver tables | [list] | [list] | [missing] |
| Gold tables | [list] | [list] | [missing] |
| Source integrations | [list] | [list] | [missing] |
| Key decisions | [list] | [list] | [missing] |

---

## Phase 2: Analysis

Evaluate documentation quality and identify issues.

### 2.1 Check Completeness

For each existing doc, verify required fields from templates:

**Catalog entries must have:**
- [ ] Name, Domain, Layer
- [ ] Purpose (business value)
- [ ] Owner, Steward
- [ ] Data Classification
- [ ] Retention Policy
- [ ] Schema with column descriptions
- [ ] Lineage (upstream/downstream)

**ADRs must have:**
- [ ] Status (Proposed/Accepted/Deprecated/Superseded)
- [ ] Context
- [ ] Decision Drivers
- [ ] Considered Options
- [ ] Decision Outcome
- [ ] Consequences

**Source docs must have:**
- [ ] Overview (system, vendor, domains)
- [ ] Entities table
- [ ] Authentication setup
- [ ] API details

### 2.2 Check Consistency

- [ ] Naming follows conventions (`{layer}_{source}_{entity}.md`)
- [ ] Cross-references are valid (no broken links)
- [ ] References to parent docs use relative paths (`../../docs/principles/...`)
- [ ] Indexes are up to date

### 2.3 Prioritize Issues

| Priority | Issue Type | Action |
|----------|-----------|--------|
| **Critical** | Missing Gold table docs | Create immediately |
| **High** | Missing source docs | Create before next source work |
| **Medium** | Incomplete catalog entries | Fill in missing fields |
| **Low** | Index out of date | Update during this run |

---

## Phase 3: Present Findings

```markdown
## Documentation Audit Results

**Context:** [Parent Repo / Project: {name}]

### Summary
- **Documented**: X of Y tables (Z%)
- **Complete**: A of X documented tables have all required fields
- **ADRs**: B decisions documented
- **Sources**: C of D sources documented

### Critical Gaps (Must Fix)

| Asset | Type | Issue |
|-------|------|-------|
| gold_dim_customer | Gold Table | Not documented |
| ... | ... | ... |

### Incomplete Documentation

| Document | Missing Fields |
|----------|---------------|
| docs/catalog/sales/silver_companies.md | Schema, Lineage |
| ... | ... |

### Potential Parent Repo Updates

These patterns could be generalized:
- [Pattern 1] - Consider adding to `docs/patterns/`
- [Pitfall 1] - Consider adding to `docs/platforms/{platform}/pitfalls.md`

### Recommendations

1. [Priority action 1]
2. [Priority action 2]

---

How would you like to proceed?
1. **Fix all** - Create missing docs, update incomplete ones
2. **Critical only** - Only address critical gaps
3. **Select items** - Choose specific items to fix
4. **Export report** - Save findings to docs/audit-report.md
```

---

## Phase 4: Action

### 4.1 Creating New Catalog Entries

For each missing table:

1. **Gather information automatically:**
   - Read the notebook/code that creates the table
   - Extract schema from code
   - Identify upstream tables from code
   - Determine domain from location

2. **Ask user for governance fields:**
   ```markdown
   Creating documentation for: gold_dim_customer

   I've extracted technical details. Please provide:
   - Owner (business owner):
   - Steward (data steward):
   - Classification (Public/Internal/Confidential/Restricted):
   - Purpose (business value in 1-2 sentences):
   ```

3. **Generate the document** using template from `docs/templates/catalog-entry.md`

4. **Save to correct location:** `docs/catalog/{domain}/{layer}_{source}_{entity}.md`

5. **Add reference to parent principles:**
   ```markdown
   ## Governance

   See [Data Governance Principles](../../../docs/principles/data-governance.md) for classification details.
   ```

### 4.2 Creating ADRs

Use `/architect` command for architecture decisions. The `/document` command will:

1. Check if ADR exists for detected decisions
2. Suggest running `/architect` if architectural decisions need documentation
3. Update ADR index after creation

### 4.3 Updating Incomplete Docs

1. **Read the existing doc**
2. **Identify missing fields**
3. **Attempt to auto-fill** from code analysis
4. **Ask user for remaining fields**
5. **Update the document**
6. **Update Last Updated date**

### 4.4 Updating Indexes

After all changes:

1. **Update `docs/catalog/README.md`** - coverage statistics
2. **Update `docs/architecture/decisions/README.md`** - ADR table
3. **Update `docs/sources/README.md`** - source status

---

## Phase 5: Verification

### 5.1 Validate Changes

```bash
# Check all markdown files are valid
find docs -name "*.md" -exec head -1 {} \;

# Check for broken internal links
grep -r "\[.*\](.*\.md)" docs/ | head -20
```

### 5.2 Cross-Reference Check

Ensure new docs:
- Are referenced from appropriate indexes
- Reference their upstream/downstream dependencies
- Link to parent repo docs where appropriate (principles, patterns)
- Use consistent terminology

### 5.3 Present Summary

```markdown
## Documentation Update Complete

### Changes Made

| Action | File | Description |
|--------|------|-------------|
| Created | docs/catalog/sales/gold_dim_customer.md | New catalog entry |
| Updated | docs/catalog/README.md | Coverage stats |
| Updated | docs/architecture/decisions/README.md | Added ADR-0003 |

### Documentation Status

| Category | Before | After |
|----------|--------|-------|
| Catalog coverage | 45% | 78% |
| Complete entries | 12 | 18 |
| ADRs | 2 | 4 |

### Remaining Gaps

[List any gaps not addressed in this run]

### Parent Repo Suggestions

If any generalizable patterns were found, suggest:
- Run `/improve-ai` to add pattern to parent repo
```

---

## Topic-Based Documentation

When invoked with a quoted topic (`/document "topic"`):

1. **Understand the topic** - What is the user asking to document?
2. **Determine location** based on topic type:

| Topic Type | Location |
|------------|----------|
| Architecture concept | Project `docs/architecture/` or ADR |
| Technical pattern (project-specific) | Project `docs/` |
| Technical pattern (generalizable) | Suggest parent `docs/patterns/` |
| Process/procedure | Project `docs/runbooks/` |
| Data asset | Project `docs/catalog/` |
| Source-specific | Project `docs/sources/` |

3. **Present options** to user with rationale
4. **Create documentation** following appropriate template

---

## Improve Existing Documentation

When invoked with `improve` (`/document improve <target>`):

1. **Read the target documentation**
2. **Analyze for improvements:**
   - Missing required fields (per templates)
   - Outdated information (compare to code)
   - Missing cross-references
   - Inconsistent terminology
   - Missing examples
3. **Present improvement plan**
4. **Apply selected improvements**
5. **Update Last Updated timestamp**

---

## Integration with Other Commands

| After | Use |
|-------|-----|
| `/sdd` | `/document` to document new assets |
| `/architect` | `/document` to update architecture docs |
| Finding patterns | `/improve-ai` to add to parent repo |

---

## Templates Reference

Templates are in the **parent repo** at `docs/templates/`:

- **Catalog Entry Template** - For tables and datasets
- **ADR Template (MADR)** - For architectural decisions
- **Source Integration Template** - For source systems
- **Runbook Template** - For operational procedures

When creating docs, copy structure from templates and fill in values.

---

## Quick Reference

| Command | Scope | Location |
|---------|-------|----------|
| `/document` | Full audit | Project docs |
| `/document sales` | Domain | Project `docs/catalog/sales/` |
| `/document bronze_hubspot_contacts` | Single table | Project `docs/catalog/` |
| `/document recent` | Git changes | Project docs |
| `/document catalog` | Catalog only | Project `docs/catalog/` |
| `/document adrs` | ADRs only | Project `docs/architecture/decisions/` |
| `/document sources` | Sources only | Project `docs/sources/` |
| `/document runbooks` | Runbooks only | Project `docs/runbooks/` |
| `/document "topic"` | Topic | Determined by topic type |
| `/document improve <path>` | Specific doc | As specified |

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Catalog | `{layer}_{source}_{entity}.md` | `bronze_hubspot_companies.md` |
| ADR | `ADR-{NNNN}-{slug}.md` | `ADR-0001-domain-structure.md` |
| Source | `{source}.md` | `hubspot.md` |
| Runbook | `{topic}.md` | `pipeline-failures.md` |
