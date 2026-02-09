# Lessons System

This directory contains **generalized lessons** learned from project work. These lessons help all commands avoid known pitfalls and apply proven patterns.

## Structure

```
.claude/lessons/
  fabric/           # Microsoft Fabric lessons
    pitfalls.md     # Known pitfalls and solutions
    patterns.md     # Proven patterns
    performance.md  # Performance lessons
  azure/            # Azure infrastructure lessons
    infrastructure.md
    security.md
  databricks/       # Databricks lessons
    patterns.md
  patterns/         # Cross-platform patterns
    api-ingestion.md
    error-handling.md
    scd-patterns.md
  workflows/        # Command/workflow improvements
    sdd.md
    documentation.md
```

## Lesson Entry Format

Each lesson follows this format:

```markdown
## [YYYY-MM-DD] [Short Title]

**Context**: [Spec ID / File / Scenario where this happened]
**Problem**: [What went wrong, what was unclear, what was discovered]
**Solution**: [How it was resolved or what approach worked]
**Generalization**: [How this applies more broadly - ready for docs]
**Related**:
- Code: [file:line]
- Spec: [spec-id]
- Docs: [doc reference]

**Status**: Captured | Reviewed | Generalized

---
```

## How Lessons Flow

### 1. Capture (During /sdd)

During `/sdd` work, lessons are captured in the **project subrepo**:
- Location: `projects/<project>/docs/lessons/<spec-id>.md`
- Captured automatically as issues/patterns are encountered
- Project-specific details preserved

### 2. Review (At end of /sdd)

After merge, `/improve-ai` automatically:
1. Reviews project lessons from `projects/<project>/docs/lessons/`
2. Separates generalizable from project-specific
3. Generalizes lessons (removes project specifics)
4. Adds to parent `.claude/lessons/`
5. Updates parent `docs/` if patterns warrant documentation
6. Marks lessons as "Generalized"

### 3. Apply (All commands)

Commands load relevant lessons on start:
- `/sdd` on Fabric project → Reads `.claude/lessons/fabric/*.md`
- `/architect` → Reads `.claude/lessons/workflows/*.md`
- `/document` → Reads `.claude/lessons/workflows/documentation.md`

This ensures learned patterns are applied automatically.

## Project-Specific Lessons

Project-specific lessons stay in the project:
- Location: `projects/<project>/docs/lessons/`
- Format: Same as above
- Usage: Available when working in that project
- Not generalized to parent repo

## Lesson Lifecycle

```
1. CAPTURE → projects/<project>/docs/lessons/<spec-id>.md
              ↓
2. REVIEW   → /improve-ai scans project lessons
              ↓
3. GENERALIZE → .claude/lessons/<area>/<topic>.md
              ↓
4. DOCUMENT → docs/platforms/ or docs/patterns/ (if significant)
              ↓
5. APPLY    → Commands load and use lessons
```

## Status Values

| Status | Meaning |
|--------|---------|
| **Captured** | Lesson recorded in project, not yet reviewed |
| **Reviewed** | Assessed by /improve-ai, categorized |
| **Generalized** | Added to parent .claude/lessons/ |
| **Documented** | Promoted to official docs/ (optional) |

## When to Document vs Keep as Lesson

| Keep as Lesson | Promote to Docs |
|---------------|-----------------|
| Quick tips | Comprehensive patterns |
| Specific gotchas | Architectural guidance |
| Workarounds | Standards |
| One-liner fixes | Complete procedures |

Lessons are **lightweight and accumulative**. Docs are **authoritative and curated**.

## Manually Adding Lessons

You can manually add lessons too:

```bash
# Add to appropriate area
echo "## $(date +%Y-%m-%d) [Title]

**Context**: Manual entry
**Problem**: [description]
**Solution**: [solution]
**Generalization**: [how this applies broadly]

**Status**: Captured

---
" >> .claude/lessons/fabric/pitfalls.md
```

Then run `/improve-ai` to review and integrate.

## Searching Lessons

```bash
# Find lessons related to a topic
grep -r "rate limit" .claude/lessons/

# Find unprocessed lessons
grep -r "Status: Captured" .claude/lessons/

# Count lessons per area
find .claude/lessons -name "*.md" -not -name "README.md" -exec wc -l {} +
```

## Integration with Commands

### /sdd
- **Loads**: Platform-specific lessons on start
- **Captures**: Lessons during implementation to project
- **Triggers**: `/document` → `/improve-ai` at end

### /improve-ai
- **Reads**: Project lessons from `projects/<project>/docs/lessons/`
- **Processes**: Generalizes and adds to `.claude/lessons/`
- **Updates**: Parent docs if patterns are significant

### /document
- **Loads**: Documentation lessons
- **Uses**: To avoid known documentation mistakes

### /architect
- **Loads**: Workflow and platform lessons
- **Uses**: To inform architecture decisions
