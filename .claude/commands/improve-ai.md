---
name: improve-ai
description: Iteratively improve AI team assets through interactive dialog and gated approval. Generalizes learnings from projects to the parent repo.
---

# Improve AI

A dialog-driven workflow for capturing learnings and improving AI team assets. Takes project-specific learnings and generalizes them for the entire AI team.

## Usage

```bash
/improve-ai                                    # Start improvement session
/improve-ai "Add new pitfall for API rate limiting"
/improve-ai "Update Fabric patterns with new discovery"
/improve-ai "Improve the /sdd command"
/improve-ai platform                           # Improve platform docs
/improve-ai commands                           # Improve commands
```

## Behavior

When invoked, Claude acts as the **AI Improvement Agent** and guides you through a structured dialog to capture and codify learnings.

---

## Core Principle: Generalization Flow

```
Project-Specific Learning
         ↓
    Generalize
         ↓
Parent Repo (data_ai_agents)
    - docs/platforms/{platform}/
    - docs/patterns/
    - docs/principles/
    - .claude/commands/
```

**Key Rule:** Learnings from projects are **generalized** before adding to the parent repo. No project-specific details in the parent repo.

### Examples of Generalization

| Project Learning | Generalized Form |
|-----------------|------------------|
| "HubSpot API returns 429 after 100 requests" | "REST APIs commonly rate-limit at ~100 req/min. Implement exponential backoff." |
| "Our silver_customers table needs SCD Type 2" | "Customer dimension tables typically need SCD Type 2 for historical tracking" |
| "Fabric notebook failed with OOM on 10GB file" | "Fabric notebooks have memory limits. Partition large files or use streaming." |

---

## Phase 1: Context Gathering

### 1.1 Determine Location & Focus

```bash
# Check current location
pwd

# Determine context
# - In project subrepo → Focus on capturing project learnings
# - In parent repo → Focus on improving AI team assets directly
```

### 1.2 Check for Unprocessed Lessons

Before presenting options, check if there are lessons to review:

```bash
# Check project lessons (if in project)
find docs/lessons -name "*.md" -exec grep -l "Status: Captured" {} \; 2>/dev/null

# Count unprocessed lessons
grep -r "Status: Captured" docs/lessons/ 2>/dev/null | wc -l
```

### 1.3 Present Mode Selection

```markdown
## AI Improvement Session

**Current Location:** [path]
**Context:** [Parent Repo / Project: {name}]

**Unprocessed Lessons Found**: [count] lessons awaiting review

Choose mode:

**A. Review Lessons** (Recommended - [count] lessons pending)
   Review and generalize captured lessons from project work

**B. Direct Improvements**
   1. Platform Patterns - docs/platforms/{platform}/
   2. Principles - docs/principles/
   3. Reusable Patterns - docs/patterns/
   4. Commands - .claude/commands/
   5. Workflows - .claude/workflows/
   6. Templates - docs/templates/

Select: A, B, or describe what you'd like to improve:
```

### 1.4 Map to Files

| Area | Files | When to Update |
|------|-------|----------------|
| Platform Patterns | `docs/platforms/{platform}/*.md` | New pitfalls, patterns, standards |
| Principles | `docs/principles/*.md` | Clarifications, new principles |
| Reusable Patterns | `docs/patterns/*.md` | New or improved patterns |
| Commands | `.claude/commands/*.md` | Workflow improvements |
| Workflows | `.claude/workflows/*.md` | Process improvements |
| Templates | `docs/templates/*.md` | Template enhancements |
| Lessons (Generalized) | `.claude/lessons/{area}/*.md` | Lightweight accumulated learnings |

---

## Phase 1.5: Lesson Review Mode (If Selected)

**This phase runs when user selects "A. Review Lessons" or when automatically invoked by `/sdd`.**

### 1.5.1 Load All Project Lessons

```bash
# Find all lesson files
find docs/lessons -name "*.md" -type f 2>/dev/null

# Read each file
for file in docs/lessons/*.md; do
  cat "$file"
done
```

### 1.5.2 Categorize Lessons

For each lesson with "Status: Captured", analyze and categorize:

| Category | Criteria | Destination |
|----------|----------|-------------|
| **Generalizable - Platform** | Platform-specific (Fabric/Azure/Databricks) | `.claude/lessons/{platform}/` |
| **Generalizable - Pattern** | Cross-platform pattern | `.claude/lessons/patterns/` |
| **Generalizable - Workflow** | Process improvement | `.claude/lessons/workflows/` |
| **Project-Specific** | Only applies to this project | Keep in project `docs/lessons/` |
| **Document-Worthy** | Significant enough for docs | Both `.claude/lessons/` AND `docs/` |

### 1.5.3 Present Lesson Review

```markdown
## Lesson Review

Found [count] unprocessed lessons from project work.

### Categorization Summary

**Generalizable Lessons** ([count]):
- [count] Platform-specific (Fabric/Azure/Databricks)
- [count] Cross-platform patterns
- [count] Workflow improvements

**Project-Specific Lessons** ([count]):
- Will remain in project docs/lessons/

**Document-Worthy** ([count]):
- Significant patterns that should be promoted to docs/

---

### Lesson Details

#### 1. [Lesson Title] - [Category]

**Original**:
> [Problem]: [original problem text]
> [Solution]: [original solution text]

**Generalized Form**:
> [Generalized version with project-specific details removed]

**Proposed Action**:
- Add to: `.claude/lessons/{area}/{file}.md`
- [If document-worthy] Also update: `docs/platforms/{platform}/pitfalls.md`

---

[Repeat for all lessons]

---

Approve generalization plan?
1. "approved" - Process all lessons as proposed
2. "modify [number]" - Adjust specific lesson
3. "skip [number]" - Don't generalize specific lesson
```

### 1.5.4 Process Approved Lessons

For each approved lesson:

1. **Append to parent `.claude/lessons/`**:
   ```bash
   echo "## [DATE] [Title]

   **Context**: [Generalized context]
   **Problem**: [Generalized problem]
   **Solution**: [Generalized solution]
   **Generalization**: [How this applies broadly]
   **Related**:
   - Origin: projects/[project]/docs/lessons/[file]
   - Spec: [spec-id if applicable]

   **Status**: Generalized

   ---
   " >> .claude/lessons/{area}/{file}.md
   ```

2. **Update parent docs/ if document-worthy**:
   - Add to `docs/platforms/{platform}/pitfalls.md`
   - Or create new pattern in `docs/patterns/`
   - Or update existing docs

3. **Mark original lesson as generalized**:
   ```bash
   # Update status in project lesson file
   sed -i '' 's/Status: Captured/Status: Generalized/' docs/lessons/[file].md
   ```

4. **Keep project-specific lessons unchanged** (they stay "Captured")

5. **Commit changes**:
   ```bash
   # Commit to parent repo (if generalizable)
   cd ../..  # Back to data_ai_agents root
   git add .claude/lessons/ docs/
   git commit -m "learn: generalize lessons from [project]

   - [Lesson 1 summary]
   - [Lesson 2 summary]
   - [count] lessons added to .claude/lessons/

   From: projects/[project]/docs/lessons/"

   # Commit to project repo (mark as generalized)
   cd projects/[project]
   git add docs/lessons/
   git commit -m "docs: mark lessons as generalized

   Lessons reviewed and added to parent repo."
   ```

**Skip to Phase 5 (Final Review) after processing lessons.**

---

## Phase 2: Probing Dialog (Direct Improvements Mode)

Ask targeted questions based on the selected area. **Do not skip this phase** - the goal is to surface implicit knowledge.

### Platform Patterns Questions

```markdown
## Improving Platform Patterns

Let me ask questions to surface learnings:

1. **New pitfalls**: What mistakes did you encounter that aren't documented?

2. **Missing patterns**: What implementation patterns worked well but aren't captured?

3. **Outdated info**: What documented patterns no longer apply or have better alternatives?

4. **Platform quirks**: Any platform-specific behaviors that surprised you?

Please share your thoughts on any of these:
```

### Principles Questions

```markdown
## Improving Principles

Let me understand what needs updating:

1. **Clarifications needed**: Are any principles unclear or ambiguous in practice?

2. **New principles**: Should we add any new guiding principles?

3. **Exceptions**: Are there valid exceptions to current principles that should be documented?

4. **Real-world application**: How well do current principles translate to implementation?

Please share your thoughts:
```

### Command/Workflow Questions

```markdown
## Improving Commands/Workflows

Let me understand what needs improving:

1. **Workflow gaps**: Are there steps missing or unclear in the workflow?

2. **Edge cases**: What scenarios does the command handle poorly?

3. **User experience**: Is the dialog/interaction flow working well?

4. **Platform awareness**: Does the command correctly adapt to different platforms?

5. **Integration**: Does it work well with other commands?

Please share your thoughts:
```

### Follow-up Questions

After initial responses, ask clarifying questions:
- "Can you give me a specific example?"
- "What was the error message or symptom?"
- "How did you discover the correct approach?"
- "Would this apply to all similar cases or just specific ones?"
- "How would you generalize this for other projects?"

---

## Phase 3: Generalization

Before proposing changes, generalize project-specific learnings.

### 3.1 Identify Generalizable Learnings

For each learning, determine:

| Question | Answer |
|----------|--------|
| Is this specific to one project? | If yes, keep in project docs only |
| Would this help other projects? | If yes, generalize |
| Is this platform-specific? | If yes, add to `docs/platforms/{platform}/` |
| Is this a universal pattern? | If yes, add to `docs/patterns/` |

### 3.2 Generalization Process

```markdown
## Generalizing Learnings

You mentioned: "[specific learning]"

Let me generalize this:

**Original (project-specific):**
> HubSpot API returns 429 errors when we call it more than 100 times per minute during our daily sync.

**Generalized (for parent repo):**
> REST APIs commonly implement rate limiting. When ingesting data:
> - Check API documentation for rate limits
> - Implement exponential backoff (start at 1s, max 60s)
> - Add retry logic for 429 responses
> - Consider batch endpoints to reduce call count

Is this generalization accurate and helpful?
```

### 3.3 Determine Destination

| Learning Type | Destination |
|--------------|-------------|
| Platform pitfall | `docs/platforms/{platform}/pitfalls.md` |
| Platform pattern | `docs/platforms/{platform}/*.md` |
| Universal pattern | `docs/patterns/{pattern}.md` |
| Principle clarification | `docs/principles/{principle}.md` |
| Command improvement | `.claude/commands/{command}.md` |
| Workflow improvement | `.claude/workflows/{workflow}.md` |

---

## Phase 4: Propose Changes

### 4.1 Read Current Files

Before proposing changes, read the relevant files:

```bash
# For platform patterns
cat docs/platforms/fabric/pitfalls.md

# For commands
cat .claude/commands/sdd.md

# For principles
cat docs/principles/data-governance.md
```

### 4.2 Draft Changes

Create specific, actionable changes:

```markdown
## Proposed Changes

Based on our discussion, here are the changes I'll make:

### File: docs/platforms/fabric/pitfalls.md

**Change 1**: Add new pitfall for rate limiting

```diff
+ ### PIT-0XX: API Rate Limiting
+
+ **Symptom**: 429 errors during data ingestion
+
+ **Wrong approach**:
+ ```python
+ # No retry logic
+ for item in items:
+     response = api.get(item)
+ ```
+
+ **Correct approach**:
+ ```python
+ @retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
+ def api_call_with_retry(item):
+     response = api.get(item)
+     response.raise_for_status()
+     return response
+ ```
+
+ **Explanation**: Always implement exponential backoff for external API calls.
```

**Rationale**: This pattern applies to all API integrations, not just the specific project where it was discovered.

---

Review these changes?

Options:
1. "approved" - Apply all changes
2. "modify" - Request adjustments
3. "skip" - Discard and end session
```

---

## Gate: User Approval

**Wait for explicit approval before making changes.**

### If "approved"

Proceed to Phase 5.

### If "modify"

- Collect requested modifications
- Update proposed changes
- Present again for approval

### If "skip"

```
No changes made. Session ended.
```

---

## Phase 5: Apply & Commit

### 5.1 Apply Changes

Make the approved edits to the files.

### 5.2 Verify Changes

```bash
# Show what changed
git diff

# Ensure we're in the parent repo
pwd  # Should be data_ai_agents root
```

### 5.3 Commit

```bash
git add docs/ .claude/
git commit -m "learn: [category] - [brief description]

- [Change 1]
- [Change 2]

Generalized from: [project name if applicable]

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Commit Message Examples

```bash
# Platform pitfall
git commit -m "learn: fabric/pitfalls - add API rate limiting guidance

- Added PIT-050: REST API rate limiting patterns
- Include exponential backoff example

Generalized from: client-hubspot-integration"

# Pattern addition
git commit -m "learn: patterns - add SCD Type 2 implementation pattern

- Created docs/patterns/scd-type-2.md
- Added PySpark and SQL examples

Generalized from: multiple customer projects"

# Command improvement
git commit -m "learn: commands - improve /sdd platform detection

- Added Databricks detection logic
- Fixed documentation path references"

# Principle clarification
git commit -m "learn: principles - clarify data classification for derived data

- Added guidance on classification inheritance
- Clarified when to upgrade classification level"
```

---

## Session Complete

```markdown
## Improvements Applied

Changes committed: [commit hash]

Files updated:
- [file 1]: [what changed]
- [file 2]: [what changed]

### Summary

The AI team is now smarter. These generalized learnings will improve future work across all projects.

### What Happens Next

When developers use these commands in any project:
- `/sdd` will apply the new patterns
- `/document` will reference updated principles
- `/architect` will use improved guidance

### Remaining Project-Specific Items

If there were learnings that couldn't be generalized, they should stay in the project:
- [Project-specific item 1] → Add to project's docs/
- [Project-specific item 2] → Add to project's runbooks/
```

---

## Quick Reference

| Phase | Purpose | User Input |
|-------|---------|------------|
| 1 | Context | Select area or describe |
| 2 | Probing | Answer questions, share learnings |
| 3 | Generalize | Confirm generalizations |
| 4 | Propose | Review diff, request changes |
| Gate | Approve | approved / modify / skip |
| 5 | Apply | Automatic |

## Improvement Targets

| Target | Files | When to Update |
|--------|-------|----------------|
| **Platform Docs** | | |
| Fabric patterns | `docs/platforms/fabric/*.md` | Fabric-specific learnings |
| Azure patterns | `docs/platforms/azure/*.md` | Azure infrastructure learnings |
| Databricks patterns | `docs/platforms/databricks/*.md` | Databricks learnings |
| Platform pitfalls | `docs/platforms/{platform}/pitfalls.md` | New mistakes discovered |
| **Principles** | | |
| Data governance | `docs/principles/data-governance.md` | Governance clarifications |
| Data quality | `docs/principles/data-quality.md` | Quality rule updates |
| Medallion | `docs/principles/medallion-architecture.md` | Layer boundary clarifications |
| **Patterns** | | |
| API ingestion | `docs/patterns/api-ingestion.md` | API integration patterns |
| Incremental load | `docs/patterns/incremental-load.md` | Load pattern improvements |
| SCD patterns | `docs/patterns/scd-type-2.md` | Dimension handling |
| Error handling | `docs/patterns/error-handling.md` | Error patterns |
| **Commands** | | |
| /sdd | `.claude/commands/sdd.md` | Workflow improvements |
| /document | `.claude/commands/document.md` | Documentation process |
| /architect | `.claude/commands/architect.md` | Architecture guidance |
| /init-project | `.claude/commands/init-project.md` | Project setup |
| /init-data-ai | `.claude/commands/init-data-ai.md` | Team initialization |
| **Workflows** | | |
| Quick Fix | `.claude/workflows/quick-fix.md` | Lightweight workflow |
| Full SDD | `.claude/workflows/full-sdd.md` | Comprehensive workflow |
| **Templates** | | |
| Catalog entry | `docs/templates/catalog-entry.md` | Data documentation |
| ADR | `docs/templates/adr.md` | Decision records |
| Source integration | `docs/templates/source-integration.md` | Source docs |
| Runbook | `docs/templates/runbook.md` | Operations |

---

## Integration with Other Commands

| Command | Triggers /improve-ai |
|---------|---------------------|
| `/sdd` | After merge, offers to capture learnings |
| `/document` | When generalizable patterns found |
| `/architect` | When new architectural patterns emerge |
