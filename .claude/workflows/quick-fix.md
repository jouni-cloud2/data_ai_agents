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
3. **Capture lessons** - Document issues encountered
4. **Stage changes** - `git add [files]`

### During Implementation

- Keep changes minimal and focused
- Don't refactor unrelated code
- Don't add features beyond the fix

### Capture Lessons

If you encounter issues, discover gotchas, or apply patterns during implementation, capture them:

**Create/append to:** `docs/lessons/general.md` (in project subrepo)

```markdown
## [YYYY-MM-DD] [Short Title]

**Context**: Quick fix - [brief context]
**Problem**: [What issue was encountered]
**Solution**: [How it was resolved]
**Generalization**: [How this applies more broadly]
**Related**:
- Code: [file:line]

**Status**: Captured

---
```

**Examples of lessons to capture:**
- API rate limits encountered
- Platform-specific behaviors discovered
- Error messages and their solutions
- Configuration gotchas
- Performance issues and fixes

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

## Step 7: Automatic Documentation and Learning

After merge decision, **automatically** run documentation and learning workflows.

### Step 7.1: Run /document Command

```markdown
Running /document to update project documentation...
```

This will:
- Create catalog entries for any new tables/pipelines
- Update source documentation if needed
- Update indexes and verify completeness

### Step 7.2: Run /improve-ai Command

```markdown
Running /improve-ai to review and generalize lessons...
```

This will:
- Review lessons from `docs/lessons/general.md`
- Generalize and add to `.claude/lessons/`
- Update parent docs if needed
- Mark lessons as processed

### Step 7.3: Summary

```markdown
## Quick Fix Complete

**Development**: ✅ Complete
**Documentation**: ✅ Updated via /document
**Lessons**: ✅ Captured and generalized via /improve-ai

Work complete!
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
