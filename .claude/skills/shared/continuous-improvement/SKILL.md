---
name: continuous-improvement
description: Patterns for learning from implementations and improving the system.
---

# Continuous Improvement Skill

## Learning Framework

### When to Learn
- After each PR is created
- After production incidents
- After performance issues
- After requirement ambiguities

### What to Learn

#### 1. Architecture Learnings
- Design decisions that worked well
- Design decisions that caused issues
- Platform-specific patterns discovered
- Scaling considerations

#### 2. Code Quality Learnings
- Common bugs and their fixes
- Best practices confirmed in production
- Anti-patterns discovered
- Code review feedback

#### 3. Performance Learnings
- Optimization techniques that worked
- Bottlenecks discovered
- Resource usage patterns
- Query performance insights

#### 4. Testing Learnings
- Test coverage gaps found
- Validation techniques that caught issues
- Edge cases discovered
- Integration test patterns

#### 5. Process Learnings
- Requirement ambiguities encountered
- Communication improvements needed
- Workflow optimizations
- Time estimation accuracy

## Learning Extraction Process

### Step 1: Review Work
```python
def extract_learnings(story_id):
    """Extract learnings from completed story."""
    learnings = {
        "commits": analyze_commits(story_id),
        "bugs": analyze_bugs(story_id),
        "tests": analyze_test_results(story_id),
        "performance": analyze_performance(story_id),
        "questions": analyze_clarifications(story_id)
    }
    return categorize_learnings(learnings)
```

### Step 2: Categorize
```python
def categorize_learnings(learnings):
    """Categorize learnings by type and severity."""
    categories = {
        "critical": [],      # Must update agents/skills
        "important": [],     # Should update agents/skills
        "nice_to_have": [],  # Consider for future
        "team_specific": []  # Document but don't automate
    }

    for learning in learnings:
        if learning["recurrence_risk"] > 0.5:
            categories["critical"].append(learning)
        elif learning["time_impact"] > 15:  # minutes
            categories["important"].append(learning)
        else:
            categories["nice_to_have"].append(learning)

    return categories
```

### Step 3: Generate Updates
```python
def generate_updates(categorized_learnings):
    """Generate agent/skill updates from learnings."""
    updates = []

    for learning in categorized_learnings["critical"]:
        updates.append({
            "target": learning["relevant_agent"],
            "section": learning["section"],
            "content": format_learning(learning),
            "type": "add" if learning["is_new"] else "update"
        })

    return updates
```

## Update Templates

### Agent Update - Common Mistakes
```markdown
## Common Mistakes to Avoid

[EXISTING CONTENT]

[NEW - added YYYY-MM-DD from [Story Name]]
- DON'T [mistake made]
- DO [correct approach]
- Reason: [why this matters]
```

### Agent Update - Lessons Learned
```markdown
## Lessons Learned

[EXISTING CONTENT]

### [YYYY-MM-DD]: [Story Name]
**Platform**: [Fabric/Databricks]
**Issue**: [What happened]
**Solution**: [How it was fixed]
**Prevention**: [How to avoid next time]
```

### Skill Update - Best Practices
```markdown
## Best Practices

[EXISTING CONTENT]

### [Topic] (added YYYY-MM-DD)
[Description of practice]

**When to use:**
- [Scenario 1]
- [Scenario 2]

**Example:**
```code
[Code example]
```
```

### CLAUDE.md Update
```markdown
## Recent Learnings

### YYYY-MM-DD: [Story Name]

**Platform**: [Fabric/Databricks]
**Story**: [Brief description]

**What Went Well:**
- [Success 1]
- [Success 2]

**Mistakes Made:**
- [Mistake 1] -> [Fix]
- [Mistake 2] -> [Fix]

**Key Learnings:**
- [Learning 1]
- [Learning 2]

**Templates Created:**
- [Template name] - [Description]

**Time Savings Next Time:**
- Est. [X] min saved with [improvement]
```

## Template Creation

### When to Create Templates
- Pattern used more than once
- Complex implementation
- Error-prone code
- Reusable across stories

### Template Structure
```python
"""
Template: [name]
Created: YYYY-MM-DD
Story: [Original story]
Platform: [Fabric/Databricks/Both]

Purpose:
[What this template does]

Usage:
[How to use this template]

Parameters:
- param1: [Description]
- param2: [Description]
"""

# Implementation
def template_function(param1, param2):
    """
    [Docstring]
    """
    # Code here
    pass
```

## Metrics Tracking

### Track These Metrics
```python
metrics = {
    "time_to_pr": {
        "description": "Time from story start to PR",
        "target": 90,  # minutes
        "unit": "minutes"
    },
    "test_pass_rate": {
        "description": "First-run test pass rate",
        "target": 0.9,
        "unit": "percentage"
    },
    "rework_rate": {
        "description": "Stories requiring rework",
        "target": 0.1,
        "unit": "percentage"
    },
    "learning_count": {
        "description": "Learnings captured per story",
        "target": 3,
        "unit": "count"
    }
}
```

### Trend Analysis
```python
def analyze_trends(metrics_history):
    """Analyze learning effectiveness over time."""
    trends = {}

    for metric_name, values in metrics_history.items():
        trend = calculate_trend(values)
        trends[metric_name] = {
            "direction": "improving" if trend < 0 else "declining",
            "rate": abs(trend),
            "action_needed": trend > 0
        }

    return trends
```

## Improvement Workflow

### 1. After PR Creation
```
1. Ask user: "Update agents with learnings? (yes/no)"
2. If yes:
   a. Analyze work
   b. Extract learnings
   c. Generate updates
   d. Apply updates
   e. Commit changes
   f. Report to user
3. If no:
   a. Skip updates
   b. Note for later
```

### 2. Periodic Review
```
Weekly:
1. Review all learnings from week
2. Identify patterns across stories
3. Propose systemic improvements
4. Update shared documentation

Monthly:
1. Analyze metrics trends
2. Review template usage
3. Identify training needs
4. Plan major improvements
```

## Commit Format for Learnings

```bash
git commit -m "learn(scope): brief description

Changes:
- Updated [agent]: [change]
- Added [template]: [description]
- Updated CLAUDE.md: [section]

From story: [story name]
Prevents: [issue prevented]
Saves: ~[X] min next time"
```

## Best Practices

- Capture learnings immediately
- Be specific about context
- Include code examples
- Link to original story
- Measure improvement over time

## Anti-Patterns

- Don't skip learning step
- Don't make vague updates
- Don't update without examples
- Don't forget to commit learnings
