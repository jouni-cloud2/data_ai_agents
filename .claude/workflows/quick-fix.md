# Quick Fix Workflow

Lightweight workflow for trivial and simple changes. Minimal ceremony, direct implementation.

## When to Use

- Typos, single-line fixes
- Config changes
- Small bugs with clear solutions
- Minor tweaks with obvious scope

## Workflow

```
Gate #1: Quick Fix Selected
           ↓
    Create Feature Branch
           ↓
    Direct Implementation
           ↓
    Validate Changes (pre-commit)
           ↓
    Gate #2: Approval
           ↓
    Merge Decision
```

---

## Step 1: Create Feature Branch

```bash
# Generate branch name from request
git checkout -b fix/[short-description]
```

Examples:
- `fix/typo-in-readme`
- `fix/null-check-customer-transform`
- `fix/config-timeout-value`

---

## Step 2: Direct Implementation

Implement the fix directly:

1. **Make the change** - Edit the necessary files
2. **Verify locally** - Ensure the fix works
3. **Stage changes** - `git add [files]`

### During Implementation

- Keep changes minimal and focused
- Don't refactor unrelated code
- Don't add features beyond the fix

---

## Step 3: Validate Changes

Before presenting for approval, run validation to catch issues early.

### 3.1 Run Pre-commit Hooks

```bash
# Stage changes
git add [files]

# Run validation
pre-commit run
```

### 3.2 Handle Validation Results

**If all checks pass:**
```
## Validation Passed

| Check | Status |
|-------|--------|
| Formatting | ✅ Passed |
| Linting | ✅ Passed |
| Security scan | ✅ Passed |

Proceeding to approval...
```

**If checks fail:**

1. **Auto-fixable issues** (formatting, imports):
   ```bash
   # Pre-commit auto-fixes many issues
   # Re-stage the fixed files
   git add [files]
   ```

2. **Manual fixes needed** (lint errors, security):
   ```
   ## Validation Failed

   | Check | Status | Action |
   |-------|--------|--------|
   | TFLint | ❌ Failed | Fix: [file:line] - [issue] |
   | Ruff | ❌ Failed | Fix: [file:line] - [issue] |

   Fixing issues...
   ```
   - Apply fixes
   - Re-run validation
   - Continue when all pass

### 3.3 Validation Checklist

- [ ] Pre-commit hooks pass
- [ ] No secrets detected
- [ ] Terraform formatted (if applicable)
- [ ] Python linted (if applicable)

---

## Step 4: Present for Approval (Gate #2)

```
## Quick Fix Complete

**Request**: [Original request]

**Changes Made**:
- [File 1]: [Description of change]
- [File 2]: [Description of change]

**Files Changed**: [count]

---

Ready to commit and create PR?

Options:
1. "approved" - Commit and create PR
2. "show diff" - View the changes
3. "make changes" - Request modifications
```

### If "show diff"

```bash
git diff --staged
```

Then ask again for approval.

### If "make changes"

- Collect requested modifications
- Apply changes
- Present for approval again

### If "approved"

Proceed to commit.

---

## Step 5: Commit and PR

```bash
git commit -m "fix: [short description]

[Longer description if needed]"

git push -u origin fix/[short-description]

gh pr create \
  --title "fix: [short description]" \
  --body "## Summary
- [What was fixed]

## Changes
- [List of changes]

## Validation
- Pre-commit hooks: ✅ Passed

---
Generated via SDD Quick Fix workflow"
```

---

## Step 6: Merge Decision (Gate #3)

```
PR created: [PR URL]

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

### If "hold"

```
PR ready for review: [PR URL]
```

---

## Step 7: Data Documentation (If New Data Created)

**If your quick fix created any new tables or pipelines**, you MUST document them.

### Check for New Data Assets

Did this fix create:
- [ ] New tables
- [ ] New pipelines
- [ ] New data flows

If YES to any, proceed with documentation.

### Ask User for Required Values

```
## Data Documentation Required

This fix created new data asset(s): [list]

I need your input on governance fields:

1. **Owner** (Business owner):
2. **Steward** (Governance responsible):
3. **Purpose** (Business value):
4. **Data Classification** (Public/Internal/Confidential/Restricted):
5. **Retention Policy** (Duration, archive strategy):
6. **Consumers** (Who uses this?):

Please provide values.
```

### Create Documentation

Create `docs/catalog/{domain}_{layer}_{name}.md` with template from `.claude/skills/platform/data-documentation-template.md`.

```bash
git add docs/catalog/
git commit --amend --no-edit  # Add to existing commit
git push --force-with-lease
```

---

## Implementation Notes

Quick Fix does NOT create:
- Spec files in `docs/specs/`
- Implementation notes
- Architecture decisions

**Quick Fix DOES create:**
- Data documentation for any new tables/pipelines (MANDATORY)

If during implementation you discover the change is more complex than expected:

```
This change is more complex than initially assessed.

Findings:
- [Complexity 1]
- [Complexity 2]

Recommend switching to Full SDD workflow.

Switch to Full SDD? (yes/no)
```

If yes, transition to [Full SDD Workflow](./full-sdd.md) and create proper spec.
