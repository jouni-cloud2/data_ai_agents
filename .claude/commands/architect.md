---
name: architect
description: Architecture guidance - guide through decisions, answer questions, plan features, review architecture.
---

# Architecture Command

Guides architecture decisions and planning for data platforms. Adapts to your needs - from initial setup to ongoing guidance.

## Usage

```bash
/architect                           # Start architecture session
/architect decisions                 # Review/update existing decisions
/architect "topic"                   # Get guidance on specific topic
/architect plan "feature"            # Plan architecture for new feature
/architect review                    # Review current architecture for issues
```

## Behavior

When invoked, Claude acts as the **Architecture Agent** and adapts based on context.

---

## Phase 1: Environment Detection

Before any architecture work, detect the environment:

### 1.1 Detect Platform

```bash
# Check for platform indicators
ls -la  # Look for:
# - *.Notebook/ folders → Microsoft Fabric
# - databricks.yml or .databricks/ → Databricks
# - snowflake/ → Snowflake
# - terraform/*.tf → Check provider blocks for cloud
```

### 1.2 Detect Project Context

```bash
# Check if in a project subrepo
pwd  # Should be in projects/{project-name}/

# Check for existing architecture decisions
ls docs/architecture/decisions/ 2>/dev/null
```

### 1.3 Load Platform Knowledge

Based on detected platform, read:
- `docs/platforms/{platform}/` - Platform-specific patterns
- `docs/principles/` - Well-architected principles
- `docs/patterns/` - Reusable patterns

---

## Phase 2: Determine Mode

Based on invocation and context:

| Invocation | Context | Mode |
|------------|---------|------|
| `/architect` | No existing ADRs | **New Project Setup** |
| `/architect` | Has ADRs | **Architecture Overview** |
| `/architect decisions` | Any | **Decision Review** |
| `/architect "topic"` | Any | **Topic Guidance** |
| `/architect plan "feature"` | Any | **Feature Planning** |
| `/architect review` | Has implementation | **Architecture Review** |

---

## Mode: New Project Setup

Guide through foundational architecture decisions.

### Present Introduction

```markdown
## Architecture Session

I'll guide you through key architecture decisions for your data platform.

**Detected Environment:**
- Platform: [Fabric/Databricks/Unknown]
- Cloud: [Azure/AWS/GCP]
- Project: [project-name]

**What would you like to focus on?**

1. **Full Setup** - Walk through all major decisions
2. **Quick Start** - Just the essentials to begin
3. **Specific Area** - Focus on one decision area

Or describe what you need:
```

### Decision Areas (Adaptive)

Only go deep on areas the user selects:

| Area | Key Questions | Output |
|------|---------------|--------|
| **Domain Model** | How many domains? Ownership model? | ADR-0001 |
| **Environment Strategy** | Dev/Test/Prod? Promotion flow? | ADR-0002 |
| **Data Governance** | Classifications? PII handling? Lineage? | ADR-0003 |
| **Security Model** | Access control? Service principals? | ADR-0004 |
| **Medallion Design** | Layer boundaries? Transformation rules? | ADR-0005 |
| **Infrastructure** | Terraform? CI/CD? Monitoring? | ADR-0006 |

### For Each Decision Area

1. **Present context** from `docs/principles/`
2. **Show platform-specific options** from `docs/platforms/{platform}/`
3. **Ask clarifying questions** to understand constraints
4. **Present recommendation** with rationale
5. **Capture decision** as ADR

Example dialog:

```markdown
## Domain Model

Based on [Well-Architected Principles](docs/principles/well-architected.md),
you have several options for organizing data domains:

**Option A: Domain-per-Workspace**
- Each business domain (Sales, HR, Finance) gets its own workspace
- Clear ownership and access control
- Best for: Large organizations, strict data governance

**Option B: Layer-per-Workspace**
- Bronze/Silver/Gold each in separate workspace
- Simpler cross-domain queries
- Best for: Smaller teams, shared data

**Option C: Hybrid**
- Production domains separate, dev/test shared
- Balance of isolation and efficiency

**Questions:**
1. How many distinct business domains do you have?
2. Do domains need strict data isolation?
3. What's your team size per domain?
```

---

## Mode: Architecture Overview

When project has existing ADRs:

```markdown
## Architecture Overview

**Project:** [project-name]
**Platform:** [Fabric/Databricks]

### Current Decisions

| ADR | Status | Summary |
|-----|--------|---------|
| ADR-0001 | Accepted | Domain-per-workspace model |
| ADR-0002 | Accepted | Three environments (Dev/Test/Prod) |
| ... | ... | ... |

### Architecture Summary

[Generated from ADRs - domain model, data flow, key patterns]

---

What would you like to do?
1. **Review a decision** - Deep dive into specific ADR
2. **Update a decision** - Modify or supersede an ADR
3. **Add new decision** - Document a new architectural choice
4. **Ask a question** - Get guidance based on current architecture
```

---

## Mode: Topic Guidance

For `/architect "topic"`:

1. **Understand the question**
2. **Check existing ADRs** for relevant context
3. **Load relevant principles** from `docs/principles/`
4. **Load platform patterns** from `docs/platforms/{platform}/`
5. **Provide guidance** with references

```markdown
## Architecture Guidance: {topic}

### Current Context
[Summary of relevant existing decisions]

### Principles
[Relevant principles from docs/principles/]

### Platform Guidance
[Specific guidance for {platform}]

### Recommendation
[Actionable guidance]

### Next Steps
- [ ] [Action item 1]
- [ ] [Action item 2]

Would you like me to create an ADR for this decision?
```

---

## Mode: Feature Planning

For `/architect plan "feature"`:

1. **Understand the feature**
2. **Check architectural fit** against existing ADRs
3. **Identify impacted areas** (domains, layers, infrastructure)
4. **Propose implementation approach**
5. **Optionally create ADR** for significant decisions

```markdown
## Architecture Plan: {feature}

### Feature Understanding
[Summary of what needs to be built]

### Architectural Fit
| Decision | Impact | Notes |
|----------|--------|-------|
| ADR-0001 (Domains) | [Fits/Needs update] | [Details] |
| ADR-0003 (Governance) | [Fits/Needs update] | [Details] |

### Proposed Approach

**Data Flow:**
```
[Source] → Bronze → Silver → Gold → [Consumer]
```

**Components:**
1. [Component 1] - [Purpose]
2. [Component 2] - [Purpose]

**Platform-Specific:**
[Fabric/Databricks specific implementation notes]

### Questions to Resolve
1. [Question 1]
2. [Question 2]

### Ready for SDD?
Once questions are resolved, use `/sdd "{feature}"` to implement.
```

---

## Mode: Architecture Review

For `/architect review`:

1. **Scan implementation** (notebooks, configs, terraform)
2. **Compare against ADRs** and principles
3. **Identify deviations** or issues
4. **Recommend improvements**

```markdown
## Architecture Review

### Compliance Summary

| Area | Status | Issues |
|------|--------|--------|
| Domain Model | ✅ Compliant | - |
| Data Governance | ⚠️ Issues | Missing classifications |
| Security | ✅ Compliant | - |
| Medallion | ⚠️ Issues | Silver layer mixing concerns |

### Issues Found

#### Issue 1: Missing Data Classifications
**Location:** `bronze_*` tables
**ADR:** ADR-0003
**Problem:** Tables missing classification metadata
**Recommendation:** Add classification to catalog entries

#### Issue 2: Silver Layer Mixing
**Location:** `silver_customer_enriched`
**Principle:** [Medallion Architecture](docs/principles/medallion-architecture.md)
**Problem:** Silver table contains Gold-level aggregations
**Recommendation:** Move aggregations to Gold layer

### Recommendations

1. [Priority 1 action]
2. [Priority 2 action]

Would you like me to create tasks for these issues?
```

---

## Output: Architecture Documentation

All architecture work outputs to the **project subrepo**:

```
projects/{project}/
└── docs/
    └── architecture/
        ├── README.md              # Architecture overview (auto-generated)
        └── decisions/
            ├── README.md          # ADR index
            ├── ADR-0001-domain-model.md
            ├── ADR-0002-environments.md
            └── ...
```

### ADR Template

Use MADR format from `docs/templates/adr.md`:

```markdown
# ADR-{NNNN}: {Title}

## Status
{Proposed | Accepted | Deprecated | Superseded by ADR-XXXX}

## Context
{What is the issue we're addressing?}

## Decision Drivers
- {Driver 1}
- {Driver 2}

## Considered Options
1. {Option 1}
2. {Option 2}

## Decision Outcome
Chosen option: "{Option X}" because {rationale}.

## Consequences
### Positive
- {Consequence 1}

### Negative
- {Consequence 1}

## References
- [Principle](../../docs/principles/{relevant}.md)
- [Platform Pattern](../../docs/platforms/{platform}/{relevant}.md)
```

---

## Platform-Specific Guidance

### Microsoft Fabric

Read and apply:
- `docs/platforms/fabric/workspace-patterns.md` - Workspace organization
- `docs/platforms/fabric/notebook-standards.md` - Development patterns
- `docs/platforms/fabric/onelake-patterns.md` - Storage patterns
- `docs/platforms/fabric/pipeline-patterns.md` - Orchestration
- `docs/platforms/fabric/pitfalls.md` - Common mistakes

Key decisions:
- Workspace per domain vs per environment
- OneLake shortcut strategy
- Capacity planning

### Azure Infrastructure

Read and apply:
- `docs/platforms/azure/` - Azure patterns
- `terraform/modules/azure/` - Terraform modules

Key decisions:
- Resource group structure
- Networking (VNet, Private Endpoints)
- Identity (Service Principals, Managed Identities)
- Key Vault strategy

---

## Integration with Other Commands

| After | Use |
|-------|-----|
| `/architect` (new project) | `/init-project` if not done, then `/sdd` for first feature |
| `/architect plan "feature"` | `/sdd "feature"` to implement |
| `/architect review` | `/sdd` to fix issues found |
| Any architecture change | `/document` to update catalog |

---

## Quick Reference

| Command | Output |
|---------|--------|
| `/architect` | Architecture session, ADRs |
| `/architect decisions` | ADR review/update |
| `/architect "topic"` | Guidance with references |
| `/architect plan "feature"` | Implementation approach |
| `/architect review` | Compliance report |
