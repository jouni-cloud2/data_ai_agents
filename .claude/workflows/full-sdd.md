# Full SDD Workflow

Comprehensive workflow for medium and complex changes. Includes spec authoring, gated approvals, and documentation.

## IMPORTANT: Agent Interaction

**READ THIS FIRST**: See [../interaction-guidelines.md](../interaction-guidelines.md) for how to ask questions properly.

**Key rule**: Always present options as clickable choices, never ask users to type responses when options can be provided.

## When to Use

- New features or components
- Multi-file changes
- Architectural decisions
- Cross-cutting concerns
- Anything requiring design decisions

## Workflow

```
Gate #1: Full SDD Selected
           ↓
    Spec Authoring (gap-filling questions)
           ↓
    Create Feature Branch
           ↓
    Gate #2: Spec Approval
           ↓
    Story Splitting (names only — small stories)
           ↓
    Gate #2b: Story List Approval
           ↓
    Write Full Stories (one by one, in spec)
           ↓
    Implementation (story by story)
           ↓
    Validate Changes (pre-commit)
           ↓
    Verification
           ↓
    Gate #3: Implementation Approval
           ↓
    Documentation Update
           ↓
    Gate #4: Merge Decision
```

---

## Step 1: Spec Authoring

### 1.1 Gap-Filling Questions

Ask clarifying questions to fill gaps in requirements:

```
## Spec Authoring: Gap-Filling Questions

**Request**: [User's request]

I need to clarify a few things before writing the spec:

1. [Question about scope/boundaries]
2. [Question about specific behavior]
3. [Question about edge cases]
4. [Question about platform/technology choices]
```

Continue asking until requirements are clear.

### 1.2 Create Spec Directory

```bash
# Generate spec ID
SPEC_ID="SDD-$(date +%Y%m%d)-[short-slug]"

mkdir -p ./projects/<project>/docs/specs/$SPEC_ID
```

### 1.3 Write Specification

Create `./projects/<project>/docs/specs/{spec-id}/spec.md`:

```markdown
# Spec: [Title]

**ID**: [SPEC_ID]
**Created**: [Date]
**Status**: Draft

## Overview

[Brief description of what this spec covers]

## Requirements

### Functional Requirements

1. **[FR-1]**: [Requirement description]
2. **[FR-2]**: [Requirement description]

### Non-Functional Requirements

1. **[NFR-1]**: [Requirement description]

## Behavior

### Scenario: [Scenario Name]

**Given** [initial context]
**When** [action]
**Then** [expected outcome]

### Scenario: [Another Scenario]

**Given** [initial context]
**When** [action]
**Then** [expected outcome]

## Technical Approach

### Architecture

[How this fits into the existing architecture]

### Components Affected

- [Component 1]: [How it's affected]
- [Component 2]: [How it's affected]

### Data Flow

[Description or diagram of data flow]

## Out of Scope

- [What this spec explicitly does NOT cover]

## Open Questions

- [Any unresolved questions]

## Dependencies

- [External dependencies]
- [Internal dependencies]
```

---

## Step 1b: Fabric Branch Pre-Flight (Fabric Platform Only)

**Before creating any branches or pushing**, confirm the target deployment branch for each Fabric workspace involved in the spec.

```bash
# List all domain branches
git branch -a | grep -E "_dev|_test|_prod"
```

For each workspace affected by this spec, record:

| Workspace | Git Branch | Confirmed? |
|-----------|------------|------------|
| `it_dev` | `it_dev` | ☐ |
| `projects_dev` | `projects_dev` | ☐ |
| `mdm_dev` | `mdm_dev` | ☐ |

**Also check `.platform` logicalId uniqueness** for any new artifacts:
```bash
# Verify no duplicate logicalIds already exist
grep -r "logicalId" fabric/ --include=".platform" | awk -F'"' '{print $4}' | sort | uniq -d
# Empty output = no duplicates (good)
```

**And inspect target branch structure** before any merge/cherry-pick:
```bash
git checkout {domain}_dev && git pull origin {domain}_dev
find fabric/{domain} -type f | sort   # Look for unexpected nested paths
```

If corrupted paths found (e.g. `fabric/it/fabric/it/`), clean up before proceeding:
```bash
git rm -r --cached fabric/{domain}/fabric/
rm -rf fabric/{domain}/fabric/
```

---

## Step 2: Create Feature Branch

```bash
git checkout -b feature/[spec-id]
```

Add spec to version control:

```bash
git add ./projects/<project>/docs/specs/[spec-id]/
git commit -m "spec: add [spec-id] specification

[Brief description]"
```

---

## Gate #2: Spec Approval

Present spec for approval:

```
## Spec Ready for Review

**Spec ID**: [SPEC_ID]
**Location**: ./projects/<project>/docs/specs/[spec-id]/spec.md

### Summary

[Brief summary of what will be implemented]

### Key Decisions

- [Decision 1]
- [Decision 2]

### Scope

- Files to create: [count]
- Files to modify: [count]
- Components affected: [list]

---

**Approve this spec to proceed with implementation?**

- **Approve** - Proceed to implementation
- **Show Spec** - Display full spec first
- **Request Changes** - Provide feedback for modifications

What would you like to do?
```

### If "Show Spec"

Display the full spec.md content, then ask again.

### If "Request Changes"

- Collect feedback
- Update spec
- Re-commit spec changes
- Present for approval again

### If "Approve"

Proceed to story splitting.

---

## Step 2b: Story Splitting

After spec approval, split the spec into **small, independently implementable stories**. A story should be completable in one focused session — one notebook, one pipeline, one lakehouse definition, etc.

### 2b.1 Draft Story List (Names Only)

Analyze the spec and produce a flat list of story names. Keep each name short (3–8 words). Do NOT write full stories yet.

```markdown
## Story List for [SPEC_ID]

Stories to implement (in dependency order):

1. Create lh_it_bronze_dev lakehouse definition
2. Create lh_it_curated_dev lakehouse definition
3. Create util_generate_mock_data_it notebook
4. Update bronze_load_freshservice default lakehouse + mock param
5. Update silver_transform_freshservice to curated lakehouse
6. Create setup_ddm_views_it notebook
7. Create pl_it_daily_ingest pipeline
8. Delete old it_daily_pipeline

**Story sizing guidance:**
- Each story = one artifact or one focused change
- No story spans multiple unrelated notebooks
- Stories are ordered by dependency (earlier = prerequisite for later)
```

### 2b.2 Gate #2b: Story List Approval

Present the story list for approval:

```markdown
## Story List Ready

**Spec**: [SPEC_ID]
**Stories**: [count] stories identified

[Story list here — names only]

---

**Approve this story breakdown?**

- **Approve** - Write full stories and begin implementation
- **Add Story** - Add a missing story (specify)
- **Remove Story** - Remove a story (specify number)
- **Split Story** - Story too large, split it (specify number)
- **Merge Stories** - Two stories too small, merge (specify numbers)

What would you like to do?
```

### 2b.3 Write Full Stories

After story list approval, write each story in full — one at a time, appended to `spec.md` under a `## Stories` section:

```markdown
## Stories

### Story 1: Create lh_it_bronze_dev lakehouse definition

**As a** data engineer,
**I want** a Fabric lakehouse definition tracked in Git,
**So that** the bronze lakehouse can be synced to the it_dev workspace.

**Acceptance Criteria:**
- [ ] `fabric/it/lh_it_bronze_dev.Lakehouse/.platform` exists with correct logicalId
- [ ] `lakehouse.metadata.json`, `alm.settings.json`, `shortcuts.metadata.json` present
- [ ] Workspace ID matches `4681b1cd-...` (it_dev)

**Implementation Notes:**
- logicalId is a placeholder UUID4 (Fabric assigns real ID on first sync)
- alm.settings.json should enable shortcuts

---

### Story 2: ...
```

**Story sizing rules:**
- Max 5 acceptance criteria per story
- Each criterion is testable/verifiable
- No story should take more than ~30 min to implement

Commit stories after writing:
```bash
git add ./projects/<project>/docs/specs/[spec-id]/spec.md
git commit -m "spec: add stories for [spec-id]"
```

---

## Step 3: Implementation

### 3.1 Create Implementation Notes and Lessons File

Create `./projects/<project>/docs/specs/{spec-id}/implementation.md`:

```markdown
# Implementation Notes: [SPEC_ID]

**Started**: [Date]
**Status**: In Progress

## Approach

[How we're implementing this]

## Progress

- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]

## Decisions Made During Implementation

| Decision | Rationale | Date |
|----------|-----------|------|
| [Decision] | [Why] | [Date] |

## Issues Encountered

### Issue 1: [Title]

**Problem**: [Description]
**Solution**: [How it was resolved]

## Files Changed

- [file1.py]: [What changed]
- [file2.py]: [What changed]
```

**Also create** `./projects/<project>/docs/lessons/{spec-id}.md` for capturing lessons during implementation:

```markdown
# Lessons: [SPEC_ID]

Lessons learned during implementation of this spec.

---
```

### 3.2 Implement and Capture Lessons

Follow the spec and implement:

1. **Work incrementally** - Complete one component at a time
2. **Update implementation notes** - Track progress and decisions
3. **Capture lessons** - Document issues, gotchas, and patterns as you discover them
4. **Stage changes** - `git add` as you complete components

### Capturing Lessons During Implementation

As you work, capture lessons in `./projects/<project>/docs/lessons/{spec-id}.md`:

```markdown
## [YYYY-MM-DD] [Short Title]

**Context**: [What you were implementing]
**Problem**: [Issue encountered, pattern discovered, gotcha found]
**Solution**: [How you resolved it or what approach worked]
**Generalization**: [How this applies beyond this specific case]
**Related**:
- Code: [file:line]
- Spec: [spec-id]
- Docs: [relevant doc]

**Status**: Captured

---
```

**Capture lessons for:**
- **Errors encountered**: API errors, platform errors, configuration issues
- **Patterns discovered**: Effective approaches that worked well
- **Gotchas**: Unexpected behaviors or edge cases
- **Performance**: Memory limits, timeouts, optimization techniques
- **Platform quirks**: Fabric/Azure/Databricks-specific behaviors
- **Dependency issues**: Version conflicts, missing packages

**Don't overthink it** - Quick capture is better than perfect documentation. The `/improve-ai` command will review and generalize these later.

### 3.3 Validate Before Commit

Run pre-commit hooks to catch issues early:

```bash
# Stage changes
git add .

# Run validation
pre-commit run
```

**Handle validation results:**

| Result | Action |
|--------|--------|
| All pass | Proceed to commit |
| Auto-fixed | Re-stage files, re-run |
| Manual fix needed | Fix issues, re-stage, re-run |

```
## Validation Results

| Check | Status |
|-------|--------|
| Terraform fmt | ✅ Passed |
| TFLint | ✅ Passed |
| Python (ruff) | ✅ Passed |
| Security scan | ✅ Passed |
| Secret detection | ✅ Passed |
```

### 3.4 Commit Implementation

```bash
git commit -m "feat: implement [spec-id]

- [Key change 1]
- [Key change 2]
- [Key change 3]

Implements: [SPEC_ID]"
```

---

## Step 4: Verification

### 4.1 Self-Verification Checklist

Before presenting for approval:

- [ ] All scenarios from spec are implemented
- [ ] Code follows existing patterns in codebase
- [ ] No hardcoded values that should be configurable
- [ ] Error handling is appropriate
- [ ] Implementation notes are updated

### 4.2 Verification Report

```
## Verification Complete

**Spec**: [SPEC_ID]

### Scenarios Verified

| Scenario | Status |
|----------|--------|
| [Scenario 1] | Implemented |
| [Scenario 2] | Implemented |

### Implementation Summary

- Files created: [count]
- Files modified: [count]
- Lines added: [count]
- Lines removed: [count]

### Notes

[Any implementation notes or deviations from spec]
```

---

## Gate #3: Implementation Approval

```
## Implementation Ready for Review

**Spec**: [SPEC_ID]

### Changes Summary

[Summary of what was implemented]

### Files Changed

- [file1]: [description]
- [file2]: [description]

---

**What would you like to do?**

- **Approve** - Proceed to documentation
- **Show Diff** - View all changes
- **Show File** - View specific file (specify which)
- **Request Changes** - Request modifications

Please select:
```

### If "Show Diff"

```bash
git diff main...HEAD
```

### If "Request Changes"

- Collect feedback
- Make modifications
- Update implementation notes
- Present for approval again

### If "Approve"

Proceed to documentation.

---

## Step 5: Data Documentation (MANDATORY)

**Every new table or pipeline MUST be documented.** Use the template from `agents/skills/platform/data-documentation-template.md`.

### 5.1 Identify New Data Assets

List all new tables/pipelines created:
- Tables: `{catalog.schema.table}`
- Pipelines: `{pipeline_name}`

### 5.2 Auto-Fill Known Values

Fill in values that can be determined from implementation:

| Field | Source |
|-------|--------|
| Name | From table/pipeline name |
| Layer | From naming convention (bronze/silver/gold) |
| Source System(s) | From implementation |
| Dependencies | From code/lineage |
| Transformation Summary | From notebook/pipeline logic |
| Technical Owner | Current implementer |
| Created Date | Today |

### 5.3 Ask User for Missing Values

**ALWAYS ask the user for these fields:**

```
## Data Documentation Required

I've created the following data assets that need documentation:

### [Asset Name]

I can fill in the technical details, but I need your input on:

1. **Owner** (Business owner accountable for this data):
   >

2. **Steward** (Day-to-day governance responsible):
   >

3. **Purpose / Business Use Case** (Why does this exist? What business value?):
   >

4. **Data Classification** (Public / Internal / Confidential / Restricted):
   >

5. **Retention Policy** (How long to keep? Archive strategy?):
   >

6. **Retention Reason** (Why this retention period?):
   >

7. **Data Quality Rules** (What checks should be applied?):
   >

8. **Consumers** (Who/what will use this data?):
   >

9. **Compliance Requirements** (GDPR, SOX, etc. or N/A):
   >

Please provide values for these fields.
```

### 5.4 Create Documentation File

Create `./projects/<project>/docs/catalog/{domain}_{layer}_{name}.md` using the template with all values filled in.

### 5.5 Update Other Documentation

1. **Update CLAUDE.md** if new patterns established
2. **Update relevant skill files** if new techniques used
3. **Update data-contracts.md** with new schema definitions
4. **Add to implementation notes** - Final status

### Commit Documentation

```bash
git add ./projects/<project>/docs/ .claude/ CLAUDE.md
git commit -m "docs: add data documentation for [spec-id]

- Added catalog entry for {table/pipeline}
- [Other doc updates]"
```

---

## Step 6: Create PR

```bash
git push -u origin feature/[spec-id]

gh pr create \
  --title "feat: [title from spec]" \
  --body "## Summary

[Summary from spec]

## Spec

See: ./projects/<project>/docs/specs/[spec-id]/spec.md

## Changes

- [Change 1]
- [Change 2]

## Validation

- Pre-commit hooks: ✅ Passed
- Terraform checks: ✅ Passed
- Security scan: ✅ Passed

## Verification

All spec scenarios implemented and verified.

---
Generated via SDD Full workflow
Spec: [SPEC_ID]"
```

---

## Gate #4: Merge Decision

```
PR created: [PR URL]

All gates passed:
- [x] Gate #2: Spec Approved
- [x] Gate #3: Implementation Approved

**What would you like to do?**

- **Merge Now** - Merge to dev branch now
- **Hold for Review** - Keep PR open for review

Please select:
```

### If "Merge Now"

```bash
gh pr merge --squash
git checkout dev
git pull
```

Update spec status:

```bash
# Update spec.md status to "Implemented"
git add ./projects/<project>/docs/specs/[spec-id]/
git commit -m "spec: mark [spec-id] as implemented"
git push
```

### If "Hold for Review"

```
PR ready for review: [PR URL]
Spec location: ./projects/<project>/docs/specs/[spec-id]/
```

---

## Step 7: Automatic Documentation and Learning

After merge decision (for both "merge" and "hold"), **automatically** run documentation and learning workflows.

### Step 7.1: Run /document Command

```markdown
Running /document to update project documentation...
```

This will:
- Create catalog entries for any new tables/pipelines
- Update source documentation if needed
- Update indexes and verify completeness
- Ask user for governance fields

### Step 7.2: Run /improve-ai Command

```markdown
Running /improve-ai to review and generalize lessons...
```

This will:
- Review lessons from `./projects/<project>/docs/lessons/{spec-id}.md`
- Separate generalizable from project-specific
- Add generalized lessons to `.claude/lessons/`
- Update parent `docs/` if patterns warrant it
- Mark lessons as processed

### Step 7.3: Summary

```markdown
## Full SDD Workflow Complete

**Development**: ✅ Complete
**Documentation**: ✅ Updated via /document
**Lessons**: ✅ Captured and generalized via /improve-ai

### Summary
- Spec: [spec-id]
- Branch: [branch-name]
- PR: [PR URL]
- Lessons captured: [count]
- Lessons generalized: [count]
- Documentation updated: [list]

Work complete!
```

---

## Handling Scope Changes

If during implementation you discover the scope needs to change:

```
## Scope Change Detected

During implementation, I discovered:
- [Finding 1]
- [Finding 2]

This affects the original spec:
- [Impact 1]
- [Impact 2]

**How would you like to proceed?**

- **Update Spec** - Modify spec and continue
- **Split Scope** - Create separate spec for new scope
- **Continue** - Proceed with original scope only

What would you like to do?
```

If "Update Spec", return to Gate #2 for re-approval.
