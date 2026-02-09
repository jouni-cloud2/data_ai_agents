# Agent Interaction Guidelines

**For all agents executing commands and workflows**

## Critical Rule: Use Interactive Questions

When asking users to make choices or provide input, **ALWAYS** format your questions to enable clickable responses. Users should be able to click on options rather than typing responses.

## ❌ Wrong: Text-Only Questions

```markdown
Options:
1. "approved" - Proceed with changes
2. "modify" - Request adjustments
3. "skip" - Discard changes

What would you like to do?
```

**Problem**: User must type "approved", "1", "modify", etc. No clickable options.

## ✅ Correct: Interactive Questions

### Format for Multiple Choice

When presenting options, structure them as a clear list that the UI can convert to clickable buttons:

```markdown
**Please select an option:**

- **Option A**: Quick Fix - Direct implementation
- **Option B**: Full SDD - Comprehensive workflow
- **Option C**: Cancel

Which option would you like?
```

**Result**: The user sees clickable buttons for each option.

### Format for Simple Yes/No

For approval/confirmation questions:

```markdown
**Approve this spec to proceed with implementation?**

- **Yes** - Proceed to implementation
- **No** - Request modifications
- **Show Details** - Display full spec first

What's your decision?
```

### Format for Lists with Context

When options need explanation:

```markdown
**Which workflow would you like to use?**

**1. Quick Fix** - Best for:
   - Typos, single-line fixes
   - Small bugs with clear solutions
   - Estimated time: 5-10 minutes

**2. Full SDD** - Best for:
   - New features or components
   - Multi-file changes
   - Estimated time: 30-60 minutes

**3. Cancel** - Stop and reassess

Please choose option 1, 2, or 3:
```

## Key Patterns

### Pattern 1: Gate/Approval Points

```markdown
## [Gate Name]

**Summary**: [Brief context of what's being approved]

**Details**:
- Key point 1
- Key point 2

**Your options:**

- **Approve** - Continue to next step
- **Request Changes** - Provide feedback
- **Show Details** - View more information

What would you like to do?
```

### Pattern 2: Selection from Multiple Items

```markdown
## Choose Items to Process

Found 5 items that need attention:

1. **Item A** - [description]
2. **Item B** - [description]
3. **Item C** - [description]
4. **Item D** - [description]
5. **Item E** - [description]

**Options:**

- **All** - Process all items
- **Select** - Choose specific items (e.g., "1,3,5")
- **None** - Skip processing

What would you like?
```

### Pattern 3: Follow-up Actions

```markdown
## Next Steps

Changes have been applied successfully.

**What would you like to do next?**

- **Commit** - Create commit and PR
- **Review** - Show me the diff first
- **Modify** - Make additional changes
- **Cancel** - Discard changes

Please select:
```

## Special Cases

### When Collecting Text Input

For fields where the user must type (like names, descriptions):

```markdown
## Required Information

I need the following information to proceed:

**1. Business Owner** (name or email):
> [User types here]

**2. Data Classification**:
- **Public** - No restrictions
- **Internal** - Internal use only
- **Confidential** - Restricted access
- **Highly Confidential** - Strictly controlled

Please provide the owner and select the classification:
```

### When Showing Progress

For actions that agents will perform:

```markdown
## Processing Lessons

I will now:

1. Review 5 captured lessons
2. Categorize as generalizable or project-specific
3. Update parent repo documentation
4. Mark lessons as processed

**Ready to proceed?**

- **Yes** - Start processing
- **Show Plan** - Let me review the details first
- **Cancel** - Stop

Your choice:
```

## Implementation Checklist

When writing commands or workflows that ask questions:

- [ ] Each decision point presents clear options
- [ ] Options are formatted as bullet lists or numbered lists
- [ ] Each option has a clear, short label (1-3 words)
- [ ] Options include brief explanations when needed
- [ ] Question ends with clear prompt ("What would you like?", "Please select:", etc.)
- [ ] Avoid free-text responses when options can be provided
- [ ] Use consistent labels ("Approve" not "approved" or "Approve this")

## Why This Matters

**User Experience**: Clicking is 10x faster than typing. Users can see all options at once and make decisions quickly.

**Error Reduction**: No typos, no guessing about valid inputs ("approve" vs "approved" vs "yes" vs "1").

**Accessibility**: Clickable options work better for all users, including those using assistive technologies.

## Examples from Commands

### /sdd Gate #1: Workflow Selection

✅ **Good**:
```markdown
## Workflow Selection

**Which workflow would you like to use?**

- **Quick Fix** - Direct implementation, minimal ceremony
- **Full SDD** - Spec authoring, comprehensive workflow

Please select:
```

❌ **Bad**:
```markdown
Which workflow would you like to use?
1. Quick Fix - Direct implementation with minimal ceremony
2. Full SDD - Spec authoring, implementation, documentation

Type "1" or "2":
```

### /improve-ai Mode Selection

✅ **Good**:
```markdown
## AI Improvement Session

**Choose mode:**

- **Review Lessons** - Process 3 captured lessons
- **Platform Patterns** - Improve platform docs
- **Commands** - Improve command workflows
- **Principles** - Update principles docs

What would you like to improve?
```

❌ **Bad**:
```markdown
Choose mode:
A. Review Lessons (Recommended - 3 lessons pending)
B. Direct Improvements
   1. Platform Patterns
   2. Principles
   3. Commands

Select: A, B, or describe what you'd like to improve:
```

## Quick Reference

| Situation | Pattern |
|-----------|---------|
| Binary choice | - **Yes** / - **No** |
| Multiple options | - **Option 1** / - **Option 2** / - **Option 3** |
| Approval gates | - **Approve** / - **Request Changes** / - **Show Details** |
| List selection | - **All** / - **Select [specify]** / - **None** |
| Workflow steps | - **Continue** / - **Review** / - **Cancel** |

---

**Remember**: If a user could click it, they should be able to click it. Always prefer interactive options over free-text input.
