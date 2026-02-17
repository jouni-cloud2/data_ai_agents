# Fabric Pitfalls

Lessons learned about common pitfalls when working with Microsoft Fabric.

---

## 2026-02-17 Missing `.platform` File for New Notebook/Lakehouse Artifacts

**Context**: IT domain restructure — creating new notebooks via Git (not Fabric UI)
**Problem**: After creating new notebook folders and content files in Git, Fabric Git sync did not import the artifacts. They were invisible in the workspace.
**Solution**: Every Fabric artifact must include a `.platform` file alongside its content. The `.platform` file declares the artifact type, display name, and a unique `logicalId` (UUID4). Without it, Fabric Git integration silently ignores the folder.
**Generalization**: Whenever creating any Fabric artifact in Git (Notebook, Lakehouse, DataPipeline), always create the `.platform` file first. Add a verification step after implementation: `find fabric/ -name "*.Notebook" -type d | while read d; do [ -f "$d/.platform" ] || echo "MISSING: $d"; done`
**Related**:
- Docs: `docs/platforms/fabric/pitfalls.md` (Missing .platform File section)
- Spec: SDD-20260217-it-dev-ddm-mock-data

**Status**: Generalized

---
