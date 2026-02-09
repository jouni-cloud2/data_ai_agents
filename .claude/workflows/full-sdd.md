# Full SDD Workflow

Comprehensive workflow for medium and complex changes. Includes spec authoring, gated approvals, and documentation.

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
    Implementation
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

mkdir -p docs/specs/$SPEC_ID
```

### 1.3 Write Specification

Create `docs/specs/{spec-id}/spec.md`:

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

## Step 2: Create Feature Branch

```bash
git checkout -b feature/[spec-id]
```

Add spec to version control:

```bash
git add docs/specs/[spec-id]/
git commit -m "spec: add [spec-id] specification

[Brief description]"
```

---

## Gate #2: Spec Approval

Present spec for approval:

```
## Spec Ready for Review

**Spec ID**: [SPEC_ID]
**Location**: docs/specs/[spec-id]/spec.md

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

Approve this spec to proceed with implementation?

Options:
1. "approved" - Proceed to implementation
2. "show spec" - Display full spec
3. "changes needed" - Request modifications
```

### If "show spec"

Display the full spec.md content, then ask again.

### If "changes needed"

- Collect feedback
- Update spec
- Re-commit spec changes
- Present for approval again

### If "approved"

Proceed to implementation.

---

## Step 3: Implementation

### 3.1 Create Implementation Notes and Lessons File

Create `docs/specs/{spec-id}/implementation.md`:

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

**Also create** `docs/lessons/{spec-id}.md` for capturing lessons during implementation:

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

As you work, capture lessons in `docs/lessons/{spec-id}.md`:

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

Options:
1. "approved" - Proceed to documentation
2. "show diff" - View all changes
3. "show file [name]" - View specific file
4. "changes needed" - Request modifications
```

### If "show diff"

```bash
git diff main...HEAD
```

### If "changes needed"

- Collect feedback
- Make modifications
- Update implementation notes
- Present for approval again

### If "approved"

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

Create `docs/catalog/{domain}_{layer}_{name}.md` using the template with all values filled in.

### 5.5 Update Other Documentation

1. **Update CLAUDE.md** if new patterns established
2. **Update relevant skill files** if new techniques used
3. **Update data-contracts.md** with new schema definitions
4. **Add to implementation notes** - Final status

### Commit Documentation

```bash
git add docs/ .claude/ CLAUDE.md
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

See: docs/specs/[spec-id]/spec.md

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

Options:
1. "merge" - Merge to dev branch now
2. "hold" - Keep PR open for review
```

### If "merge"

```bash
gh pr merge --squash
git checkout dev
git pull
```

Update spec status:

```bash
# Update spec.md status to "Implemented"
git add docs/specs/[spec-id]/
git commit -m "spec: mark [spec-id] as implemented"
git push
```

### If "hold"

```
PR ready for review: [PR URL]
Spec location: docs/specs/[spec-id]/
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
- Review lessons from `docs/lessons/{spec-id}.md`
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

Options:
1. "update spec" - Modify spec and continue
2. "split" - Create separate spec for new scope
3. "continue" - Proceed with original scope only
```

If updating spec, return to Gate #2 for re-approval.
